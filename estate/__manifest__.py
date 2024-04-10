
{
    'name': 'Real Estate',
    'depends': [
        'base',
        'base_setup',
    ],
    'application': True,
    'installable': True,
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/estate_data.xml',
        'demo/estate_demo.xml',
        'demo/estate_offer_demo.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_menus.xml'
    ],
    'category': 'Real Estate/Brokerage',
}