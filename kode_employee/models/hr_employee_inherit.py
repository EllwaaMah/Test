import uuid

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, exceptions, _

from datetime import date, datetime, timedelta

from odoo.exceptions import UserError


class HrEmployeeCertificate(models.Model):
    _name = 'hr.employee.certificate'

    name = fields.Char(string="Name", required=1)


class FamilyInformation(models.Model):
    _name = 'family.information'

    name = fields.Char(string="Name", required=1)
    type = fields.Selection(selection=[('child', 'Children'), ('spouses', 'Spouses')], string="Type",
                            default='child', required=1)
    birthday = fields.Date(string="Birthday")
    medical_insurance_num = fields.Char(string="Medical Insurance ID")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string="Gender",
                              default='male')
    employee_id = fields.Many2one('hr.employee', string='employee')


class PositionGrade(models.Model):
    _name = 'position.grade'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    percentile_1 = fields.Char(string="Percentile 1")
    percentile_2 = fields.Char(string="Percentile 2")
    percentile_3 = fields.Char(string="Percentile 3")
    percentile_4 = fields.Char(string="Percentile 4")
    percentile_5 = fields.Char(string="Percentile 5")


class DisabilityType(models.Model):
    _name = 'disability.type'

    name = fields.Char(string="Name")


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    hr_business_partner_id = fields.Many2one('res.users', string="HR business Partner", required=True)
    hr_business_partner_ids = fields.Many2many('res.users', string="HR business Partner", compute="get_employee_users")
    manager_id = fields.Many2one('hr.employee', string='Manager', tracking=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 required=True)

    @api.depends('name')
    def get_employee_users(self):
        users = self.env['res.users'].search(
            [('groups_id', 'in', [self.env.ref('hr.group_hr_user').id])])
        self.hr_business_partner_ids = [(6, 0, users.ids)]


class AssessmentName(models.Model):
    _name = 'assessment.name'

    name = fields.Char(string="Name", required=1)


