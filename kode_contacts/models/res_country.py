# © 2022 Bitsera Solutions (<http://bitsera-solutions.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ResCountry(models.Model):
    _inherit = 'res.country'

    @api.model
    def _get_country_by_code(self, code):
        return self.search([('code', 'ilike', code)], limit=1)
