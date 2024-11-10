from odoo import models, fields, api, _
from datetime import date, timedelta
from random import randint


class ContractView(models.Model):
    _name = "contract.view"
    _description = "Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]

# -------------------| Start Serial Fields |------------------
    serial = fields.Char(string="Serial", default=lambda self: _("New"), readonly=True)
    priority = fields.Selection(selection=[("normal", "Normal"), ("vip", "VIP")], string="Priority")
# -------------------| End Serial Fields |--------------------
    
# -------------------| Start Statusbar Fields |---------------
    state = fields.Selection(selection=[("draft", "Draft"), ("confirmed", "Confirmed"), ("done", "Done")],
                             default="draft")
# -------------------| End Statusbar Fields |-----------------
    
    name = fields.Char(string="Name", required=True, tracking=True)
    image = fields.Binary(string="Image")
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)




# -------------------| Start Serial Section Function Multi Company |--------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            company_id = vals.get('company_id') or self.env.company.id
            sequence = self.env['ir.sequence'].with_context(force_company=company_id)
            vals['serial'] = sequence.next_by_code('contract_view_sequence') or _('New')
        return super(ContractView, self).create(vals_list)
# -------------------| End Serial Section Function Multi Company |----------------
    
# -------------------| Start Statusbar Logic |----------------------
    def button_draft(self):
        for rec in self:
            rec.state = "draft"

    def button_confirmed(self):
        for rec in self:
            rec.state = "confirmed"

    def button_done(self):
        for rec in self:
            rec.state = "done"
# -------------------| End Statusbar Logic |-----------------------
        


