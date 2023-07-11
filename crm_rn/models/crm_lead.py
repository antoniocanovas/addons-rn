# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    vat   = fields.Char('NIF', related='partner_id.vat', readonly=False)

    @api.depends('stage_id')
    def _get_crm_estado(self):
        for record in self:
            if (record.probability == 0) and (record.estado != 'lost') and (record.type == 'opportunity'):
                estado = 'lost'
            elif (record.probability == 100) and (record.estado != 'won') and (record.type == 'opportunity'):
                estado = 'won'
            elif (record.probability > 0) and (record.probability < 100) and (record.type == 'opportunity'):
                estado = 'pending'
            self.estado = estado
    estado = fields.Selection([('pending','En curso'),('won','Ganado'),('lost','Perdido')],
                              string='Estado', store=True, readonly=True, compute='_get_crm_estado')

    @api.depends('active')
    def _get_lead_es_perdida(self):
        for record in self:
            lost = False
            if record.active == False: lost = True
            record['es_perdida'] = lost
    es_perdida = fields.Boolean('Es perdida', store=True, compute=_get_lead_es_perdida)
