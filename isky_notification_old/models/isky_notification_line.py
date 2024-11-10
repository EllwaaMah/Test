# -*- coding: utf-8 -*-

from odoo import fields, models, api


class NotificationLine(models.Model):
    _name = 'notification.line'
    _description = 'Notification Line'

    model_id = fields.Many2one('ir.model', string='Model')
    field_id = fields.Many2one('ir.model.fields', string='Fields')
    notification_type = fields.Selection([('user', 'Users'), ('group', 'Groups'), ('other', 'Other')],string= "Notification For")
    notification_user_ids = fields.Many2many('res.users', string="Users")
    notification_group_ids = fields.Many2many('res.groups', string="Groups")
    notification_id = fields.Many2one('isky.notification', string="Notification")
    receipt_ids = fields.Many2many('ir.model.fields', string="Receipts")

    @api.onchange('notification_type')
    def _onchange_notification(self):
        for rec in self:
            rec.notification_user_ids = []
            rec.notification_group_ids = []
