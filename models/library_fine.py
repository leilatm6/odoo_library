from odoo import models, fields, api
from odoo.exceptions import UserError

class LibraryFine(models.Model):
    _name = 'library.fine'
    _description = 'Book Fine'

    FINE_PER_DAY = 2.0 
    MAX_FINE_DAYS = 30

    book_borrow_id = fields.Many2one('book.borrow', string='Book Borrow', required=True)
    fine_amount = fields.Float(string='Fine Amount', compute='_compute_fine_amount', store=True)    
    user_id = fields.Many2one('res.users', string='User', related='book_borrow_id.borrower_id', store=True)

    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)
    state = fields.Selection([('unpaid', 'Unpaid'), ('paid', 'Paid')],
                         default='unpaid', string='State')
    
    @api.depends('book_borrow_id.return_date', 'book_borrow_id.due_date')
    def _compute_fine_amount(self):     
        for record in self:
            if record.book_borrow_id.return_date and record.book_borrow_id.due_date:
                overdue_days = (record.book_borrow_id.return_date - record.book_borrow_id.due_date).days
                if overdue_days > 0:
                    overdue_days = min(overdue_days, self.MAX_FINE_DAYS)
                    record.fine_amount = overdue_days * self.FINE_PER_DAY
                else:
                    record.fine_amount = 0.0
            else:
                record.fine_amount = 0.0

    def action_create_invoice(self):
        self.ensure_one()
        if self.invoice_id:
            raise UserError("An invoice already exists for this fine.")
        if not self.fine_amount:
            raise UserError("Cannot invoice a zero-amount fine.")

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.user_id.partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': f"Library fine: {self.book_borrow_id.book_id.title}",
                'quantity': 1,
                'price_unit': self.fine_amount,
            })],
        })
        self.invoice_id = invoice.id
        invoice.action_post()  
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fine Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
        }