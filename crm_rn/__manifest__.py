{
    'name': 'CRM Roldán Netya',
    'version': '14.0.1.0.0',
    'category': 'CRM',
    'description': u"""
Objetivos y seguimiento mensual Roldán Netya
""",
    'author': 'Serincloud',
    'depends': [
        'crm',
        'partner_status',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/objetivo_anual_views.xml',
        'views/crm_stage_views.xml',
        'views/objetivo_mensual_views.xml',
        'views/objetivo_grupo_views.xml',
        'views/objetivo_anual_linea_views.xml',
        'views/objetivo_mensual_linea_views.xml',
        'views/objetivo_equipo_views.xml',
        'views/crm_lead_views.xml',
        'views/res_users_views.xml',
        'views/menu_views.xml',
        'data/server_action.xml',
        'data/automated_action.xml',
    ],
    'installable': True,
}
