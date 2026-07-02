from odoo import models, fields, api

class LibUsers(models.Model):
    _inherit = 'res.users'

    borrowed_book_ids = fields.One2many('book.borrow', 'borrower_id', string='Borrowed Books')

    max_books = fields.Integer(string="Maximum Books",default=5)

    available_borrows = fields.Integer(
        string="Available Borrows",
        compute="_compute_available_borrows",
        store=True,
    )

    @api.depends("max_books", "borrowed_book_ids.state")
    def _compute_available_borrows(self):
        for record in self:
            active = len(record.borrowed_book_ids.filtered(
                lambda b: b.state == 'borrowed'
            ))
            record.available_borrows = record.max_books - active