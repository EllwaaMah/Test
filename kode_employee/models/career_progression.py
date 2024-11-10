from odoo import api, fields, models

class HrContract(models.Model):
    _inherit = "hr.contract"

    current_wage = fields.Monetary(string="Wage")

    @api.onchange('current_wage')
    def set_start_wage(self):
        for rec in self:
            if rec.current_wage:
                rec.wage = rec.current_wage


class CareerProgression(models.Model):
    _name = "career.progression"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=1)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    previous_job_id = fields.Many2one('hr.job', string="Previous Job Position")
    previous_department_id = fields.Many2one('hr.department', string="Previous Department")
    previous_manager_id = fields.Many2one('hr.employee', string="Previous Manager")
    previous_salary = fields.Float(string="Previous Salary")
    new_job_id = fields.Many2one('hr.job', string="New Job Position")
    new_department_id = fields.Many2one('hr.department', string="New Department")
    new_manager_id = fields.Many2one('hr.employee', string="New Manager")
    new_salary = fields.Float(string="New Salary")
    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('confirm', 'Confirmed'), ], required=False,
                             default='draft')

    @api.onchange('employee_id')
    def onchange_employee(self):
        for rec in self:
            if rec.employee_id:
                rec.end_date = rec.employee_id.contract_id.date_end
                rec.previous_job_id = rec.employee_id.job_id
                rec.previous_department_id = rec.employee_id.department_id
                rec.previous_manager_id = rec.employee_id.parent_id
                rec.previous_salary = rec.employee_id.contract_id.wage
            else:
                rec.end_date = False
                rec.previous_job_id = False
                rec.previous_department_id = False
                rec.previous_manager_id = False
                rec.previous_salary = False
    @api.onchange('new_job_id')
    def onchange_new_department_id(self):
        for rec in self:
            if rec.new_job_id:
                rec.new_department_id = rec.new_job_id.department_id
                rec.new_manager_id = rec.new_department_id.manager_id
            else:
                rec.new_manager_id = False
                rec.new_department_id = False

    def confirm_change(self):
        for rec in self:
            rec.employee_id.job_id = rec.new_job_id
            rec.employee_id.department_id = rec.new_department_id
            rec.employee_id.parent_id = rec.new_manager_id
            rec.employee_id.contract_id.wage = rec.new_salary
            rec.state = 'confirm'
            pass
