# © 2022 Bitsera Solutions (<http://bitsera-solutions.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ResCity(models.Model):
    _inherit = 'res.city'

    @api.model
    def _get_city_by_name(self, name):
        return self.search([('name', 'ilike', name)], limit=1)
