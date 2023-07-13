# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


import logging
import re

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'


    vat   = fields.Char('NIF', related='partner_id.vat', readonly=False)

    empresa_id = fields.Many2one('res.company', store=True, related='user_id.empresa_id')

    @api.depends('stage_id','probability')
    def _get_crm_estado(self):
        for record in self:
            if (record.probability == 0) and (record.type == 'opportunity'):
                estado = 'lost'
            elif (record.probability == 100) and (record.type == 'opportunity'):
                estado = 'won'
            elif (record.probability > 0) and (record.probability < 100) and (record.type == 'opportunity'):
                estado = 'pending'
            self.estado = estado
    estado = fields.Selection([('pending','En curso'),('won','Ganado'),('lost','Perdido')],
                              string='Estado', store=True, readonly=True, default='pending', compute='_get_crm_estado')

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

    def _get_objetivo_anual(self):
        for record in self:
            objetivo = False
            registros = self.env['objetivo.anual.linea'].search([('oportunidad_id', '=', record.id),
                                                                  ('objetivo_id.estado', '=', 'activo')])
            if registros.ids:
                primero = registros[0]
                objetivo = primero.objetivo_id.id
            record['objetivo_anual_id'] = objetivo
    objetivo_anual_id = fields.Many2one('objetivo.anual', string='Obj. Anual', store=False, compute='_get_objetivo_anual')

    @api.constrains('vat')
    def _check_valid_nif(self):
        # Se divide por 23 y el dígito de control es el de la lista:
        REGEXP = "[0-9]{8}[A-Z]"
        DIGITO_CONTROL = "TRWAGMYFPDXBNJZSQVHLCKE"
        INVALIDOS = {"00000000T", "00000001R", "99999999R"}
        vat = self.vat

        if self.vat in INVALIDOS:
            raise ValidationError('NIF no válido 1')
        if len(vat) != 9:
            raise ValidationError('Son 9 dígitos')
        if re.match(REGEXP, vat) is not None:
            raise ValidationError('NIF no válido 2')
        if self.vat[8] != DIGITO_CONTROL[int(self.vat[:8]) % 23]:
           raise ValidationError('NIF no válido3 ')
        raise ValidationError('NIF: ' + self.vat + " Números: " + str(self.vat[8]) + str(int(self.vat[:8]) % 23))