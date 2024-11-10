import werkzeug
from odoo import api, fields, models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    applicant_id = fields.Many2one("hr.applicant")

    def get_start_url(self):
        self.ensure_one()
        if self.env.context:
            if 'active_model' in self.env.context:
                if self.env.context['active_model'] == 'hr.applicant':
                    applicant_id = self.env['hr.applicant'].browse(self.env.context['active_id'])
                    return '%s' % (applicant_id.get_start_url())
        return '%s?answer_token=%s' % (self.survey_id.get_start_url(), self.access_token)


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    is_recruitment = fields.Boolean(string="Recruitment")
    template_id = fields.Many2one('mail.template', 'Default template',
                                  domain="['|', ('model', '=', 'hr.applicant'), ('model', '=', 'survey.user_input')]")


class SurveyInvite(models.TransientModel):
    _inherit = "survey.invite"

    applicant_id = fields.Many2one('hr.applicant', string='Applicant')

    @api.depends('survey_id.access_token')
    def _compute_survey_start_url(self):
        for invite in self:
            if invite.applicant_id:
                invite.survey_start_url = werkzeug.urls.url_join(invite.applicant_id.get_base_url(),
                                                                 invite.applicant_id.get_start_url()) if invite.applicant_id else False
            else:
                invite.survey_start_url = werkzeug.urls.url_join(invite.survey_id.get_base_url(),
                                                                 invite.survey_id.get_start_url()) if invite.survey_id else False

    # Overrides of mail.composer.mixin
    # @api.depends('survey_id')  # fake trigger otherwise not computed in new mode
    # def _compute_render_model(self):
    #     if self.applicant_id:
    #         self.render_model = 'hr.applicant'
    #
    #     else:
    #         self.render_model = 'survey.user_input'
