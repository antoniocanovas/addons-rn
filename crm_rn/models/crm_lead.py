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

    @api.depends('stage_id','user_id')
    def _get_cambios_de_etapa(self):
        for record in self:
            fechas_unicas_por_oportunidad, cambio_por_dia_y_oportunidad = [], ""

            cambiosdeetapa = self.env['mail.tracking.value'].search([('field', '=', 'stage_id'),
                                                                     ('new_value_char', '!=', False),
                                                                     ('mail_message_id.model', '=', 'crm.lead'),
                                                                     ('mail_message_id.res_id', '=', record.id),
                                                                     ('write_uid', '=', record.user_id.id)])
            for li in cambiosdeetapa:
                cambio_por_dia_y_oportunidad = str(li.mail_message_id.res_id) + str(li.create_date.date())
                if (cambio_por_dia_y_oportunidad not in fechas_unicas_por_oportunidad):
                    fechas_unicas_por_oportunidad.append(cambio_por_dia_y_oportunidad)
            record['cambio_etapa_count'] = len(fechas_unicas_por_oportunidad)
    cambio_etapa_count = fields.Integer('Cambios de etapa', readonly=1, store=True, compute='_get_cambios_de_etapa')

    @api.depends('stage_id','user_id')
    def _get_cambios_de_etapa_date(self):
        for record in self:
            record['cambio_etapa_date'] = datetime.today().date()
    cambio_etapa_date = fields.Date('Último cambio de etapa', readonly=1, store=True, compute='_get_cambios_de_etapa_date')
