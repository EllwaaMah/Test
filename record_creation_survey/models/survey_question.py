from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class SurveyQuestion(models.Model):
    _inherit = "survey.question"

    field_id = fields.Many2one(string="Field", comodel_name="ir.model.fields", domain=[])
    model_id = fields.Many2one(comodel_name="ir.model")
    record_creation_question_id = fields.Many2one(comodel_name='survey.question')
    child_question_ids = fields.One2many(comodel_name='survey.question', inverse_name='record_creation_question_id')
    created_record_id = fields.Integer()

    link_to_central_partner = fields.Boolean(string="Mark as family member and link survey respondee")
    survey_can_create_records = fields.Boolean(related='survey_id.can_create_records')
    can_create_records = fields.Boolean()
    model_name = fields.Char(related="model_id.model")

    @api.constrains('question_type','field_id')
    def _check_question_type_field_id(self):
        field_type_question_type_dict = {
            'char': ('char_box','Single Line Text Box'),
            'text': ('text_box', 'Multiple Lines Text Box'),
            'integer': ('numerical_box','Numerical Value'),
            'float': ('numerical_box','Numerical Value'),
            'date': ('date','Date'),
            'datetime': ('datetime','Datetime'),
            'boolean': ('simple_choice','Multiple choice: only one answer')
        }
        
        for record in self:
            if record.can_create_records and record.field_id:
                if record.field_id.ttype not in field_type_question_type_dict.keys():
                    raise ValidationError(_('Issue with Question \"%s\": Record creation supported only for fields of type char, text, integer, float, date, datetime and boolean.',record.title))
                
                expected_question_type = field_type_question_type_dict[record.field_id.ttype]

                if record.question_type and record.question_type != expected_question_type[0]:
                    raise ValidationError(_('Question \"%s\" linked to field \"%s\" of model \"%s\" should be of type %s to create records',record.title, record.field_id.name, record.model_id.name, expected_question_type[1]))
    
    @api.constrains('can_create_records','model_id','record_creation_question_id','child_question_ids')
    def _check_question_record_creation_model(self):
        for record in self.filtered(lambda r: r.can_create_records):
            validation_err = []
            if record.record_creation_question_id:
                if record.id == record.record_creation_question_id.id:
                    validation_err.append(_('Issue in Question \"%s\": Cannot set record creation question as the same question itself', record.title))
                if not record.record_creation_question_id.can_create_records:
                    validation_err.append(_('Issue in Question \"%s\": Question set as record creation question not marked as \"can create records\"', record.title))
                if record.model_id.id != record.record_creation_question_id.model_id.id:
                    validation_err.append(_('Model set on question \"%s\" must match model of Record Creation Question linked \"%s\"',record.title, record.record_creation_question_id.title))
            if record.child_question_ids:
                validation_err.append(_('Cannot disable record creation in question \"%s\" while other questions have set it as record creation question', record.title))
            # added this for user friendly error, so the user can see all the errors at once. -AKR
            if bool(validation_err):
                raise ValidationError(','.join(validation_err))

                                