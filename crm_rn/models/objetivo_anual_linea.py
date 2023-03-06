from odoo import _, api, fields, models
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class ObjetivoAnualLinea(models.Model):
    _name = 'objetivo.anual.linea'
    _description = 'Objetivo anual Líneas'

    # Estos campos van en el módulo de facturación desde ERP:
    #    x_facturado  Incremento facturado
    #    x_facturado_op_ganada   Fact.Op.Ganadas

    name = fields.Char('Name')
    active = fields.Boolean('Activo', store=True, related='oportunidad_id.active')
    currency_id = fields.Many2one('res.currency', default=1)
    anho = fields.Integer('Año', store=True, related='objetivo_id.anho')
    objetivo_id = fields.Many2one('objetivo.anual', string='Objetivo anual', store=True, readonly=True)
    cliente_id = fields.Many2one('res.partner', string="Cliente")
    comercial_id = fields.Many2one('res.users', string="Comercial", store=True, readonly=True)
    equipo_id = fields.Many2one('crm.team', string="Equipo de ventas", related='comercial_id.sale_team_id', store=True, readonly=True)
    es_cuenta_nueva = fields.Boolean('Es cuenta nueva', store=True, readonly=True,
                                     help='En el momento de crear la oportunidad, esta cuenta estaba marcada como "Prospección", '
                                          'es posible que en actualmente este estado haya cambiado manualmente porque ya se le ha vendido algo, '
                                          'pero el sistema guarda la información histórica que es la interesante.')
    es_nueva = fields.Boolean('Es nueva', store=True, readonly=True)
    es_objetivo = fields.Boolean('Es objetivo', store=True, readonly=True)
    oportunidad_id = fields.Many2one('crm.lead', string='Oportunidad', store=True, readonly=True)
    es_perdida = fields.Boolean('Es perdida', store=True, readonly=True, related='oportunidad_id.es_perdida', help='Campo de control para mostrar en las líneas de análisis anual.')
    estado = fields.Selection('Estado Op.', store=True, readonly=True, related='oportunidad_id.estado')
    estado_actual_id = fields.Many2one('crm.stage', string="Última etapa", store=False, readonly=True, related='oportunidad_id.stage_id')
    estado_inicial_id = fields.Many2one('crm.stage', string="Estado inicial", store=True, readonly=True)
    importe_actual = fields.Monetary('Importe actual', store=True, readonly=True, related='oportunidad_id.planned_revenue')
    importe_inicial = fields.Monetary('Importe inicial', store=True, readonly=True)
    objetivo_equipo_id = fields.Many2one('objetivo.equipo', string='Obj. Equipo venta', store=True, readonly=True,
                                         related='objetivo_id.objetivo_equipo_id')
