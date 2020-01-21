# -*- coding: utf-8 -*-

{
    'name': 'Airflow Import Module',
    'version': '1.0',
    'author': u'EST-POS OÜ',
    'website': 'https://estpos.ee',
    'category': 'Sales',
    'depends': [
        'base',
        'stock',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/airflow_import_views.xml',
    ],

    'description': u'''
Import module for sale history.
''',
}
