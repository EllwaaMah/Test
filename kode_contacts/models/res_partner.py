# © 2022 Bitsera Solutions (<http://bitsera-solutions.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import date


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    def read(self, fields=None, load='_classic_read'):
        """
        somehow the fields are came from the another object ('res.partner')
        """
        if fields and any(f not in self._fields for f in fields):
            fields = [f for f in self._fields if f in fields]
        return super(CRMLead, self).read(fields=fields, load=load)

    def _get_partner_phone_update(self):
        return False

class ResPartner(models.Model):
    _inherit = 'res.partner'

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ])
    birthday = fields.Date()
    partner_age = fields.Char(string='Age', compute='_compute_partner_age')
    passport_number = fields.Char()
    occupation_company_name = fields.Char(string="Occupation & Company Name")
    education = fields.Char()
    member_id = fields.Many2one(comodel_name="res.partner")
    referred_member_ids = fields.One2many(
        comodel_name="res.partner", inverse_name="member_id"
    )
    city = fields.Char(
        inverse="_inverse_city", store=True
    )
    country_code = fields.Char(
        compute="_compute_country_code", inverse="_inverse_country_code",
        store=True
    )

    def _onchange_phone_validation(self):
        return


    @api.depends('country_id')
    def _compute_country_code(self):
        for rec in self:
            rec.country_code = rec.country_id.code


    def _inverse_country_code(self):
        for rec in self:
            rec.country_id = self.env['res.country']._get_country_by_code(
                rec.country_code
            ).id

    def _inverse_city(self):
        for rec in self:
            city_id = self.env['res.city']._get_city_by_name(rec.city)
            rec.city_id = city_id.id
            rec.zip = city_id.zipcode
            rec.country_id = city_id.country_id.id
            rec.state_id = city_id.state_id.id

    @api.depends('birthday')
    def _compute_partner_age(self):
        for partner in self:
            partner_age = ' '
            if partner.birthday:
                b_date = relativedelta(date.today(), partner.birthday)
                years, months, day = b_date.years, b_date.months, b_date.days
                if years:
                    partner_age += '%dYear/s ' % years
                if months:
                    partner_age += '%dMonth/s ' % months
                if day:
                    partner_age += '%dday/s' % day
            partner.partner_age = partner_age

    def _migrate_data(self):
        for rec in self.search([]):
            rec.gender = rec.x_studio_gender and rec.x_studio_gender.lower() or ''
            rec.birthday = rec.x_studio_date_of_birth
            rec.passport_number = rec.x_studio_idpassport_number
            rec.occupation_company_name = rec.x_studio_occupation_company_name
            rec.education = rec.x_studio_education
            rec.member_id = rec.x_studio_referrer.id
