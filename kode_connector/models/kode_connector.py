# -*- coding: utf-8 -*-
# © 2021 DGTera systems (<http://www.dgtera.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import hmac
import json
import hashlib
import requests
import psycopg2
from odoo import models, fields, api, registry, SUPERUSER_ID, _


class KodeConnector(models.Model):
    _name = "kode.connector"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Kode Connector"

    name = fields.Char(required=True, tracking=True)
    is_testing = fields.Boolean(tracking=True)
    url = fields.Char(compute='_compute_url')
    test_url = fields.Char(tracking=True)
    production_url = fields.Char(tracking=True)
    access_token = fields.Char()
    state = fields.Selection(
        string="status", selection=[
            ('draft', 'Draft'), ('connect', 'Connect'), ('error', 'Error')
        ], default='draft'
    )
    connect_message = fields.Text(tracking=True)
    log_type = fields.Selection(
        selection=[
            ('nothing', 'Nothing'), ('all', 'All'), ('error', 'Error')
        ], default='nothing'
    )
    log_count = fields.Integer(compute='_compute_log_count')
    field_ids = fields.Many2many(
        'ir.model.fields', string='Matched Fields'
    )

    def _compute_log_count(self):
        domain = [('name', '=ilike', f'{self._name},%')]
        log_data = self.env['ir.logging'].read_group(domain, ['name'], ['name'])
        log_data = dict(
            (int(d['name'].replace(f'{self._name},', '')), d['name_count'])
            for d in log_data
        )
        for rec in self:
            rec.log_count = log_data.get(rec.id, 0)

    @api.depends('production_url', 'test_url', 'is_testing')
    def _compute_url(self):
        for rec in self:
            rec.url = rec._get_url()

    def _get_kode_instance(self):
        return self.search([('state', '=', 'connect')], limit=1)

    def _get_url(self):
        return self.production_url if not self.is_testing else self.test_url

    def test_connection(self):
        partner_id = self.env['res.partner'].search([], limit=1).id
        res = self._send_request_signal(data={'id': str(partner_id)})
        if not res or res.get('error'):
            state = 'error'
            msg = """Test connection Un-successful, (%s) """ % res['error']
        else:
            state = 'connect'
            msg = "Congratulation, It's Successfully Connected with Kode."
        return self.write({'connect_message': msg, 'state': state})

    def _fetch_kode_headers(self, data):
        key = (self.access_token or '').encode("utf-8")
        hexdigest = hmac.new(key, data, digestmod=hashlib.sha256).hexdigest()
        return {
            "Signature": hexdigest,
            "Action": "user/update",
            "Connection": "keep-alive",


            'Content-Type': 'application/json',

        }

    def _send_request_signal(self, request_type='POST', data=None):
        error = False
        try:
            data = data or {}
            json_dump = json.dumps(data).encode("utf-8")
            headers = self._fetch_kode_headers(json_dump)
            data = data or {}
            json_dump = json.dumps(data).encode("utf-8")
            headers = self._fetch_kode_headers(json_dump)
        # try:
        #     response = requests.request(
        #         request_type, self._get_url(), data=json_dump,
        #         headers=headers
        #     )
        #     if response.text:
        #         response = json.loads(str(response.text))
        except Exception as e:
            error = True
            response = {'error': e}
        if self.log_type == 'all' or (self.log_type == 'error' and error):
            self.log(response, self._get_url(), 'user/update', error)
            msg = {'headers': headers, 'body': json_dump, 'response': response}
            self.log(
                msg, self._get_url(),
                'user/update', error
            )
        return response

    def log(self, message, path, func, error=False):
        self.flush()
        db_name = self._cr.dbname
        # Use a new cursor to avoid rollback that could be
        # caused by an upper method
        try:
            db_registry = registry(db_name)
            with db_registry.cursor() as cr:
                lvl = 'ERROR' if error else 'DEBUG'
                env = api.Environment(cr, SUPERUSER_ID, {})
                IrLogging = env['ir.logging']
                IrLogging.sudo().create({
                    'name': f'kode.connector,{self.id}', 'type': 'server',
                    'dbname': db_name, 'level': lvl, 'message': message,
                    'path': path, 'func': func, 'line': 1
                })
        except psycopg2.Error:
            pass

    def action_view_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Logs'),
            'res_model': 'ir.logging',
            'view_mode': 'tree,form',
            'domain': [('name', '=', f'{self._name},{self.id}')],
        }
