from odoo import api, fields, models
from datetime import date


class ViolationType(models.Model):
    _name = "violation.type"

    name = fields.Char(string="Name", required=1)
    

class DisciplinaryAction(models.Model):
    _name = "disciplinary.action"

    name = fields.Char(string="Name", required=1)


class DisciplinaryCasesHistory(models.Model):
    _name = "disciplinary.cases.history"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=1)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    reported_by_id = fields.Many2one('hr.employee', string="Reported by")
    assigned_to_id = fields.Many2one('res.users', string="Assigned to")
    violation_type_id = fields.Many2one('violation.type', string="Violation Type")

    disciplinary_action_id = fields.Many2one('disciplinary.action', string="Disciplinary Action")
    category_comment = fields.Text(string="Category comment")
    disciplinary_action_comment = fields.Text(string="Description")
    state = fields.Selection(string="state", selection=[('initiated', 'initiated'),
                                                        ('in_progress', 'In Progress'),
                                                        ('close', 'Closed'), ], required=False, default='initiated')
    disciplinary_date = fields.Date(string="Disciplinary Date")
    close_date = fields.Date(string="Close Date")

    def button_initiated(self):
        for rec in self:
            rec.state = 'in_progress'

    def button_inprogress(self):
        for rec in self:
            rec.state = 'close'
            rec.close_date = date.today()
            # rec.close_date = today_date.strftime("%B/%d/%Y")
