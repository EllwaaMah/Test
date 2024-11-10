from odoo import api, fields, models


class ReferralReward(models.Model):
    _name = "referral.reward"
    _description = 'Reward'

    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=1)
    based_on = fields.Selection([
        ('create_applicant', 'Employee Conversion Process'),
        ('end_of_probation', 'End of probation period'),
        ('appraisal_high_score', 'Appraisal high score'),
    ], string='Based On', index=True, default='create_applicant',
        help="Defines what is the reward type")
    template_id = fields.Many2one('mail.template', 'Use template', domain="[('model', '=', 'employee.referral.reward')]")
    send_email_auto = fields.Boolean(string="Auto e-mail Notification",)
    appraisal_high_score_avg = fields.Float(string='Appraisal HighScore AVG', default=1)
