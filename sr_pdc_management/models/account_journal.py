
from odoo import models, fields, api, _

class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    PDC = [
        ('pdc_received','PDC Received'),
        ('pdc_issued','PDC Issued')
    ]

    pdc_type = fields.Selection(PDC, string="PDC Type")