from odoo import _, api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    partner_status_id = fields.Many2one('partner.status', related='partner_id.status_id', store=True)
    is_prospection = fields.Boolean('Prospection', related='partner_status_id.is_prospection')

