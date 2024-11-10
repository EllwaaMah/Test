from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    send_information_form_stage_id = fields.Many2one('crm.stage')