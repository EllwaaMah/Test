from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    shopify_code = fields.Char()
    