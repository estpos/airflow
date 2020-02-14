# -*- coding: utf-8 -*-

{
    'name': 'Product Bundle Pack',
    'category': 'Sales',
    'author': 'Browseinfo',
    'version': '12',
    'depends': [
        'sale',
        'product',
        'sale_management'
    ],
    'data': [
        'views/product_view.xml',

        'wizard/product_bundle_wizard_view.xml',

        'security/ir.model.access.csv'
    ],
    'summary': '''
       Combine two or more products together in order to create a bundle product.''',

    'description': '''
Product Bundle Pack
===================
This module is use to create Product Bundle,Product Pack, Bundle Pack of Product, 
Combined Product pack. Product Pack, Custom Combo Product, Bundle Product. 
Customized product, Group product. Custom product bundle. Custom Product Pack. 
Pack Price, Bundle price, Bundle Discount, Bundle Offer.
''',
}
