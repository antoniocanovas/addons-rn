{
    'name': 'CRM Partner Plan',
    'version': '14.0.1.0.0',
    'category': 'CRM',
    'description': u"""
Partner Plan in contacts and CRM Configuration
""",
    'author': 'Serincloud',
    'depends': [
        'crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/partner_plan_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
}
