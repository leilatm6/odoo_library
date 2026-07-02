from odoo import models, fields, api

class BookPropertyType(models.Model):
    _name = 'book.property.type'
    _description = 'Book Property Type'

    name = fields.Char('Name', required=True)
     
    _check_name_unique = models.Constraint(
        "UNIQUE(name)", "Property type name must be unique."
    )   