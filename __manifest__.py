{
    'name':'Library',
    'depends':['base'],
    'application':True,
    'data' : [
        'views/book_property_view.xml',
        "views/book_property_type_view.xml",
        "views/book_borrow_view.xml",
        "views/lib_users_view.xml",
        "views/library_menus.xml",

        'security/library_security.xml',
        'security/ir.model.access.csv',
    ]
}