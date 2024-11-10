try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

from odoo import api, fields, models, tools, SUPERUSER_ID


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
        # channel_ids = [r['id'] for r in recipients_data['channels']]
        # if channel_ids:
        #     message.write({'channel_ids': [(6, 0, channel_ids)]})
        inbox_pids = [r['id'] for r in recipients_data]
        bus_notifications = []
        if inbox_pids:
            notif_create_values = [{
                'mail_message_id': message.id,
                'res_partner_id': pid,
                'notification_type': 'inbox',
                'notification_status': 'sent',
            } for pid in inbox_pids]
            self.env['mail.notification'].sudo().create(notif_create_values)
            message_format_values = message.message_format()[0]
            for partner_id in inbox_pids:
                bus_notifications.append(
                    (self.env['res.partner'].browse(partner_id), 'mail.message/inbox', dict(message_format_values)))
        self.env['bus.bus'].sudo()._sendmany(bus_notifications)
        return res
