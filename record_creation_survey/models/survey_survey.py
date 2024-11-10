from odoo.exceptions import UserError
import re
from odoo import api, fields, models, tools, _

emails_split = re.compile(r"[;,\n\r]+")


class Survey(models.Model):
    _inherit = "survey.survey"

    can_create_records = fields.Boolean(string="Can create records")


class SurveyInvite(models.TransientModel):
    _inherit = "survey.invite"

    def action_invite(self):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed """
        self.ensure_one()
        Partner = self.env['res.partner']
        print("self._context.get('active_ids')", self._context.get('active_ids'))
        # compute partners and emails, try to find partners for given emails
        valid_partners = self.partner_ids
        valid_emails = []
        print('self.emails', self.emails)
        for email in emails_split.split(self.emails or ''):
            partner = False
            email_normalized = tools.email_normalize(email)
            if email_normalized:
                limit = None if self.survey_users_login_required else 1
                partner = Partner.search([('email_normalized', '=', email_normalized)], limit=limit)
            if partner:
                valid_partners |= partner
            else:
                email_formatted = tools.email_split_and_format(email)
                if email_formatted:
                    valid_emails.extend(email_formatted)

        if not valid_partners and not valid_emails:
            raise UserError(_("Please enter at least one valid recipient."))

        answers = self._prepare_answers(valid_partners, valid_emails)
        for answer in answers:
            print('answer', answer)
            self._send_mail(answer)
            print('yrtest')
        for rec in self._context.get('active_ids'):
            if (self._context.get("active_model")
                    and self._context.get("active_model") == "crm.lead"):
                lead_id = self.env['crm.lead'].browse(rec)
                if lead_id:
                    followers = lead_id.message_follower_ids.filtered(
                        lambda fol: fol.partner_id != self.env.user.partner_id).mapped(
                        'partner_id')
                    print(followers)
                    print(followers.ids)
                    print(self.body)
                    print(self.subject)

                    mail_message = self.env['mail.message'].sudo().create({
                        'author_id': self.env.user.partner_id.id,
                        'body': self.body,
                        'email_from': self.env.user.partner_id.email_formatted,
                        'is_internal': False,
                        'message_id': tools.generate_tracking_message_id('dummy-generate'),
                        'message_type': 'comment',
                        'model': 'crm.lead',
                        # 'record_name': self.name,
                        'res_id': lead_id.id,
                        # 'reply_to': self.company_id.name,
                        'subtype_id': self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment'),
                        'subject': 'Re: %s' % lead_id.name,
                        'partner_ids': followers,
                        # 'notified_partner_ids': [6, 0, followers.ids],

                    })
        return {'type': 'ir.actions.act_window_close'}
