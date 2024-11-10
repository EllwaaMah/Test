from odoo import api, fields, models
from datetime import date, datetime, timedelta


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields):
        result = super(MailComposeMessage, self).default_get(fields)
        if self._context.get('active_model') == 'employee.referral.reward':

            active_emp_referral_reward = self.env['employee.referral.reward'].sudo().browse(
                self._context.get('active_id'))
            if active_emp_referral_reward:
                result['template_id'] = active_emp_referral_reward.reward_id.template_id.id
        filtered_result = dict((fname, result[fname]) for fname in result if fname in fields)
        return filtered_result

    def _action_send_mail(self, **kwargs):
        for wizard in self:
            if wizard.model == 'employee.referral.reward':
                self.env[wizard.model].sudo().browse(wizard.res_id).state = 'received'
        return super()._action_send_mail(**kwargs)


class EmployeeReferralReward(models.Model):
    _name = "employee.referral.reward"
    _description = 'Employee Referral Reward'

    name = fields.Char(string="Name", default="/")
    referred_employee_id = fields.Many2one('hr.employee', string="Referred Employee")
    rewarded_employee_id = fields.Many2one('hr.employee', string="Rewarded Employee")
    reward_id = fields.Many2one('referral.reward', string="Reward")
    state = fields.Selection(string="state", selection=[('in_progress', 'In Progress'),
                                                        ('received', 'Email Received'),
                                                        ('reward_received', 'Reward Received')], default='in_progress',
                             readonly=True)

    @api.model
    def create(self, vals):
        print("vals.get('name')", vals.get('name'))
        if vals.get('name') == '/' or vals.get('name') is None:
            vals['name'] = self.env['ir.sequence'].next_by_code('emp.referral.reward.seq') or '/'
        return super(EmployeeReferralReward, self).create(vals)

    @api.model
    def _cron_reward_for_end_of_probation_period(self):
        contracts = self.env['hr.contract'].search(
            [('state', '=', 'open'), ('is_primary', '=', True), ('end_of_probation_period_received', '=', False),
             ('end_of_probation_period', '=', date.today())])
        if contracts:
            reward_id = self.env['referral.reward'].sudo().search([('based_on', '=', 'end_of_probation')])
            for contract in contracts:
                if reward_id:
                    print('contract.employee_id.applicant_id', contract.employee_id.applicant_id.ids[0])
                    applicant_id = self.env['hr.applicant'].browse(contract.employee_id.applicant_id.ids[0])

                    emp_referral_reward = self.env['employee.referral.reward'].sudo().create({
                        'referred_employee_id': contract.employee_id.id,
                        'rewarded_employee_id': applicant_id.ref_emp_id.id,
                        'reward_id': reward_id.id})
                    print('emp_referral_reward', emp_referral_reward)
                    if reward_id.send_email_auto:
                        # send email template then if the email successfully sent convert the line state to done
                        print('send automatically')
                        mail_content = reward_id.template_id.body_html
                        main_content = {
                            'subject': reward_id.template_id.subject,
                            'email_to': applicant_id.ref_emp_id.work_email,
                            'body_html': mail_content,
                        }
                        mail = self.env['mail.mail'].sudo().create(main_content)
                        mail.send()
                        print('mail', mail)
                        if mail.state != 'exception':
                            emp_referral_reward.state = 'received'

                    contract.end_of_probation_period_received = True

    @api.model
    def _cron_reward_appraisal_high_score_cron(self):
        contracts = self.env['hr.contract'].search(
            [('state', '=', 'open'), ('is_primary', '=', True), ('end_of_probation_period_received', '=', False),
             ('end_of_probation_period', '=', date.today())])
        if contracts:
            reward_id = self.env['referral.reward'].sudo().search([('based_on', '=', 'appraisal_high_score')])
            for contract in contracts:
                if reward_id:
                    print('contract.employee_id.applicant_id', contract.employee_id.applicant_id.ids[0])
                    applicant_id = self.env['hr.applicant'].browse(contract.employee_id.applicant_id.ids[0])

                    emp_referral_reward = self.env['employee.referral.reward'].sudo().create({
                        'referred_employee_id': contract.employee_id.id,
                        'rewarded_employee_id': applicant_id.ref_emp_id.id,
                        'reward_id': reward_id.id})
                    print('emp_referral_reward', emp_referral_reward)
                    if reward_id.send_email_auto:
                        # send email template then if the email successfully sent convert the line state to done
                        print('send automatically')
                        mail_content = reward_id.template_id.body_html
                        main_content = {
                            'subject': reward_id.template_id.subject,
                            'email_to': applicant_id.ref_emp_id.work_email,
                            'body_html': mail_content,
                        }
                        mail = self.env['mail.mail'].sudo().create(main_content)
                        mail.send()
                        print('mail', mail)
                        if mail.state != 'exception':
                            emp_referral_reward.state = 'received'

                    contract.end_of_probation_period_received = True

    def action_send_reward(self):
        for rec in self:
            rec.state = 'reward_received'

