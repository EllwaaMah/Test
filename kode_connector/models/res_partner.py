# -*- coding: utf-8 -*-
# © 2021 DGTera systems (<http://www.dgtera.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def write(self, vals):
        kode_connector = self.env['kode.connector']._get_kode_instance()
        if kode_connector and any(
                f in vals.keys()
                for f in kode_connector.mapped('field_ids.name')
        ):
            for rec in self:
                kode_connector._send_request_signal(data={'id': rec.id})
        return super(ResPartner, self).write(vals)
