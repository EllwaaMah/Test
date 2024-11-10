from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import AccessError, UserError, ValidationError


class EmploymentType(models.Model):
    _name = "employment.type"
    _description = 'Employment Type'

    name = fields.Char(string="Name", required=True)


class WorkingPlan(models.Model):
    _name = "working.plan"
    _description = 'Working Plan'

    name = fields.Char(string="Name", required=True)


class ReplacementReason(models.Model):
    _name = "replacement.reason"
    _description = 'Replacement Reason'

    name = fields.Char(string="Name", required=True)


class RecruitmentRequisition(models.Model):
    _name = "recruitment.requisition"
    _description = 'Recruitment Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", default="/", readonly=True, copy=False)
    job_id = fields.Many2one('hr.job', string="Position", required=True, tracking=True,
                             )

    department_id = fields.Many2one('hr.department', related="job_id.department_id", readonly=True,
                                    string="Department", help="Employee")
    manager_id = fields.Many2one(string='Direct Manager', related='department_id.manager_id')
    no_of_vacancies = fields.Integer("No of Vacancies", default=1, tracking=True)
    hiring_reason = fields.Selection(string='Hiring Reason',
                                     selection=[('new', 'New Position'), ('replace', 'Replacement')], default="new",
                                     tracking=True)
    replacement_reason_id = fields.Many2one('replacement.reason', string="Replacement Reason")
    former_emp_id = fields.Many2one('hr.employee', string="Former Employee", help="Former Employee", tracking=True)
    former_emp_barcode = fields.Char(string="Former Employee ID", related="former_emp_id.employee_card_id",
                                     help="ID used for employee identification.", groups="hr.group_hr_user", copy=False)
    vacancy_date = fields.Date(string="Vacancy Date", tracking=True)
    included_in_wfp = fields.Boolean(string="Included in WFP")
    wfp_reason = fields.Char(string="Reasons")
    desired_hiring_date = fields.Date(string="Desired Hiring Date", required=True)
    ceo_approval_date = fields.Datetime(string="CEO Approval Date")
    contract_type_id = fields.Many2one('hr.contract.type', string="Contract Type", required=True,
                                       default=lambda self: self.env['hr.contract.type'].search([], limit=1))
    employment_type = fields.Many2one('employment.type', string="Employment Type", required=True,
                                      default=lambda self: self.env['employment.type'].search([], limit=1),
                                      tracking=True)
    working_plan = fields.Many2one('working.plan', string="Working Plan", required=True, tracking=True)
    description = fields.Html(string='Job Description', related="job_id.description", readonly=False)
    requirements = fields.Text(string='Job Requirements', related="job_id.requirements", readonly=False)
    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Pending Manager Approval'), ('bp_approval', 'Pending BP Approval'),
         ('hr_m_approval', 'Pending HR Manager Approval'),
         ('ceo_approval', 'Pending CEO Approval'), ('under_recruitment', 'Under Recruitment'),
         ('done', 'Done'), ('reject', 'Reject')], readonly=True, default='draft', copy=False,
        string="Status", tracking=True)
    all_application_count = fields.Integer(compute='_compute_all_application_count', string="All Application Count")
    all_hired_employees_count = fields.Integer(compute='_compute_all_application_count', string="All Application Count")
    log_ids = fields.One2many(comodel_name="requisition.log", inverse_name="requisition_id",
                              string="Approvals Log Times")
    durations_of_hiring_employees = fields.One2many(comodel_name="hiring.duration", inverse_name="requisition_id",
                                                    string="Approvals Log Times")

    whole_cycle_duration = fields.Float(string='Whole Cycle Duration', compute='_compute_whole_cycle_duration')

    @api.depends('durations_of_hiring_employees')
    def _compute_whole_cycle_duration(self):
        for rec in self:
            if rec.durations_of_hiring_employees:
                rec.whole_cycle_duration = max(rec.durations_of_hiring_employees.mapped('duration'))
            else:
                rec.whole_cycle_duration = False

    def _compute_all_application_count(self):
        for rec in self:
            applicants = self.env['hr.applicant'].sudo().search(
                [('job_id', '=', rec.job_id.id), ('requisition_id', '=', rec.id)])
            count_applicants = self.env['hr.applicant'].sudo().search_count(
                [('job_id', '=', rec.job_id.id), ('requisition_id', '=', rec.id)])
            count_employees = self.env['hr.employee'].sudo().search_count([('applicant_id', 'in', applicants.ids)])

            rec.all_application_count = count_applicants
            rec.all_hired_employees_count = count_employees

    def approval_process(self):
        for rec in self:
            if self.env.user.has_group(
                    'recruitment_requisition.group_recruitment_requisition_ceo') and rec.state == 'ceo_approval':
                rec.state = 'under_recruitment'
                rec.ceo_approval_date = fields.Datetime.now()
                rec.job_id.ready_to_start = True
                rec.job_id.no_of_recruitment = rec.no_of_vacancies
                duration = fields.Datetime.now() - rec.create_date
                duration_in_days = duration.days
                self.env["requisition.log"].sudo().create(
                    {
                        "approved_by": self.env.user.id,
                        "duration": duration_in_days,
                        "requisition_id": rec.id,
                        "approval_state": 'CEO Approval',
                    }
                )

            elif self.env.user.has_group(
                    'recruitment_requisition.group_recruitment_requisition_manager') and rec.state not in [
                'ceo_approval', 'under_recruitment', 'done']:
                rec.state = 'ceo_approval'
                duration = fields.Datetime.now() - rec.create_date
                duration_in_days = duration.days
                self.env["requisition.log"].sudo().create(
                    {
                        "approved_by": self.env.user.id,
                        "duration": duration_in_days,
                        "requisition_id": rec.id,
                        "approval_state": 'HR Manager Approval',
                    }
                )

            elif rec.department_id.hr_business_partner_id and rec.department_id.hr_business_partner_id == self.env.user and rec.state == 'bp_approval':
                rec.state = 'hr_m_approval'
                duration = fields.Datetime.now() - rec.create_date
                duration_in_days = duration.days
                self.env["requisition.log"].sudo().create(
                    {
                        "approved_by": self.env.user.id,
                        "duration": duration_in_days,
                        "requisition_id": rec.id,
                        "approval_state": 'Business Partner Approval',
                    }
                )
            elif rec.department_id.manager_id.user_id and rec.department_id.manager_id.user_id == self.env.user and rec.state == 'submit':
                rec.state = 'bp_approval'
                duration = fields.Datetime.now() - rec.create_date
                duration_in_days = duration.days
                self.env["requisition.log"].sudo().create(
                    {
                        "approved_by": self.env.user.id,
                        "duration": duration_in_days,
                        "requisition_id": rec.id,
                        "approval_state": 'Department Manager Approval',
                    }
                )
            else:
                raise AccessError(
                    _("You don't have the access rights to approve this requisition."))

    def action_done(self):
        for rec in self:
            if self.env.user.has_group('recruitment_requisition.group_recruitment_requisition_manager'):
                rec.state = 'done'
                rec.job_id.ready_to_start = False
            else:
                raise AccessError(
                    _("You don't have the access rights to close this requisition."))


    def action_submit(self):
        for rec in self:
            rec.state = 'submit'


    def action_reset(self):
        for rec in self:
            if self.env.user.has_group('recruitment_requisition.group_recruitment_requisition_manager'):
                rec.state = 'draft'
            else:
                raise AccessError(
                    _("You don't have the access rights to close this requisition."))

    def action_reject(self):
        for rec in self:
            if self.env.user.has_group('recruitment_requisition.group_recruitment_requisition_manager'):
                rec.state = 'reject'
            else:
                raise AccessError(
                    _("You don't have the access rights to close this requisition."))

    @api.model
    def create(self, vals):
        print("vals.get('name')", vals.get('name'))
        if vals.get('name') == '/' or vals.get('name') is None:
            vals['name'] = self.env['ir.sequence'].next_by_code('recruitment.requisition.seq') or '/'
        return super(RecruitmentRequisition, self).create(vals)

    def action_open_hired_employees(self):
        self.ensure_one()
        applicants = self.env['hr.applicant'].sudo().search(
            [('job_id', '=', self.job_id.id), ('requisition_id', '=', self.id)])
        hired_employees = self.env['hr.employee'].sudo().search([('applicant_id', 'in', applicants.ids)])
        action = self.env["ir.actions.actions"]._for_xml_id("hr.open_view_employee_list_my")
        if len(hired_employees) > 1:
            action['domain'] = [('id', 'in', hired_employees.ids)]
        elif len(hired_employees) == 1:
            form_view = [(self.env.ref('hr.view_employee_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = hired_employees.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        action['context'] = dict(self._context, create=False)
        return action


class RequisitionLog(models.Model):
    _name = "requisition.log"
    _description = 'Requisition Log'
    _rec_name = "create_date"

    approved_by = fields.Many2one('res.users', 'Approved by')
    duration = fields.Float('Duration')
    requisition_id = fields.Many2one('recruitment.requisition', string="Requisition")
    approval_state = fields.Char('Approval Type')


class HiringDuration(models.Model):
    _name = "hiring.duration"
    _description = 'Hiring Duration'
    _rec_name = "create_date"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    employee_create_date = fields.Datetime('Employee Creating Date')
    duration = fields.Float('Duration')
    requisition_id = fields.Many2one('recruitment.requisition', string="Requisition")


class HrEmployee(models.Model):
    _inherit = ["hr.employee"]

    ref_emp_id = fields.Many2one('hr.employee', string='Referred By', invisible=True, copy=False)
    employee_rewards_ids = fields.One2many(comodel_name="employee.referral.reward", inverse_name="rewarded_employee_id",
                                           string="Employee Rewards")

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        if res.applicant_id and len(res.applicant_id) == 1:
            requisition_id = self.env['recruitment.requisition'].sudo().search(
                [('job_id', '=', res.applicant_id.job_id.id), ('state', '=', 'under_recruitment')],
                limit=1)
            if requisition_id:
                duration = res.create_date - requisition_id.ceo_approval_date
                duration_in_days = duration.days

                hiring_duration_id = self.env['hiring.duration'].sudo().create({
                    'requisition_id': requisition_id.id,
                    'employee_id': res.id,
                    'employee_create_date': res.create_date,
                    'duration': duration_in_days})
        return res
