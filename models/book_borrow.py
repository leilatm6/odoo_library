from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import UserError

class BookBorrow(models.Model):
    _name = 'book.borrow'
    _description = 'Book Borrow'

    LOAN_PERIOD_DAYS = 14

    book_id = fields.Many2one('book.property', string='Book',required=True)
    borrower_id = fields.Many2one('res.users', string='Borrower',required=True)
    borrow_date = fields.Date(string='Borrow Date', default=fields.Date.today)
    due_date = fields.Date(string='Due Date', readonly=True, copy=False)
    return_date = fields.Date(string='Return Date')
    state = fields.Selection([("new", "New"), ("borrowed", "Borrowed"), ("returned", "Returned")], string='State', default='new')

    def _get_due_date(self, borrow_date):
        return borrow_date + timedelta(days=self.LOAN_PERIOD_DAYS) if borrow_date else False

    @api.onchange('borrow_date')
    def _onchange_borrow_date(self):
        for record in self:
            if record.borrow_date:
                record.due_date = record._get_due_date(record.borrow_date)

    def borrow_book(self):
        for record in self:
            if record.state == 'borrowed':
                raise UserError("This borrow record is already confirmed.")

            if record.book_id.available_copies <= 0:
                raise UserError("There are no available copies of this book.")

            if record.borrower_id.borrowed_book_ids.filtered(lambda b: b.state == 'borrowed'):
                raise UserError("This borrower already has a borrowed book. Please return it before borrowing another one.")

            if not record.borrow_date:
                record.borrow_date = fields.Date.today()
            record.due_date = record._get_due_date(record.borrow_date)
            record.state = 'borrowed'

    def write(self, vals):
        if vals.get('borrow_date') and 'due_date' not in vals:
            vals['due_date'] = self._get_due_date(fields.Date.to_date(vals['borrow_date']))
        return super().write(vals)

    def return_book(self):
        for record in self:
            if record.state != 'borrowed':
                raise UserError("Only borrowed books can be returned.")

            if not record.return_date:
                record.return_date = fields.Date.today()
            record.state = 'returned'
