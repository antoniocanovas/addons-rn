from odoo import _, api, fields, models
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class ObjetivoMensualLinea(models.Model):
    _name = 'objetivo.mensual.linea'
    _description = 'Objetivo anual Líneas'


    name = fields.Char('Name')
    active = fields.Boolean('Activo', store=True, readonly=True, related='oportunidad_id.active')
    currency_id = fields.Many2one('res.currency', default=1)
    cliente_id = fields.Many2one('res.partner', string="Cliente", related='oportunidad_id.partner_id')
    comercial_id = fields.Many2one('res.users', string="Comercial", store=True, readonly=True)
    equipo_id = fields.Many2one('crm.team', string="Equipo de ventas", related='comercial_id.sale_team_id', store=True, readonly=True)
    es_cuenta_nueva = fields.Boolean('Prospección', store=True, readonly=True,
                                     help='En el momento de crear la oportunidad, esta cuenta estaba marcada como "Prospección", '
                                          'es posible que en actualmente este estado haya cambiado manualmente porque ya se le ha vendido algo, '
                                          'pero el sistema guarda la información histórica que es la interesante.')
    es_nueva = fields.Boolean('Es nueva', store=True, readonly=True)
    es_objetivo = fields.Boolean('Es objetivo', store=True, readonly=True)
    es_perdida = fields.Boolean('Es perdida', store=True, readonly=True)
    etapa_id = fields.Many2one('crm.stage', string='Etapa')
    importe = fields.Monetary('Importe')
    objetivo_equipo_id = fields.Many2one('objetivo.equipo', string='Obj. Equipo venta', store=True, readonly=True,
                                         related='objetivo_mensual_id.objetivo_equipo_id')
    objetivo_mensual_id = fields.Many2one('objetivo.mensual', string='Obj. mensual')
    oportunidad_id = fields.Many2one('crm.lead', string='Oportunidad', store=True, readonly=True)
