from odoo import _, api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    partner_status = fields.Many2one('partner.status', related='partner_id.status', store=True)
    is_prospection = fields.Boolean('Prospection', related='partner_status.is_prospection')

