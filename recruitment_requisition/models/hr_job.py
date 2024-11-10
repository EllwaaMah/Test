from odoo import api, fields, models
from datetime import date, datetime, timedelta
from odoo.osv import expression


class HrJob(models.Model):
    _inherit = 'hr.job'

    ready_to_start = fields.Boolean(string="Ready To Start")
    state = fields.Selection([('open', 'Not Recruiting'),
                              ('recruit', 'Recruitment in Progress')
                              ], string='Status', readonly=True, required=True, tracking=True, copy=False,
                             default='open',
                             help="Set whether the recruitment process is open or closed for this job position.")

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        super(HrJob, self)._name_search(
            name, args=None, operator='ilike', limit=100, name_get_uid=None)
        if self.env.user.has_group(
                "recruitment_requisition.group_recruitment_requisition_manager") or self.env.user.has_group(
                "recruitment_requisition.group_recruitment_requisition_ceo"):
            domain = [('name', 'ilike', name)]
        else:
            domain = ['|', ('department_id.hr_business_partner_id', '=', self.env.user.id), ('department_id.manager_id.user_id', '=', self.env.user.id), ('name', 'ilike', name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    # To apply domain to load menu_________ 1
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        _ = self._context or {}
        if not self.env.user.has_group(
                "recruitment_requisition.group_recruitment_requisition_manager") and not self.env.user.has_group(
                "recruitment_requisition.group_recruitment_requisition_ceo"):
            args += [
                '|', ('department_id.hr_business_partner_id', '=', self.env.user.id), ('department_id.manager_id.user_id', '=', self.env.user.id),
            ]
        return super(HrJob, self).search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
        )


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    requisition_id = fields.Many2one('recruitment.requisition', string="Requisition",
                                     domain="[('state', '=', 'under_recruitment')]")

    @api.model
    def create(self, vals):
        if vals.get('job_id'):
            requisition_id = self.env['recruitment.requisition'].sudo().search(
                [('state', '=', 'under_recruitment'), ('job_id', '=', vals['job_id'])], limit=1)
            if requisition_id:
                vals['requisition_id'] = requisition_id.id
        return super(HrApplicant, self).create(vals)
