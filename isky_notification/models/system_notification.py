# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields, models, api


class SystemNotification(models.Model):
    _name = 'system.notification'
    _description = 'System Notification'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    state = fields.Selection([('draft', 'Draft'), ('running', 'Running'), ('canceled', 'Canceled')], "Status",
                             default='draft')
    shifting_days = fields.Integer(string="Shifting Days")
    line_ids = fields.One2many('notification.line', 'notification_id')

    def run_notification(self):
        for rec in self:
            rec.state = 'running'

    def cancel_notification(self):
        for rec in self:
            rec.state = 'canceled'

    @api.model
    def send_notification(self):
        obj_has_notification_list = []
        for rec in self.env['system.notification'].search([('state', '=', 'running')]):
            for line in rec.line_ids:
                model_name = line.model_id.model
                field_name = line.field_id.name
                field_type = line.field_id.ttype
                records = False
                partners = []
                if line.notification_type == 'user':
                    for user in line.notification_user_ids:
                        if user.partner_id.id not in partners:
                            partners.append(user.partner_id.id)

                if line.notification_type == 'group':
                    users = self.env['res.users'].sudo().search([])
                    for user in users:
                        for group in line.notification_group_ids:
                            if user.id in group.users.ids and user.partner_id.id not in partners:
                                partners.append(user.partner_id.id)

                for res in self.env[model_name].search([]):
                    res_date = getattr(res, field_name)

                    if res_date:
                        if field_type == 'date':
                            res_date = fields.Date.from_string(res_date)
                        else:
                            res_date = fields.Datetime.from_string(res_date).date()
                        notification_date = res_date + timedelta(days=rec.shifting_days)
                        today = fields.Date.from_string(fields.Date.today())

                        if notification_date == today:
                            records = True
                            obj_has_notification_list.append(res)
                            if line.notification_type == 'other':
                                for user in line.receipt_ids:
                                    receipt = getattr(res, user.name)
                                    if receipt:
                                        if user.relation == 'res.users' and receipt.partner_id and receipt.partner_id.id not in partners:
                                            partners.append(receipt.partner_id.id)

                                        elif user.relation == 'hr.employee' and receipt.user_id and receipt.user_id.partner_id and receipt.user_id.partner_id.id not in partners:
                                            partners.append(receipt.user_id.partner_id.id)

                                        elif user.relation == 'res.partner' and receipt.id not in partners:
                                            partners.append(receipt.id)

                if len(partners) > 0 and records and obj_has_notification_list:
                    for obj_has_notification in obj_has_notification_list:
                        post_vars = {
                            'subject': 'This is a notification For ' + obj_has_notification.name + " " + line.field_id.field_description,
                            'body': 'This is a notification For ' + '<a href="/web#id=' + str(
                                obj_has_notification.id) + '&view_type=form&model=' + str(
                                line.model_id.model) + '&menu_id=">' + obj_has_notification.name + '</a>' + " " + line.field_id.field_description,
                            'partner_ids': partners
                        }
                        rec.message_post(message_type='comment', subtype_xmlid='mail.mt_note', **post_vars)
