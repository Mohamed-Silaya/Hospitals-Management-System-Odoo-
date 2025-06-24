from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
import logging
_logger = logging.getLogger(__name__)
class Patient(models.Model):
    _name = 'hms.patient'
    _inherit = ['mail.thread']
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
    email = fields.Char(string='Email', required=True)

    department_id = fields.Many2one('hms.department')
    department_capacity = fields.Integer(related='department_id.capacity', readonly=True)
    doctor_ids = fields.Many2many('hms.doctor')
    state = fields.Selection([
        ('undetermined', 'Undetermined'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('serious', 'Serious')
    ], default='undetermined')
    log_history_ids = fields.One2many(
        'patient.log.history',
        'patient_id',
        string='Log History'
    )

    @api.constrains('email')
    def _check_valid_email(self):
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError("Invalid email address: %s" % record.email)

    _sql_constraints = [
        ('email_unique', 'UNIQUE(email)', 'Email address must be unique.')
    ]

    @api.depends('birth_date')
    def _compute_age(self):
        for rec in self:
            _logger.info(f"Computing age for {rec.id}, birth_date: {rec.birth_date}")
            if rec.birth_date:
                today = date.today()
                age = today.year - rec.birth_date.year
                if (today.month, today.day) < (rec.birth_date.month, rec.birth_date.day):
                    age -= 1
                rec.age = age
                _logger.info(f"Computed age: {rec.age}")
            else:
                rec.age = 0
                _logger.info("No birth_date, age set to 0")

    @api.onchange('birth_date', 'pcr')
    def _onchange_birth_date(self):
        if self.birth_date and self.age < 30:
            if not self.pcr:
                self.pcr = True
                return {
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

    ########################### handle logs

    def _create_log(self, description):
        self.ensure_one()
        try:
            _logger.info(f"Creating log for patient {self.id}: {description}")
            return self.env['patient.log.history'].create({
                'patient_id': self.id,
                'description': description,
            })
        except Exception as e:
            _logger.error(f"Failed to create log for patient {self.id}: {e}")

    @api.model
    def create(self, vals):
        record = super(Patient, self).create(vals)
        if 'state' in vals:
            _logger.info(f"State in vals during create: {vals['state']}")
            record._create_log('State set to {}'.format(vals['state']))
        return record

    def write(self, vals):
        if 'state' in vals:
            for record in self:
                _logger.info(f"State in vals during write: {vals['state']}")
                record._create_log('State changed to {}'.format(vals['state']))
        return super(Patient, self).write(vals)