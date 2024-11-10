from odoo import _, api, fields, models
from odoo.exceptions import UserError

class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    def _mark_done(self):
        super(SurveyUserInput, self)._mark_done()
        for user_input in self:
            field_value = ''
            for user_input_line in user_input.user_input_line_ids\
                    .filtered(lambda r: r.question_id.can_create_records):           
                model_id = user_input_line.question_id.model_id
                #Type of field is already ensured to match question_type/answer_type via check in action_open of survey and python constraint in survey_question
                if user_input_line.question_id.field_id.ttype == 'boolean' and user_input_line.answer_type == 'suggestion':
                    field_value = user_input_line.suggested_answer_id.value.lower()
                    field_value = field_value == 'true' or field_value == 'yes' or field_value == '1'
                else: 
                    field_value = user_input_line['value_%s' % user_input_line.answer_type]
                vals = {
                    user_input_line.question_id.field_id.name: field_value
                }
                if user_input_line.question_id.record_creation_question_id:
                    created_record_id = user_input_line.question_id.record_creation_question_id.created_record_id
                    created_record = self.env[model_id.model].browse(created_record_id)
                    created_record.write(vals)
                else:
                    created_record = self.env[model_id.model].create(vals)
                    user_input_line.question_id.created_record_id = created_record.id
                    if model_id.model == 'res.partner' and user_input_line.question_id.link_to_central_partner and user_input.partner_id:
                        created_record.write({
                            'membership_type': 'member',
                            'central_partner_id': user_input.partner_id.id
                        })
                        