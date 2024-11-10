# -*- coding: utf-8 -*-

import base64
import datetime
import email
import hashlib
import lxml
import pytz
import re
import socket
import time
import threading

try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

from collections import namedtuple
from email.message import Message
from werkzeug.urls import url_encode
from werkzeug import urls

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.osv import expression

from odoo.tools.safe_eval import safe_eval


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_record_by_email(self, message, recipients_data, msg_vals=False,
                                model_description=False, mail_auto_delete=True, check_existing=False,
                                force_send=True, send_after_commit=True,
                                **kwargs):
        """ Method to send email linked to notified messages."""
        res = super(MailThread, self)._notify_record_by_email(message, recipients_data, msg_vals=False,
                                                              model_description=False, mail_auto_delete=True,
                                                              check_existing=False,
                                                              force_send=True, send_after_commit=True,
                                                              **kwargs)
        # create notification in case of email
        channel_ids =  []
        inbox_pids = []
        for data in recipients_data:
            print("recipients_data['channels']",recipients_data)
            if data.get('channels'):
                channel_ids = [int(r['id']) for r in data['channels']]
                if channel_ids:
                    message.write({'channel_ids': [(6, 0, channel_ids)]})
            if data.get('partners'):
                inbox_pids = [int(r['id']) for r in data['partners']]
                if inbox_pids:
                    notif_create_values = [{
                        'mail_message_id': message.id,
                        'res_partner_id': pid,
                        'notification_type': 'inbox',
                        'notification_status': 'sent',
                    } for pid in inbox_pids]
                    objj = self.env['mail.notification'].sudo().create(notif_create_values)

            bus_notifications = []
            if inbox_pids or channel_ids:
                message_format_values = False
                if inbox_pids:
                    message_format_values = message.message_format()[0]
                    for partner_id in inbox_pids:
                        bus_notifications.append(
                            [(self._cr.dbname, 'ir.needaction', partner_id), dict(message_format_values)])
                if channel_ids:
                    bus_notifications += self.env['mail.channel'].sudo().browse(channel_ids)._channel_message_notifications(
                        message, message_format_values)
            if bus_notifications:
                self.env['bus.bus'].sudo().sendmany(bus_notifications)
        return res
