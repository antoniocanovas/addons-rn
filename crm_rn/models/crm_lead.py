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
            # Actualizar campo 'x_estado' que en enterprise es 'won_status'. Corrección 21/09/20:
            # if (record.active == False) and (record.probability == 0) and (record.x_estado != 'lost'):
            if (record.probability == 0) and (record.estado != 'lost') and (record.type == 'opportunity'):
                record['estado'] = 'lost'
            # elif (record.active == True) and (record.probability == 100) and (record.x_estado != 'won'):
            elif (record.probability == 100) and (record.estado != 'won') and (record.type == 'opportunity'):
                record['estado'] = 'won'
            elif (record.probability > 0) and (record.probability < 100) and (record.estado != 'pending') and (
                    record.type == 'opportunity'):
                record['estado'] = 'pending'
    estado = fields.Selection([('pending','En curso'),('won','Ganado'),('lost','Perdido')],
                              string='Estado', store=True, readonly=True, compute='_get_crm_estado')

    @api.depends('active')
    def _get_lead_es_perdida(self):
        for record in self:
            lost = False
            if record.active == False: lost = True
            record['es_perdida'] = lost
    es_perdida = fields.Boolean('Es perdida', store=True, compute=_get_lead_es_perdida)
