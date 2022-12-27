{
    'name': 'CRM Partner Status',
    'version': '14.0.1.0.0',
    'category': 'CRM',
    'description': u"""
Partner Status in CRM
""",
    'author': 'Serincloud',
    'depends': [
        'crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
}
