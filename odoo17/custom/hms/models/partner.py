from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    related_patient_id = fields.Many2one('hms.patient', string='Related Patient')

    @api.constrains('related_patient_id', 'email')
    def _check_patient_email_unique(self):
        for record in self:
            if record.related_patient_id and record.related_patient_id.email:
                other_partners = self.env['res.partner'].search([
                    ('email', '=', record.related_patient_id.email),
                    ('id', '!=', record.id),
                ])
                if other_partners:
                    raise ValidationError(
                        "The email %s is already assigned to another customer." % record.related_patient_id.email
                    )

    @api.constrains('vat', 'customer_rank')
    def _check_vat_required(self):
        for record in self:
            if record.customer_rank > 0 and not record.vat:
                raise ValidationError("Tax ID is required for customers.")

    def unlink(self):
        for record in self:
            if record.related_patient_id:
                raise UserError(
                    "Cannot delete customer linked to patient: %s" % record.related_patient_id.name_get()[0][1])
        return super(ResPartner, self).unlink()