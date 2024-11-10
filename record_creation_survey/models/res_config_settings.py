from datetime import timedelta

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    send_information_form_stage_id = fields.Many2one('crm.stage', related='company_id.send_information_form_stage_id', readonly=False)
