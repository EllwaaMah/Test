from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    survey_id = fields.Many2one(
        string="Survey", comodel_name="survey.survey", domain=[("can_create_records", "=", True)]
    )

    is_information_form_stage = fields.Boolean(compute="_compute_is_information_form_stage")

    @api.depends('stage_id', 'company_id.send_information_form_stage_id')
    def _compute_is_information_form_stage(self):
        for record in self:
            record.is_information_form_stage = record.stage_id.id == record.company_id.send_information_form_stage_id.id

    def action_send_information_form(self):
        self.ensure_one()
        survey_id = self.survey_id
        if not survey_id:
            raise UserError(_('No survey set on CRM'))
        survey_invite_action = survey_id.action_send_survey()
        context = survey_invite_action.get('context', {})
        context.update({
            'default_partner_ids': [self.partner_id.id]
        })
        survey_invite_action['context'] = context

        return survey_invite_action

    def action_send_information_form_bulk(self):
        print('self', self)
        firts_survey = self[0].survey_id
        if all(record.survey_id == firts_survey for record in self):
            survey_id = firts_survey
        else:
            raise UserError("Can't combine between different Surveys")

        if not survey_id:
            raise UserError(_('No survey set on CRM'))
        if all(record.stage_id == self.env.ref('crm.stage_lead3') for record in self):
            survey_invite_action = survey_id.action_send_survey()
            context = survey_invite_action.get('context', {})
            partner_ids = []
            for rec in self:
                partner_ids.append(rec.partner_id.id)
            context.update({
                'default_partner_ids': [(6, 0, partner_ids)]
            })
            survey_invite_action['context'] = context

            return survey_invite_action

        else:
            raise UserError(_('You should select Leads with stage %s only.') % (self.env.ref('crm.stage_lead3').name,))
