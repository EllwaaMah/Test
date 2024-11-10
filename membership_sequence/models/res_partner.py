# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    membership_type = fields.Selection([('central', 'Central Member'), ('member', 'Family Member'),('other','Non-subscriber')],
                                       string="Membership Type", copy=False)
    central_partner_id = fields.Many2one(
        'res.partner', string='Central Family Member',
        domain=[('membership_type', '=', 'central')], copy=False
    )

    family_members_ids = fields.One2many('res.partner', 'central_partner_id')

    all_members_ids = fields.Many2many(
        comodel_name='res.partner',
        relation="res_partner_all_family_members_rel",
        column1="partner_id", column2="member_id",
        compute="_compute_members", store=True
    )
    family_members_count = fields.Integer(
        compute="_compute_members", store=True
    )
    membership_code = fields.Text(copy=False)
    membership_status = fields.Selection(
        [('running', 'Running'), ('suspended', 'Expired'), ('no_sub', 'No Subscription')],
        compute='_compute_subscription_status')

    active_subscription_ids = fields.One2many('sale.subscription','partner_id',domain=[('stage_category', '=', 'progress')])

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._set_membership_id()
        return res

    def write(self, vals):
        res = super().write(vals)
        if vals.get('membership_type') or vals.get('central_partner_id'):
            self._set_membership_id()
        return res

    def _set_membership_id(self):
        # using super() to skip recursive calls. (write, will call write, will call write)
        for record in self:
            if record.membership_type == 'central':
                super(ResPartner, record).write(
                    {'membership_code': record.env['ir.sequence'].next_by_code('membership.sequence'),
                     'central_partner_id': False})
            elif record.membership_type == 'member' and record.central_partner_id.membership_code:
                new_family_members_count = record.central_partner_id.family_members_count + 1
                super(ResPartner, record).write({
                    'membership_code': record.central_partner_id.membership_code + f' - {new_family_members_count}'
                })

    @api.depends(
        'central_partner_id', 'central_partner_id.family_members_ids',
        'family_members_ids'
    )
    def _compute_members(self):
        for rec in self:
            members = rec.central_partner_id | rec.family_members_ids
            members |= rec.central_partner_id.family_members_ids | rec
            rec.all_members_ids = members
            rec.family_members_count = len(members)

    def show_family_members(self):
        self.ensure_one()
        domain = [('id', 'in', self.all_members_ids.ids)]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contacts',
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'domain': domain,
            'context': "{'create': False}"
        }

    @api.depends('central_partner_id.membership_status','active_subscription_ids')
    def _compute_subscription_status(self):
        for rec in self:
            #if they have an active subscription then they are central members always.
            if rec.active_subscription_ids:
                rec.central_partner_id = False
                rec.membership_type = 'central'
            #if they have
            rec.membership_status = (rec.active_subscription_ids and 'running') or \
                                     (rec.membership_type == 'member' and rec.central_partner_id.membership_status) or \
                                     (not rec.active_subscription_ids and rec.subscription_count and 'suspended') or\
                                      'no_sub'