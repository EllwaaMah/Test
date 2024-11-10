# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from dateutil.relativedelta import relativedelta


class BatchPdcPayment(models.Model):
    _name = "batch.pdc.payment"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', default='New')
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, copy=False)
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked')], readonly=True, default='draft', copy=False,
                             string="Status")
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', 'in', ['bank'])])
    deposit_journal_id = fields.Many2one('account.journal', string='Bank Journal', required=True,
                                         domain=[('type', 'in', ['bank'])])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    communication = fields.Char(string='Memo')
    cheques_no = fields.Integer(string="Total No of Cheques", default="1")
    no_of_months = fields.Integer(string="No of months", default="1")
    first_cheque_date = fields.Date(string='First Cheque Date', default=fields.Date.context_today)
    first_cheque_ref = fields.Integer('First Cheque Ref')

    agent = fields.Char('Agent')
    bank = fields.Many2one('res.bank', string="Bank")
    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')], default='inbound',
                                    string='Payment Type', required=True)
    line_ids = fields.One2many('sr.pdc.payment', 'batch_id')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('batch.pdc.payment')
        return super(BatchPdcPayment, self).create(vals)

    def lock(self):
        self.state = 'lock'

    @api.ondelete(at_uninstall=False)
    def _unlink_except_done(self):
        if 'lock' in self.mapped('state'):
            raise UserError(_('You cannot delete a Batch PDC which is Locked.'))

    def generate_cheques(self):
        for rec in self:
            if rec.line_ids:
                for line in rec.line_ids:
                    rec.line_ids = [(2, line.id)]
            for n in range(0, rec.cheques_no):
                pdc_line = self.env["sr.pdc.payment"].sudo().create(
                    {
                        "amount": rec.amount / rec.cheques_no,
                        "batch_id": rec.id,
                        "journal_id": rec.journal_id.id,
                        "deposit_journal_id": rec.deposit_journal_id.id,
                        "payment_type": rec.payment_type,
                        "agent": rec.agent,
                        "partner_id": rec.partner_id.id,
                        "bank": rec.bank.id,
                        "due_date": rec.first_cheque_date + relativedelta(months=n * rec.no_of_months),
                        "cheque_ref": rec.first_cheque_ref + n,
                        "communication": rec.communication,
                    }
                )
                pdc_line.register()

    @api.onchange('journal_id')
    def _default_currency(self):
        if self.journal_id:
            journal = self.journal_id
            currency_id = journal.currency_id or journal.company_id.currency_id or self.env.user.company_id.currency_id
            self.currency_id = currency_id.id
        else:
            self.currency_id = False
