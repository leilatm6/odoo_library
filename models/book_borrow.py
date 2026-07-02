from odoo import models, fields, api
from odoo.exceptions import UserError


class BookBorrow(models.Model):
    _name = 'book.borrow'
    _description = 'Book Borrow'

    book_id = fields.Many2one('book.property', string='Book', required=True)
    borrower_id = fields.Many2one(
        'res.users',
        string='Borrower',
        required=True,
        default=lambda self: self.env.user
    )
    borrow_date = fields.Date(string='Borrow Date')
    return_date = fields.Date(string='Return Date')

    state = fields.Selection([
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
    ], string='State')


    def borrow_book(self):
        for record in self:
            if record.state == 'borrowed':
                raise UserError("This book is already borrowed.")

            if record.book_id.available_copies <= 0:
                raise UserError("There are no available copies of this book.")

            if record.borrower_id.borrowed_book_ids.filtered(lambda b: b.state == 'borrowed'):
                raise UserError(
                    "This borrower already has a borrowed book. Please return it first."
                )

            record.borrow_date = fields.Date.today()
            record.state = 'borrowed'

    def return_book(self):
        for record in self:
            if record.state != 'borrowed':
                raise UserError("Only borrowed books can be returned.")

            record.return_date = fields.Date.today()
            record.state = 'returned'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            book_id = vals.get('book_id')
            borrower_id = vals.get('borrower_id') or self.env.user.id

            existing = self.search([
                ('book_id', '=', book_id),
                ('borrower_id', '=', borrower_id),
                ('state', '=', 'borrowed'),
            ])

            if existing:
                raise UserError("This borrower already borrowed this book.")

        return super().create(vals_list)