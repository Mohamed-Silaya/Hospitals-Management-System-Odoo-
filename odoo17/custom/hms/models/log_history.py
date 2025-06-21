from odoo import models, fields, api

class PatientLogHistory(models.Model):
    _name = 'patient.log.history'
    _description = 'Patient Log History'
    _order = 'create_date desc'

    patient_id = fields.Many2one('hms.patient', required=True)
    #here we used lamda to be dynamic call to current user
    created_by = fields.Many2one('res.users', string="Created By", default=lambda self: self.env.user)
    create_date = fields.Datetime(string="Date", default=fields.Datetime.now)
    description = fields.Text(string="Description")