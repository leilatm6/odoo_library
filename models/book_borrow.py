from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta   


class BookBorrow(models.Model):
    _name = 'book.borrow'
    _description = 'Book Borrow'

    LOAN_PERIOD_DAYS = 14 

    display_name = fields.Char(compute='_compute_display_name')

    book_id = fields.Many2one('book.property', string='Book', required=True)
    borrower_id = fields.Many2one(
        'res.users',
        string='Borrower',
        required=True,
        default=lambda self: self.env.user
    )
    borrow_date = fields.Date(string='Borrow Date')
    return_date = fields.Date(string='Return Date')
    due_date = fields.Date(string='Due Date', compute='_compute_due_date', store=True)



    state = fields.Selection([
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
    ], string='State')

    fine_ids = fields.One2many('library.fine', 'book_borrow_id', string='Fines')
    has_fine = fields.Boolean(compute='_compute_has_fine')

    @api.depends('fine_ids')
    def _compute_has_fine(self):
        for record in self:
            record.has_fine = bool(record.fine_ids)


    def borrow_book(self):
        for record in self:
            if record.state == 'borrowed':
                raise UserError("This book is already borrowed.")

            if record.book_id.available_copies <= 0:
                raise UserError("There are no available copies of this book.")

            if record.borrower_id.available_borrows <= 0:
                raise UserError(
                    f"{record.borrower_id.name} has reached the maximum of "
                    f"{record.borrower_id.max_books} borrowed books."
                )

            if not record.borrow_date:
                record.borrow_date = fields.Date.today()
            record.state = 'borrowed'
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def return_book(self):
        for record in self:
            if record.state != 'borrowed':
                raise UserError("Only borrowed books can be returned.")

            if not record.return_date:
                record.return_date = fields.Date.today()
            record.state = 'returned'

            if record.due_date and record.return_date > record.due_date:
                self.env['library.fine'].create({
                    'book_borrow_id': record.id,
                })

        return {'type': 'ir.actions.client', 'tag': 'reload'}
    

    @api.depends('borrow_date')
    def _compute_due_date(self):
        for record in self:
            record.due_date = (
                record.borrow_date + timedelta(days=self.LOAN_PERIOD_DAYS)
                if record.borrow_date else False
        )
            

    def action_view_fine(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fine',
            'res_model': 'library.fine',
            'view_mode': 'form',
            'res_id': self.fine_ids[0].id,
            'target': 'new',
        }
    
    @api.depends('book_id.title', 'borrower_id.name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.book_id.title or ''} — {record.borrower_id.name or ''}"

    @api.constrains('state', 'book_id', 'borrower_id')
    def _check_duplicate_borrow(self):
        for record in self:
            if record.state == 'borrowed':
                duplicate = self.search_count([
                    ('id', '!=', record.id),
                    ('book_id', '=', record.book_id.id),
                    ('borrower_id', '=', record.borrower_id.id),
                    ('state', '=', 'borrowed'),
                ])
                if duplicate:
                    raise UserError("This borrower already has this book borrowed.")