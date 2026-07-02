from odoo import models, fields, api

class LibUsers(models.Model):
    _inherit = 'res.users'

    borrowed_book_ids = fields.One2many('book.borrow', 'borrower_id', string='Borrowed Books')

    max_books = fields.Integer(string="Maximum Books",default=5)

    