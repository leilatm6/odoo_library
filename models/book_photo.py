
from odoo import models, fields, api
 
 
class BookPhoto(models.Model):
    _name = 'book.photo'
    _description = 'Book Photo Gallery'
    _order = 'sequence, id'
 
    book_id = fields.Many2one(
        'book.property',
        string='Book',
        required=True,
        ondelete='cascade'
    )
    
    name = fields.Char(
        string='Photo Name',
    )
    
    photo = fields.Image(
        string='Photo',
        required=True,
        max_width=1920,
        max_height=1920,
        help='Upload book photo (JPG, PNG, GIF supported)'
    )
    
    description = fields.Text(
        string='Description',
        help='Photo description or notes'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of display in gallery'
    )
    
    uploaded_date = fields.Datetime(
        string='Uploaded Date',
        default=fields.Datetime.now,
        readonly=True
    )
    
    photo_type = fields.Selection(
        [
            ('cover', 'Book Cover'),
            ('interior', 'Interior Page'),
            ('spine', 'Book Spine'),
            ('back', 'Back Cover'),
            ('toc', 'Table of Contents'),
            ('preview', 'Preview'),
            ('other', 'Other')
        ],
        string='Photo Type',
        default='other',
        help='Categorize the type of photo'
    )
    
    @api.onchange('photo')
    def _on_change_photo(self):
        if self.photo and not self.name and self.book_id:
            photo_num = len(self.book_id.photo_ids) + 1
            self.name = f"{self.book_id.title} - Photo {photo_num}"