class HrJob(models.Model):
    _inherit = 'hr.job'

    position_grade_id = fields.Many2one('position.grade', string=" Position Grade")
    survey_ids = fields.Many2many('survey.survey', string="Apply Survey")

    hr_users_ids = fields.Many2many('res.users', string="HR  users", compute="get_employee_users")
    department_id = fields.Many2one('hr.department', string='Department', required=True,
                                    domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    def get_employee_users(self):
        users = self.env['res.users'].search(
            [('groups_id', 'in', [self.env.ref('hr.group_hr_user').id])])

        self.hr_users_ids = [(6, 0, users.ids)]


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    emp_type = fields.Selection(selection=[('internal', 'Kode Contract'), ('external', 'Outsourced')],
                                string="Employee Type", default='internal', required=1)

    employee_card_id = fields.Char(string="Employee ID")
    arabic_name = fields.Char(string="Name Arabic")
    gifted = fields.Boolean(string="Gifted")
    disability_type_id = fields.Many2one('disability.type', string="Disability Type")

    disability_desc = fields.Char(string="Disability Description")

    position_grade_id = fields.Many2one('position.grade', string="Position Grade", related='job_id.position_grade_id')

    len_years_service_in_company = fields.Float(string="Length of service inside the company (Years)",
                                                compute='_compute_len_service_in_company')
    previous_insured_years = fields.Float(string="Previous insured years")
    total_insured_years = fields.Integer(string="Total insured (Years)", compute='_compute_len_service_in_company')

    required_license1 = fields.Char(string="Required License 1")
    required_license2 = fields.Char(string="Required License 2")
    social_insurance_num = fields.Char(string="Social Insurance Number")
    medical_insurance_num = fields.Char(string="Medical Insurance Number")
    emergency_relation = fields.Char(string="Emergency relation")
    age = fields.Char(string="Age", compute="get_age")
    address_home_per_id = fields.Many2one(
        'res.partner', 'Address as per National ID',
        help='Enter here the private address of the employee, not the one linked to your company.',
        groups="hr.group_hr_user", tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    family_info_ids = fields.One2many('family.information', 'employee_id', string="Family")
    total_children = fields.Integer(string="Total Children", compute="get_total_children")
    certificate_id = fields.Many2one('hr.employee.certificate', string="Certificate Level", required=True)
    # selection_add
    employee_type = fields.Selection(selection_add=[('partime', 'Part-Time'), ('consultant', 'Consultant')],
                                     ondelete={'partime': 'set default', 'consultant': 'set default'})

    @api.depends('family_info_ids', 'family_info_ids.type')
    def get_total_children(self):
        for rec in self:
            count = 0
            for line in rec.family_info_ids:
                if line.type == 'child':
                    count += 1

            rec.total_children = count

    @api.depends('birthday')
    def get_age(self):
        for rec in self:
            age = 0
            if rec.birthday:
                today = date.today()

                age = today.year - rec.birthday.year - (
                        (today.month, today.day) < (rec.birthday.month, rec.birthday.day))
            rec.age = age

    @api.depends('first_contract_date', 'contract_id', 'previous_insured_years')
    def _compute_len_service_in_company(self):
        for rec in self:
            len_years_service_in_company = 0
            today = date.today()
            if rec.contract_id.state == 'open':
                if rec.first_contract_date:
                    len_years_service_in_company = ((
                                                            date.today().year - rec.first_contract_date.year) * 12 + today.month - rec.first_contract_date.month) / 12
            else:
                date_end = rec.contract_id.date_end
                if rec.contract_id.date_end and date_end:
                    len_years_service_in_company = ((
                                                            date_end.year - rec.first_contract_date.year) * 12 + date_end.month - rec.first_contract_date.month) / 12

            rec.len_years_service_in_company = len_years_service_in_company
            rec.total_insured_years = len_years_service_in_company + rec.previous_insured_years

    @api.model
    def create(self, vals):
        if vals['emp_type'] == 'internal':
            vals['employee_card_id'] = self.env['ir.sequence'].next_by_code('internal.employee')
        if vals['emp_type'] == 'external':
            vals['employee_card_id'] = self.env['ir.sequence'].next_by_code('external.employee')
        result = super(HrEmployee, self).create(vals)
        return result

    def get_disciplinary_cases_history(self):
        for rec in self:
            return {
                'name': "Disciplinary Cases History",
                'res_model': 'disciplinary.cases.history',
                'view_mode': 'tree, form',

                'views': [(self.env.ref("kode_employee.disciplinary_cases_history_tree_view").id, "tree"),
                          (self.env.ref("kode_employee.disciplinary_cases_history_form_view").id, "form")],
                'type': 'ir.actions.act_window',
                'context': {
                    'default_employee_id': self.id,
                },
                'domain': [('employee_id', '=', self.id)]
            }

    def get_career_progression(self):
        for rec in self:
            return {
                'name': "Change of status",
                'res_model': 'career.progression',
                'view_mode': 'tree, form',
                'views': [(self.env.ref("kode_employee.career_progression_tree_view").id, "tree"),
                          (self.env.ref("kode_employee.career_progression_form_view").id, "form")],
                'type': 'ir.actions.act_window',
                'context': {
                    'default_employee_id': self.id,
                },
                'domain': [('employee_id', '=', self.id)]
            }


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    # assessment_name_id = fields.Many2one('assessment.name', string="Assessment Name")
    # evaluation = fields.Char(string="Evaluation")
    def _get_default_access_token(self):
        return str(uuid.uuid4())

    survey_ids = fields.Many2many('survey.survey', 'rel_servey_job', string="Apply Survey", related='job_id.survey_ids')
    survey_id = fields.Many2many('survey.survey', 'rel_survey_applicant', string="Survey")
    chosen_survey_id = fields.Many2one('survey.survey', string="Chosen Survey")
    assessment_ids = fields.One2many('hr.applicant.assessment.line', 'applicant_id')
    name = fields.Char("Subject / Application Name", required=False,
                       help="Email subject for applications sent via email")
    email_from = fields.Char("Email", required=True, size=128, help="Applicant email",
                             compute='_compute_partner_phone_email',
                             inverse='_inverse_partner_email', store=True)
    partner_mobile = fields.Char("Mobile", required=True, size=32, compute='_compute_partner_phone_email',
                                 inverse='_inverse_partner_mobile', store=True)
    partner_name = fields.Char("Applicant's Name", required=True)
    access_token = fields.Char('Access Token', default=lambda self: self._get_default_access_token(), copy=False)

    def get_start_url(self):
        return '%s?applicant_token=%s' % (self.chosen_survey_id.get_start_url(), self.access_token)

    # def action_send_information_form(self):
    #     self.ensure_one()
    #     survey_id = self.survey_id
    #     if not survey_id:
    #         raise UserError(_('No survey set on Application'))
    #     survey_invite_action = survey_id.action_send_survey()
    #     context = survey_invite_action.get('context', {})
    #     followers = self.message_follower_ids.filtered(lambda fol: fol.partner_id != self.env.user.partner_id).mapped('partner_id')
    #     print("followers",followers)
    #     print("followers",followers.ids)
    #     context.update({
    #         'default_partner_ids': followers.ids
    #     })
    #     survey_invite_action['context'] = context
    #
    #     return survey_invite_action

    def action_survey_user_input_completed(self):
        action = self.env['ir.actions.act_window']._for_xml_id('survey.action_survey_user_input')
        ctx = dict(self.env.context)
        ctx.update({
            'search_default_applicant_id': self.ids[0],
            'search_default_completed': 1,
            'search_default_not_test': 1})
        action['context'] = ctx
        # if self.survey_id.is_appraisal:
        action.update({
            'domain': [('applicant_id', '=', self.ids[0])]
        })
        return action

    # def action_send_survey(self):
    #     """ Open a window to compose an email, pre-filled with the survey message """
    #     # Ensure that this survey has at least one question.
    #     if not self.chosen_survey_id.question_ids:
    #         raise UserError(_('You cannot send an invitation for a survey that has no questions.'))
    #
    #     # Ensure that this survey has at least one section with question(s), if question layout is 'One page per section'.
    #     if self.chosen_survey_id.questions_layout == 'page_per_section':
    #         if not self.chosen_survey_id.page_ids:
    #             raise UserError(_('You cannot send an invitation for a "One page per section" survey if the survey has no sections.'))
    #         if not self.chosen_survey_id.page_ids.mapped('question_ids'):
    #             raise UserError(_('You cannot send an invitation for a "One page per section" survey if the survey only contains empty sections.'))
    #
    #     if not self.chosen_survey_id.active:
    #         raise exceptions.UserError(_("You cannot send invitations for closed surveys."))
    #
    #     template = self.chosen_survey_id.template_id
    #
    #     local_context = dict(
    #         self.env.context,
    #         default_survey_id=self.chosen_survey_id.id,
    #         default_use_template=bool(template),
    #         default_body=template.body_html,
    #         default_template_id=template and template.id or False,
    #         default_applicant_id=self.id,
    #         notif_layout='mail.mail_notification_light',
    #     )
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'survey.invite',
    #         'target': 'new',
    #         'context': local_context,
    #     }


class HrApplicantAssessmentLine(models.Model):
    _name = 'hr.applicant.assessment.line'

    assessment_name_id = fields.Many2one('assessment.name', string="Assessment Name")
    evaluation = fields.Char(string="Evaluation")
    applicant_id = fields.Many2one('hr.applicant', string="Applicant")


class HrContract(models.Model):
    _inherit = "hr.contract"

    def mail_reminder(self):
        """Sending expiry date notification for ID and Passport"""

        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        contracts = self.search([('state', '=', 'open')])
        for contract in contracts:
            if contract.date_end:
                exp_date = fields.Date.from_string(contract.date_end) - timedelta(days=30)
                if date_now >= exp_date:
                    mail_content = "  Hello  " + contract.hr_responsible_id.name + ",<br>The contract of employee  " + contract.employee_id.name + "is going to expire on " + \
                                   str(contract.date_end) + ". Please renew it before expiry date"
                    main_content = {
                        'subject': _('The -%s Expired On %s') % (contract.name, contract.date_end),
                        'author_id': self.env.user.partner_id.id,
                        # 'author_id': contract.hr_responsible_id.partner_id.id or self.env.uid,
                        'body_html': mail_content,
                        'email_from': self.env.user.email_formatted,
                        'email_to': contract.hr_responsible_id.email,
                    }

                    id = self.env['mail.mail'].sudo().create(main_content).send()


class ApplicantGetRefuseReason(models.TransientModel):
    _inherit = 'applicant.get.refuse.reason'
    _description = 'Get Refuse Reason'

    send_mail = fields.Boolean("Send Email")

    @api.depends('refuse_reason_id')
    def _compute_send_mail(self):
        for wizard in self:
            template = wizard.refuse_reason_id.template_id
            # wizard.send_mail = bool(template)
            wizard.template_id = template

    def action_refuse_reason_apply(self):
        if self.send_mail:
            if not self.template_id:
                raise UserError(_("Email template must be selected to send a mail"))
            if not self.applicant_ids.filtered(lambda x: x.email_from or x.partner_id.email):
                raise UserError(_("Email of the applicant is not set, email won't be sent."))
        self.applicant_ids.write({'refuse_reason_id': self.refuse_reason_id.id, 'active': False})
        if self.send_mail:
            # applicants = self.applicant_ids.filtered(lambda x: x.email_from or x.partner_id.email)
            # applicants.with_context(active_test=True).message_post_with_template(self.template_id.id, **{
            #     'auto_delete_message': True,
            #     'subtype_id': self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'),
            #     'email_layout_xmlid': 'mail.mail_notification_light'
            # })
            # partners = [self.applicant_ids[0].partner_id.id]
            #
            # values = self.applicant_ids.with_context(default_partner_ids=partners,
            #                                      default_emails=self.applicant_ids[0].email_from,
            #                                      active_model='hr.applicant',
            #                                      active_id=applicants.ids[0]).action_send_survey()
            # values['context']['default_template_id'] = self.template_id.id
            template = self.template_id

            local_context = dict(
                self.env.context,
                default_survey_id=self.id,
                default_use_template=bool(template),
                default_template_id=template and template.id or False,
                notif_layout='mail.mail_notification_light',
                default_model='hr.applicant',
                force_email=True,
            )
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'target': 'new',
                'context': local_context,
            }


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    parent_id = fields.Many2one('hr.employee', 'Department Manager', compute="_compute_parent_id", store=True,
                                readonly=False,
                                domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    coach_id = fields.Many2one(
        'hr.employee', 'Direct Manager', compute='_compute_coach', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help='Select the "Employee" who is the coach of this employee.\n'
             'The "Coach" has no specific rights or responsibilities by default.')
