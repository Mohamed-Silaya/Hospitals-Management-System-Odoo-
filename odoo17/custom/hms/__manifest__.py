{
    'name': 'Hospital Management System',
    'version': '1.0.0',
    'summary': 'Manage hospital patients',
    'description': 'Module for managing patient records in hospitals',
    'category': 'Healthcare',
    'author': 'Mohamed Silaya',
    'depends': ['base','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/actions.xml',
        'views/patient_views.xml',
        'views/department_views.xml',
        'views/doctor_views.xml',
        'views/menus.xml',

    ],
    'installable': True,
    'application': True,
}