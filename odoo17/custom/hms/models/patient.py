from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class Patient(models.Model):
    _name = 'hms.patient'
    _description = 'Patient Record'

    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    birth_date = fields.Date()
    history = fields.Html()
    cr_ratio = fields.Float()
    blood_type = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ])
    pcr = fields.Boolean(string="PCR Required")
    image = fields.Binary(attachment=True)
    address = fields.Text()
    age = fields.Integer(compute="_compute_age", store=True)

    department_id = fields.Many2one('hms.department')
    department_capacity = fields.Integer(related='department_id.capacity', readonly=True)
    doctor_ids = fields.Many2many('hms.doctor')
    state = fields.Selection([
        ('undetermined', 'Undetermined'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('serious', 'Serious')
    ], default='undetermined')

    @api.onchange('birth_date','pcr')
    def _compute_age(self):
        for rec in self:
            if rec.birth_date:
                today = date.today()
                rec.age = today.year - rec.birth_date.year - (
                    (today.month, today.day) < (rec.birth_date.month, rec.birth_date.day)
                )
                if rec.age < 30:
                    if not self.pcr:
                        self.pcr = True
                    return {
                        'value': {'pcr': True},
                        'domain': {},
                        'warning': {
                            'title': "PCR Locked",
                            'message': "PCR cannot be unchecked for patients under 30 years old.",
                        }
                    }

@api.constrains('pcr', 'cr_ratio')
def _check_cr_ratio_required(self):
    for rec in self:
        if rec.pcr and not rec.cr_ratio:
            raise ValidationError("CR Ratio is required when PCR is checked")