from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


class ContractInherit(models.Model):
    _inherit = 'hr.contract'


    is_primary = fields.Boolean('Primary Contract', copy=False, default=True)
    end_of_probation_period_received = fields.Boolean(copy=False)
    end_of_probation_period = fields.Date(string='End of probation period', copy=False)

    @api.constrains('is_primary')
    def _check_primary_contract(self):
        for rec in self:
            if rec.is_primary:
                contracts = self.env['hr.contract'].sudo().search(
                    [('id', '!=', rec.id), ('employee_id', '=', rec.employee_id.id), ('is_primary', '=', True)])
                if contracts:
                    raise UserError(_('This Employee has primary contract already!'))

    @api.onchange('date_start', 'is_primary')
    def _set_end_of_probation_period(self):
        for rec in self:
            if rec.is_primary and rec.date_start:
                rec.end_of_probation_period = rec.date_start + relativedelta(months=3)


class HrEmployee(models.Model):
    _inherit = ["hr.employee"]

    ref_emp_id = fields.Many2one('hr.employee', string='Referred By', invisible=True, copy=False)
    employee_rewards_ids = fields.One2many(comodel_name="employee.referral.reward", inverse_name="rewarded_employee_id",
                                           string="Employee Rewards")

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        print('testttt', vals.get("applicant_id", False))
        print('testttt', vals)
        emp_referral_reward = False
        if res.applicant_id and len(res.applicant_id) == 1:
            reward_id = self.env['referral.reward'].sudo().search([('based_on', '=', 'create_applicant')])
            if reward_id:
                emp_referral_reward = self.env['employee.referral.reward'].sudo().create({
                    # 'referred_employee_id': self.id,
                    'rewarded_employee_id': res.applicant_id.ref_emp_id.id,
                    'reward_id': reward_id.id})
                print('emp_referral_reward', emp_referral_reward)
                if reward_id.send_email_auto:
                    # send email template then if the email successfully sent convert the line state to done
                    print('send automatically')
                    mail_content = reward_id.template_id.body_html
                    main_content = {
                        'subject': reward_id.template_id.subject,
                        'email_to': res.applicant_id.ref_emp_id.work_email,
                        'body_html': mail_content,
                    }
                    mail = self.env['mail.mail'].sudo().create(main_content)
                    mail.send()
                    print('mail', mail)
                    if mail.state != 'exception':
                        emp_referral_reward.state = 'received'
        if emp_referral_reward:
            emp_referral_reward.referred_employee_id = res.id
        return res


class Applicant(models.Model):
    _inherit = ["hr.applicant"]

    ref_emp_id = fields.Many2one('hr.employee', string='Referred By', tracking=True, copy=False)

    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.display_name
            else:
                if not applicant.partner_name:
                    raise UserError(_('You must define a Contact Name for this applicant.'))
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'type': 'private',
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile
                })
                applicant.partner_id = new_partner_id
                address_id = new_partner_id.address_get(['contact'])['contact']
            if applicant.partner_name or contact_name:
                employee_data = {
                    'default_name': applicant.partner_name or contact_name,
                    'default_job_id': applicant.job_id.id,
                    'default_job_title': applicant.job_id.name,
                    'default_address_home_id': address_id,
                    'default_department_id': applicant.department_id.id or False,
                    'default_address_id': applicant.company_id and applicant.company_id.partner_id
                                          and applicant.company_id.partner_id.id or False,
                    'default_work_email': applicant.department_id and applicant.department_id.company_id
                                          and applicant.department_id.company_id.email or False,
                    'default_work_phone': applicant.department_id.company_id.phone,
                    'form_view_initial_mode': 'edit',
                    'default_applicant_id': applicant.ids,
                    'default_ref_emp_id': applicant.ref_emp_id.id,
                }

        dict_act_window = self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list')
        dict_act_window['context'] = employee_data
        return dict_act_window
