# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from email.policy import default
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'out_receipt': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
    'in_receipt': 'supplier',
}


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_pdc_payment_account = fields.Many2one('account.account', 'PDC Payment Account for Customer')
    vendor_pdc_payment_account = fields.Many2one('account.account', 'PDC Payment Account for Vendors/Suppliers')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        res['customer_pdc_payment_account'] = int(
            self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account', default=0))
        res['vendor_pdc_payment_account'] = int(
            self.env['ir.config_parameter'].sudo().get_param('vendor_pdc_payment_account', default=0))

        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('customer_pdc_payment_account',
                                                         self.customer_pdc_payment_account.id)
        self.env['ir.config_parameter'].sudo().set_param('vendor_pdc_payment_account',
                                                         self.vendor_pdc_payment_account.id)

        super(ResConfigSettings, self).set_values()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    pdc_id = fields.Many2one('sr.pdc.payment', 'Post Dated Cheques')


class AccountMove(models.Model):
    _inherit = "account.move"

    pdc_id = fields.Many2one('sr.pdc.payment', 'Post Dated Cheques')
    pdc_ref_id = fields.Many2one('sr.pdc.payment', 'Post Dated Cheques')
    cheque_ref = fields.Char('Cheque Reference')

    # def open_pdc_payment_view(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _("PDC Payment"),
    #         'res_model': 'sr.pdc.payment',
    #         'view_mode': 'form',
    #         'domain': [('invoice_ids', '=', self.id), ('move_type', '=', 'out_invoice')],
    #         'views': [(self.env.ref('sr_pdc_management.sr_pdc_payment_tree').id, 'tree'), (False, 'form')],
    #     }

    def action_opening_invoice(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''

        return {
            'name': _('Invoice'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


    def action_invoice_pdc_payment(self):
        return self.env['sr.pdc.payment'] \
            .with_context(active_ids=self.ids, active_model='account.move', active_id=self.id) \
            .action_register_payment()

    def action_bill_pdc_payment(self):
        return self.env['sr.pdc.payment'] \
            .with_context(active_ids=self.ids, active_model='account.move', active_id=self.id) \
            .action_register_payment()

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state')
    def _compute_amount(self):
        invoice_ids = [move.id for move in self if move.id and move.is_invoice(include_receipts=True)]
        self.env['account.payment'].flush(['state'])
        if invoice_ids:
            self._cr.execute(
                '''
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                        OR
                        (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE move.state IN ('posted')
                    -- AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                ''', [tuple(invoice_ids)]
            )
            in_payment_set = set(res[0] for res in self._cr.fetchall())
        else:
            in_payment_set = {}

        for move in self:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            print("=======self._context======", self._context)
            if self._context.get('pdc'):
                total_residual = 0
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = -total
            move.amount_residual_signed = total_residual

            currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
            is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual

            # Compute 'invoice_payment_state'.
            if move.state == 'posted' and is_paid:
                if move.id in in_payment_set:
                    move.payment_state = 'in_payment'
                else:
                    move.payment_state = 'paid'
            else:
                move.payment_state = 'not_paid'


class PdcPayment(models.Model):
    _name = "sr.pdc.payment"
    _description = "PDC Payment"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    invoice_ids = fields.Many2many('account.move', 'account_invoice_pdc_rel', 'pdc_id', 'invoice_id', string="Invoices",
                                    readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, )
    state = fields.Selection(
        [('draft', 'Draft'), ('register', 'Registered'), ('return', 'Returned'), ('deposit', 'Deposited'),
         ('bounce', 'Bounced'), ('done', 'Collected'), ('cancel', 'Cancelled')], readonly=True, default='draft', 
        string="Status")

    deposit_journal_id = fields.Many2one('account.journal', string='Bank Journal', domain=[('type', 'in', ['bank'])])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, )
    due_date = fields.Date(string='Due Date', default=fields.Date.context_today, required=True, )
    
    deposit_date = fields.Date(string='Deposit Date', default=fields.Date.context_today, )
    bounce_date = fields.Date(string='Bounce Date', default=fields.Date.context_today, )
    return_date = fields.Date(string='Return Date', default=fields.Date.context_today, )
    physically_received = fields.Boolean(string="Physically Received", default=False)

    communication = fields.Char(string='Memo')
    cheque_ref = fields.Char('Cheque Reference')
    agent = fields.Char('Agent')
    bank = fields.Many2one('res.bank', string="Bank")
    name = fields.Char('Name')
    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')], string='Payment Type', required=True, )
    batch_id = fields.Many2one('batch.pdc.payment', string='Batch', invisible=True)
    registered_deposit_entry = fields.Many2one('account.move', string="Registered Deposit Entry")
    returned_entry = fields.Many2one('account.move', string="Returned Entry")
    
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                    domain="[('type','=','bank')]")
    
    
    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        result = {}
        if self.payment_type == "inbound":
            result = {'domain': {'journal_id': [('pdc_type','=','pdc_received')]}} 
        if self.payment_type == "outbound":
            result = {'domain': {'journal_id': [('pdc_type','=','pdc_issued')]}}
        return result

    

    @api.onchange('communication')
    def _onchange_communication(self):
        self.invoice_ids.ref = self.communication

    @api.model
    def create(self, vals):
        self._cr.execute("ALTER TABLE sr_pdc_payment DROP CONSTRAINT IF EXISTS sr_pdc_payment_unique_cheque_ref")
        res = super(PdcPayment, self).create(vals)

        return res

    @api.onchange('journal_id')
    def _default_currency(self):
        if self.journal_id:
            journal = self.journal_id
            currency_id = journal.currency_id or journal.company_id.currency_id or self.env.user.company_id.currency_id
            self.currency_id = currency_id.id
        else:
            self.currency_id = False

    @api.model
    def default_get(self, default_fields):
        rec = super(PdcPayment, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.move':
            return rec

        invoices = self.env['account.move'].browse(active_ids).filtered(
            lambda move: move.is_invoice(include_receipts=True))
        lines = invoices.line_ids

        # Check all invoices are open
        if not invoices or any(invoice.state != 'posted' for invoice in invoices):
            raise UserError(_("You can only register payments for open invoices"))
        # Check if, in batch payments, there are not negative invoices and positive invoices
        dtype = invoices[0].move_type
        for inv in invoices[1:]:
            if inv.move_type != dtype:
                if ((dtype == 'in_refund' and inv.move_type == 'in_invoice') or
                        (dtype == 'in_invoice' and inv.move_type == 'in_refund')):
                    raise UserError(_(
                        "You cannot register Post dated cheques for vendor bills and supplier refunds at the same time."))
                if ((dtype == 'out_refund' and inv.move_type == 'out_invoice') or
                        (dtype == 'out_invoice' and inv.move_type == 'out_refund')):
                    raise UserError(_(
                        "You cannot register Post dated cheques for customer invoices and credit notes at the same time."))
        # amount = self.env['account.payment']._compute_payment_amount(invoices, invoices[0].currency_id, invoices[0].journal_id, rec.get('payment_date') or fields.Date.today())
        amount = sum(lines.mapped('amount_residual'))
        rec.update({
            'currency_id': invoices[0].currency_id.id,
            'amount': abs(amount),
            'payment_type': 'inbound' if amount > 0 else 'outbound',
            'partner_id': invoices[0].commercial_partner_id.id,
            'communication': invoices[0].payment_reference or invoices[0].ref or invoices[0].name,
            'invoice_ids': [(6, 0, invoices.ids)],
        })
        return rec

    def cancel(self):
        self.state = 'cancel'

    def register(self):
        inv = self.env['account.move'].browse(self._context.get('active_ids'))
        # if inv:
        #     inv.amount_residual -= self.amount
        if self.payment_type == 'inbound':
            self.name = self.env['ir.sequence'].next_by_code('pdc.payment')
        else:
            self.name = self.env['ir.sequence'].next_by_code('pdc.payment.vendor')

        if self.journal_id.default_account_id:
            inv = self.invoice_ids
            AccountMove = self.env['account.move'].with_context(default_type='entry')
            aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
            if self.payment_type == 'inbound':
                account_id = self.partner_id.property_account_receivable_id.id
            else:
                account_id = self.partner_id.property_account_payable_id.id
            if inv:
                # inv.state = 'paid'
                custom_currency_id = inv.currency_id
                company_currency_id = inv.company_id.currency_id
                # account_id = inv.account_id.id
            else:
                custom_currency_id = self.currency_id
                company_currency_id = self.env.user.company_id.currency_id
            if self.currency_id != self.env.user.company_id.currency_id:
                balance = self.currency_id._convert(self.amount, company_currency_id, self.env.user.company_id,
                                                    self.due_date)
            else:
                balance = self.amount
            name = ''
            if self.invoice_ids:
                name += 'Registered PDC Payment: '
                for record in self.invoice_ids:
                    if record.line_ids:
                        name += record.name + ', '
                name = name[:len(name) - 2]
            pdc_credit_account_id = False
            pdc_debit_account_id = False
            if self.payment_type == 'inbound':
                pdc_credit_account_id = account_id
                pdc_debit_account_id = self.journal_id.default_account_id.id
            else:
                pdc_credit_account_id = self.journal_id.default_account_id.id
                pdc_debit_account_id = account_id
            if self.env.user.company_id.currency_id != self.currency_id:
                amount_currency = self.amount
            else:
                amount_currency = 0.0
            move_vals = {
                'date': self.payment_date,
                'ref': self.communication,
                'journal_id': self.journal_id.id,
                'currency_id': self.journal_id.currency_id.id or self.currency_id.id,
                'partner_id': self.partner_id.id,
                'pdc_ref_id': self.id,
                'line_ids': [
                    (0, 0, {
                        'name': name,
                        'amount_currency': amount_currency,
                        'currency_id': self.currency_id.id if self.env.user.company_id.currency_id != self.currency_id else False,
                        'debit': 0.0,
                        'credit': balance,
                        'date_maturity': self.due_date,
                        'partner_id': self.partner_id.id,
                        'account_id': pdc_credit_account_id,
                    }),
                    (0, 0, {
                        'name': name,
                        'amount_currency': -amount_currency,
                        'currency_id': self.currency_id.id if self.env.user.company_id.currency_id != self.currency_id else False,
                        'debit': balance,
                        'credit': 0.0,
                        'date_maturity': self.due_date,
                        'partner_id': self.partner_id.id,
                        'account_id': pdc_debit_account_id,
                    }),
                ],
            }
            move = AccountMove.create(move_vals)
            # FIXME : reconcile with invoice
            move.action_post()
            domain = [('account_internal_type', 'in', (
                'receivable', 'payable')), ('reconciled', '=', False)]
            lines = move.line_ids

            inv_lines = inv.line_ids.filtered_domain(domain)
            for account in inv_lines.account_id:
                (inv_lines + lines).filtered_domain(
                    [('account_id', '=', account.id),
                     ('reconciled', '=', False)]).reconcile()
            self.returned_entry = move
            if self.state == 'register':
                self.registered_deposit_entry = move
        else:
            raise UserError(_("Configuration Error: Please define account for the PDC payment."))
        self.state = 'register'

        return

    def return_cheque(self):
        if self.returned_entry:
            reversed_entry_wizard = self.env['account.move.reversal'].with_context(
                active_model='account.move', active_ids=self.returned_entry.ids).create({
                'reason': 'Registered Entry',
                'journal_id': self.journal_id.id,
                'date': self.return_date,
                # 'pdc_ref_id': self.id,
            })
            res = reversed_entry_wizard.reverse_moves()
            reversed_entry = self.env['account.move'].browse(res['res_id'])
            reversed_entry.pdc_ref_id = self.id

        self.state = 'return'
        return True

    def deposit(self):
        if self.deposit_journal_id:
            if self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account') and self.env[
                'ir.config_parameter'].sudo().get_param('vendor_pdc_payment_account'):
                print('testtt')
                inv = self.invoice_ids
                AccountMove = self.env['account.move'].with_context(default_type='entry')
                aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
                # if self.payment_type == 'inbound':
                account_id = self.journal_id.default_account_id.id
                # else:
                #     account_id = self.partner_id.property_account_payable_id.id
                if inv:
                    # inv.state = 'paid'
                    custom_currency_id = inv.currency_id
                    company_currency_id = inv.company_id.currency_id
                    # account_id = inv.account_id.id
                else:
                    custom_currency_id = self.currency_id
                    company_currency_id = self.env.user.company_id.currency_id
                if self.currency_id != self.env.user.company_id.currency_id:
                    balance = self.currency_id._convert(self.amount, company_currency_id, self.env.user.company_id,
                                                        self.deposit_date)
                else:
                    balance = self.amount
                name = ''
                if self.invoice_ids:
                    name += 'PDC Payment: '
                    for record in self.invoice_ids:
                        if record.line_ids:
                            name += record.name + ', '
                    name = name[:len(name) - 2]
                pdc_credit_account_id = False
                pdc_debit_account_id = False
                if self.payment_type == 'inbound':
                    pdc_credit_account_id = account_id
                    pdc_debit_account_id = int(
                        self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account'))
                else:
                    pdc_credit_account_id = int(
                        self.env['ir.config_parameter'].sudo().get_param('vendor_pdc_payment_account'))
                    pdc_debit_account_id = account_id
                if self.env.user.company_id.currency_id != self.currency_id:
                    amount_currency = self.amount
                else:
                    amount_currency = 0.0
                move_vals = {
                    'date': self.deposit_date,
                    'ref': self.communication,
                    'journal_id': self.journal_id.id,
                    'currency_id': self.journal_id.currency_id.id or self.currency_id.id,
                    'partner_id': self.partner_id.id,
                    'pdc_ref_id': self.id,
                    'line_ids': [
                        (0, 0, {
                            'name': name,
                            'amount_currency': amount_currency,
                            'currency_id': self.currency_id.id if self.env.user.company_id.currency_id != self.currency_id else False,
                            'debit': 0.0,
                            'credit': balance,
                            'date_maturity': self.deposit_date,
                            'partner_id': self.partner_id.id,
                            'account_id': pdc_credit_account_id,
                        }),
                        (0, 0, {
                            'name': name,
                            'amount_currency': -amount_currency,
                            'currency_id': self.currency_id.id if self.env.user.company_id.currency_id != self.currency_id else False,
                            'debit': balance,
                            'credit': 0.0,
                            'date_maturity': self.deposit_date,
                            'partner_id': self.partner_id.id,
                            'account_id': pdc_debit_account_id,
                        }),
                    ],
                }
                move = AccountMove.create(move_vals)
                # FIXME : reconcile with invoice
                move.action_post()
                domain = [('account_internal_type', 'in', (
                    'receivable', 'payable')), ('reconciled', '=', False)]
                lines = move.line_ids

                inv_lines = inv.line_ids.filtered_domain(domain)
                for account in inv_lines.account_id:
                    (inv_lines + lines).filtered_domain(
                        [('account_id', '=', account.id),
                        ('reconciled', '=', False)]).reconcile()
                if self.state == 'register':
                    self.registered_deposit_entry = move
            else:
                raise UserError(_("Configuration Error: Please define account for the PDC payment."))
            self.state = 'deposit'
            return True
        else:
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': ('Required Field'),
                    'message': '- You Should Fill (Bank Journal).',
                    'type':'danger',  #types: success,warning,danger,info
                    'sticky': False,  
                },
            }
            return notification
            # msg = 'You Should Fill Bank Journal Fields.'
            # raise UserError(msg)
        

    def done(self):
        if self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account') and self.env[
            'ir.config_parameter'].sudo().get_param('vendor_pdc_payment_account'):
            aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
            AccountMove = self.env['account.move'].with_context(default_type='entry')

            company_currency_id = self.env.user.company_id.currency_id
            if self.currency_id != self.env.user.company_id.currency_id:
                balance = self.currency_id._convert(self.amount, company_currency_id, self.env.user.company_id,
                                                    self.due_date)
            else:
                balance = self.amount
            account_id = self.deposit_journal_id.default_account_id.id
            name = ''
            if self.invoice_ids:
                name += 'PDC Payment: '
                for record in self.invoice_ids:
                    if record.line_ids:
                        name += record.name + ', '
                name = name[:len(name) - 2]
            if self.payment_type == 'inbound':
                pdc_debit_account_id = account_id
                pdc_credit_account_id = int(
                    self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account'))
            else:
                pdc_credit_account_id = account_id
                pdc_debit_account_id = int(
                    self.env['ir.config_parameter'].sudo().get_param('vendor_pdc_payment_account'))
            if self.env.user.company_id.currency_id != self.currency_id:
                amount_currency = self.amount
            else:
                amount_currency = 0.0
            move_vals = {
                'date': self.due_date,
                'ref': self.communication,
                'journal_id': self.journal_id.id,
                'currency_id': self.journal_id.currency_id.id or self.currency_id.id,
                'partner_id': self.partner_id.id,
                'pdc_ref_id': self.id,
                'line_ids': [
                    (0, 0, {
                        'name': name,
                        'amount_currency': amount_currency,
                        'currency_id': self.currency_id.id if self.env.user.company_id.currency_id != self.currency_id else False,
                        'debit': 0.0,
                        'credit': balance,
                        'date_maturity': self.due_date,
                        'partner_id': self.partner_id.id,
                        'account_id': pdc_credit_account_id,
                    }),
                    (0, 0, {
                        'name': name,
                        'amount_currency': -amount_currency,
                        'currency_id': self.currency_id.id if self.env.user.company_id.currency_id != self.currency_id else False,
                        'debit': balance,
                        'credit': 0.0,
                        'date_maturity': self.due_date,
                        'partner_id': self.partner_id.id,
                        'account_id': pdc_debit_account_id,
                    }),
                ],
            }
            move = AccountMove.create(move_vals)
            move.action_post()
            self.state = 'done'
        #             if self.invoice_ids:
        #                 (move + self.invoice_ids).line_ids \
        #                     .filtered(lambda line: not line.reconciled and (line.account_id.id == int(self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account')) or line.account_id.id == self.partner_id.property_account_receivable_id.id) )\
        #                     .reconcile()
        #             for record in self.invoice_ids:
        #                 record.payment_state = 'paid'
        else:
            raise UserError(_("Configuration Error: Please define account for the PDC payment."))
        return True

    def bounce(self):
        if self.registered_deposit_entry:
            reversed_entry_wizard = self.env['account.move.reversal'].with_context(
                active_model='account.move', active_ids=self.registered_deposit_entry.ids).create({
                'date': self.bounce_date,
                'reason': 'Reverse Entry',
                'journal_id': self.journal_id.id,
            })
            res = reversed_entry_wizard.reverse_moves()
            reversed_entry = self.env['account.move'].browse(res['res_id'])
            reversed_entry.pdc_ref_id = self.id
            if self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account') and self.env['ir.config_parameter'].sudo().get_param('vendor_pdc_payment_account'):
                if self.payment_type == 'inbound':
                    account_id = self.partner_id.property_account_receivable_id.id
                else:
                    account_id = self.partner_id.property_account_payable_id.id
                aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
                AccountMove = self.env['account.move'].with_context(default_type='entry')
                company_currency_id = self.env.user.company_id.currency_id
                if self.currency_id != self.env.user.company_id.currency_id:
                    balance = self.currency_id._convert(self.amount, company_currency_id, self.env.user.company_id, self.due_date)
                else:
                    balance = self.amount
                name = ''
                if self.invoice_ids:
                    name += 'PDC Payment: '
                    for record in self.invoice_ids:
                        if record.line_ids:
                            name += record.name + ', '
                    name = name[:len(name) - 2]
                # if self.payment_type == 'inbound':
                #     pdc_debit_account_id = account_id
                #     pdc_credit_account_id = int(self.env['ir.config_parameter'].sudo().get_param('customer_pdc_payment_account'))
                # else:
                #     pdc_credit_account_id = account_id
                #     pdc_debit_account_id = int(self.env['ir.config_parameter'].sudo().get_param('vendor_pdc_payment_account'))
                # if self.env.user.company_id.currency_id != self.currency_id:
                #     amount_currency = self.amount
                # else:
                #     amount_currency = 0.0
                # move_vals = {
                #     'date': self.bounce_date,
                #     'ref': self.communication,
                #     'journal_id': self.journal_id.id,
                #     'currency_id': self.journal_id.currency_id.id or self.currency_id.id,
                #     'partner_id': self.partner_id.id,
                #     'pdc_ref_id': self.id,
                #     'line_ids': [
                #         (0, 0, {
                #             'name': name,
                #             'amount_currency': amount_currency,
                #             'currency_id': self.currency_id.id if self.env.user.company_id.currency_id != self.currency_id else False,
                #             'debit': 0.0,
                #             'credit': balance ,
                #             'date_maturity': self.bounce_date,
                #             'partner_id': self.partner_id.id,
                #             'account_id': pdc_credit_account_id,
                #         }),
                #         (0, 0, {
                #             'name': name,
                #             'amount_currency': -amount_currency,
                #             'currency_id': self.currency_id.id if self.env.user.company_id.currency_id != self.currency_id else False,
                #             'debit': balance,
                #             'credit': 0.0,
                #             'date_maturity': self.bounce_date,
                #             'partner_id': self.partner_id.id,
                #             'account_id': pdc_debit_account_id,
                #         }),
                #     ],
                # }
                # move = AccountMove.create(move_vals)
                # move.action_post()
            self.state = 'bounce'
            for record in self.invoice_ids:
                record.amount_residual = record.amount_total
        else:
            raise UserError(_("Configuration Error: Please define account for the PDC payment."))
        return True

    def open_entries_view(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("PDC Entries"),
            'res_model': 'account.move',
            'view_mode': 'form',
            'domain': [('pdc_ref_id', '=', self.id), ('move_type', '=', 'entry')],
            'views': [(self.env.ref('account.view_move_tree').id, 'tree'), (False, 'form')],
        }

    def open_invoice_view(self):
        return self.env['account.move'] \
            .with_context(active_ids=self.ids, active_model='sr.pdc.payment', active_id=self.id) \
            .action_opening_invoice()
    
    def open_bill_view(self):
        return self.env['account.move'] \
            .with_context(active_ids=self.ids, active_model='sr.pdc.payment', active_id=self.id) \
            .action_opening_invoice()

    @api.ondelete(at_uninstall=False)
    def _unlink_if_draft(self):
        if self.state != 'draft':
            raise ValidationError(_(f"You can't delete {self.name} ,because it is not in draft state."))

    def action_register_payment(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''

        return {
            'name': _('PDC Payment'),
            'res_model': 'sr.pdc.payment',
            'view_mode': 'form',
            'view_id': self.env.ref('sr_pdc_management.sr_view_pdc_payment_invoice_view').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
