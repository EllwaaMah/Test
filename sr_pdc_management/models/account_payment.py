
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from num2words import num2words

class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        result = {}
        if self.payment_type == "inbound":
            result = {'domain': {'journal_id': ['|', ('type', 'in', ['sale','purchase','cash','general']), ('pdc_type','=', 'pdc_received')] }} 
        if self.payment_type == "outbound":
            result = {'domain': {'journal_id': ['|', ('type', 'in', ['sale','purchase','cash','general']), ('pdc_type','=', 'pdc_issued')] }}
        return result


    text_amount = fields.Char(compute="amount_to_words", store=True)
    unit = fields.Char(string="Unit No.")

    @api.depends('amount')
    def amount_to_words(self):
        for rec in self:
            rec.text_amount = num2words(rec.amount, lang='ar_AR')

   
    def action_print_report_payment_receive(self):
        return self.env.ref('sr_pdc_management.action_report_down_account_payment_receive').report_action(self)

    def action_print_report_payment_send(self):
        return self.env.ref('sr_pdc_management.action_report_down_account_payment_send').report_action(self)


   