from odoo import api, fields, models, _
from odoo.exceptions import UserError



class SendSurveyWizard(models.TransientModel):
    _name = "send.survey.applicant"

    survey_id = fields.Many2one('survey.survey', string="Survey")
    applicant_id = fields.Many2one('hr.applicant', string="applicant")
    survey_ids = fields.Many2many('survey.survey', string="Apply Survey", related='applicant_id.survey_id')


    def action_send_information_form_applicant(self):
        self.ensure_one()
        survey_id = self.survey_id
        if not survey_id:
            raise UserError(_('No survey set on Application'))
        if not self.applicant_id.partner_id:
            if not self.applicant_id.partner_name:
                raise UserError(_('You must define a Contact Name for this applicant.'))
            self.applicant_id.partner_id = self.env['res.partner'].create({
                'is_company': False,
                'type': 'private',
                'name': self.applicant_id.partner_name,
                'email': self.applicant_id.email_from,
                'phone': self.applicant_id.partner_phone,
                'mobile': self.applicant_id.partner_mobile
            })
        followers = self.applicant_id.message_follower_ids.filtered(
            lambda fol: fol.partner_id != self.env.user.partner_id).mapped(
            'partner_id')
        partners = [l.id for l in followers]
        partners.append(self.applicant_id.partner_id.id)


        values = self.survey_id.with_context(default_partner_ids=partners,
                                           default_emails=self.applicant_id.email_from,
                                           # active_model='hr.applicant',
                                           active_id=self.applicant_id.id).action_send_survey()
        values['context']['default_template_id'] = self.survey_id.template_id.id
        values['context']['default_body'] = self.survey_id.template_id.body_html
        self.applicant_id.chosen_survey_id = self.survey_id
        return values

        # survey_invite_action = survey_id.action_send_survey()
        # context = survey_invite_action.get('context', {})
        # followers = self.applicant_id.message_follower_ids.filtered(lambda fol: fol.partner_id != self.env.user.partner_id).mapped(
        #     'partner_id')
        #
        # context.update({
        #     'default_partner_ids': followers.ids,
        #     'default_emails': self.applicant_id.email_from
        # })
        # survey_invite_action['context'] = context
        #
        # return survey_invite_action
