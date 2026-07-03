{
    'name':'Library',
    'depends':['base','account'],
    'application':True,
    'data' : [
        'views/book_property_view.xml',
        "views/book_property_type_view.xml",
        "views/book_borrow_view.xml",
        "views/lib_users_view.xml",
        "views/book_photo_view.xml",
        "views/library_menus.xml",
        "views/library_fine_view.xml",
        'security/library_security.xml',
        'security/ir.model.access.csv',
    ]
}