""" Initialize Pdc Payment Wizard """

from email.policy import default
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning
from dateutil.relativedelta import relativedelta


class PdcPaymentWizard(models.TransientModel):
    """
        Initialize Pdc Payment Wizard:
    """
    _name = 'pdc.payment.wizard'
    _description = 'Pdc Payment Wizard'

    invoice_ids = fields.Many2many(
        'account.move', string="Invoices", copy=False, readonly=True
    )
    partner_id = fields.Many2one(
        'res.partner', string='Partner', required=True, copy=False)

    move_type = fields.Selection(related="invoice_ids.move_type", store=True)

    @api.onchange('move_type')
    def _onchange_payment_type(self):
        result = {}
        if self.move_type in ["out_invoice", "in_refund"]:
            result = {'domain': {'journal_id': ['&', ('type', 'in', ['bank']), ('pdc_type','=', 'pdc_received')] }} 
        if self.move_type in ["out_refund", "in_invoice"]:
            result = {'domain': {'journal_id': ['&', ('type', 'in', ['bank']), ('pdc_type','=', 'pdc_issued')] }}
        return result

    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True)
    
    company_id = fields.Many2one(
        'res.company', related='journal_id.company_id', string='Company', readonly=True
    )
    residual_amount = fields.Monetary(readonly=True)
    communication = fields.Char(string='Memo')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id
    )
    payment_type = fields.Selection(
        [('outbound', 'Send Money'), ('inbound', 'Receive Money')], string='Payment Type', required=True,
    )
    line_ids = fields.One2many(
        'pdc.payment.wizard.line', 'wizard_id',
    )
    batch_pdc = fields.Boolean('Batch PDC')
    amount = fields.Monetary(string='Total Amount')
    cheques_no = fields.Integer(string="Total No of Cheques", default="1")
    no_of_months = fields.Integer(string="No of months", default="1")

    first_cheque_date = fields.Date(string='First Cheque Date', default=fields.Date.context_today)
    first_cheque_ref = fields.Integer('First Cheque Ref')

    def create_pdc_cheques(self):
        if self.line_ids:
            for line in self.line_ids:
                self.line_ids = [(2, line.id)]
        for n in range(0, self.cheques_no):
            self.env["pdc.payment.wizard.line"].sudo().create(
                {
                    "amount": self.amount / self.cheques_no,
                    "wizard_id": self.id,
                    "journal_id": self.journal_id.id,
                    "due_date": self.first_cheque_date + relativedelta(months=n * self.no_of_months),
                    "cheque_ref": self.first_cheque_ref + n,
                    "communication": self.communication,
                }
            )
        # return {'type': 'ir.actions.act_window_close'}
        return {
            'context': self.env.context,
            'name': 'Pdc Payment Wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pdc.payment.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def register(self):
        pdc = self.env['sr.pdc.payment']
        vals = []
        for line in self.line_ids:
            vals.append({
                'invoice_ids': self.invoice_ids,
                'partner_id': self.partner_id.id,
                'journal_id': self.journal_id.id,
                'company_id': self.company_id.id,
                'amount': line.amount,
                'currency_id': self.currency_id.id,
                'payment_date': line.payment_date,
                'due_date': line.due_date,
                'communication': line.communication,
                'cheque_ref': line.cheque_ref,
                'agent': line.agent,
                'bank': line.bank.id,
                'name': line.name,
                'payment_type': self.payment_type,
            })
        records = pdc.create(vals)
        for rec in records:
            rec.register()

    @api.model
    def default_get(self, default_fields):
        rec = super(PdcPaymentWizard, self).default_get(default_fields)
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
        amount = sum(lines.mapped('amount_residual'))
        rec.update({
            'currency_id': invoices[0].currency_id.id,
            # 'flag': invoices[0].move_type,
            'residual_amount': abs(amount),
            'payment_type': 'inbound' if dtype in ['out_invoice', 'in_refund'] else 'outbound',
            'partner_id': invoices[0].commercial_partner_id.id,
            'communication': invoices[0].payment_reference or invoices[0].ref or invoices[0].name,
            'invoice_ids': [(6, 0, invoices.ids)],
        })
        return rec


class PdcPaymentWizardLine(models.TransientModel):
    """
        Initialize Pdc Payment Wizard Line:
    """
    _name = 'pdc.payment.wizard.line'
    _description = 'Pdc Payment Wizard Line'

    amount = fields.Monetary(string='Payment Amount', required=True)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    due_date = fields.Date(string='Due Date', default=fields.Date.context_today, required=True, copy=False)
    cheque_ref = fields.Char('Cheque Reference')
    agent = fields.Char('Agent')
    bank = fields.Many2one('res.bank', string="Bank")
    name = fields.Char('Name')
    wizard_id = fields.Many2one('pdc.payment.wizard')
    communication = fields.Char(string='Memo')
    company_id = fields.Many2one(
        'res.company', related='journal_id.company_id', string='Company', readonly=True
    )
     
    journal_id = fields.Many2one(
        'account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ['bank'])])
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id
    )
