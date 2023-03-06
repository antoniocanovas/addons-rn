from odoo import _, api, fields, models
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class ObjetivoMensual(models.Model):
    _name = 'objetivo.mensual'
    _description = 'Objetivo mensual'

    # Estos campos van en el módulo de facturación desde ERP:
    #    x_facturado  Incremento facturado
    #    x_facturado_op_ganada   Fact.Op.Ganadas

    name = fields.Char('Name', store=True, readonly=True)
    # El siguiente campo se llamaba x_activo y dependía de otro llamado x_estado (cambiar a estándar):
    active = fields.Boolean('Activo', default=True)
    currency_id = fields.Many2one('res.currency', default=1)
    estado = fields.Selection(string='Estado', store=True, readonly=True,
        [('borrador','Borrador'),('activo','Activo'),('archivado','Archivado')])

    act_finalizada_count = fields.Integer('Activ.finalizadas', readonly=True, store=True,
                                          help='Nº de actividades marcadas como hechas')
    act_planificada_count= fields.Integer('Activ.planificadas', readonly=True, store=True,
                                          help='Nº de actividades planificadas')
    act_vencida_count = fields.Integer('Activ.vencidas', readonly=True, store=True,
                                       help='Nº de oportunidades con actividad planificada sin actualizar (sin realizar).')
    act_vencida_percent = fields.Float('Activ.vencidas( %)', readonly=True, store=True,
                                       help='Porcentaje entre actividades planificadas sin actualizar y número de oportunidades actuales.')

    comercial_id = fields.Many2one('res.users', string="Comercial", store=True, required=True)
    conseguido_mes_ca_count = fields.Integer('Op. ganadas en mes CA', readonly=True, store=True)
    conseguido_mes_cn_count = fields.Integer('Op. ganadas en mes CN', readonly=True, store=True)
    equipo_id = fields.Many2one('objetivo.mensual', string='Equipo de ventas', store=True, readonly=True)
    facturado = fields.Monetary('Facturado', store=True, readonly=True)
    facturado_op_ganada = fields.Monetary('Fact. Ops. Ganadas', store=True, readonly=True)
    iniciativa_count = fields.Integer('Iniciativas', store=True, readonly=True)
    kpi_captacion = fields.Float('KPI Captación', store=True, readonly=True,
                                 help='Relación entre las oportunidades GANADAS, y la suma de GANADAS+PERDIDAS.'
                                      'Refleja qué tanto por ciento de oportunidades ganamos del total. '
                                      'Por ejemplo un 33% indica que ganamos una de cada 3.'
                                      'Para CUENTA NUEVA.')
    kpi_fidelizacion = fields.Float('KPI Fidelización', store=True, readonly=True,
                                 help='Relación entre las oportunidades GANADAS, y la suma de GANADAS+PERDIDAS.'
                                      'Refleja qué tanto por ciento de oportunidades ganamos del total.'
                                      'Por ejemplo un 33% indica que ganamos una de cada 3.'
                                      'Para CUENTA ACTUAL (base instalada).')
    linea_ids = fields.One2many('objetivo.mensual.linea', 'objetivo_mensual_id', string='Líneas')
    mes = fields.Char('Mes', store=True, readonly=True)
    nota = fields.Text('Notas')
    objetivo_anual_id = fields.Many2one('objetivo.anual', string="Objetivo anual")
    objetivo_ca = fields.Monetary('Objetivo CA', store=True, readonly=True,
                                  help='Parte del objetivo de venta año actual que hay que hacer en cliente actual o cliente Vip.')
    objetivo_ca_count = fields.Integer('Objetivo Ud.CA', store=True, readonly=True,
                                       help='Número de oportunidades año actual que hay que hacer en Cliente Actual o Cliente VIP.')
    objetivo_ca_id = fields.Monetary('Objetivo anual CA', store=True, readonly=True, related='objetivo_anual_id.objetivo_ca',
                                     help='Parte del objetivo de venta año actual que hay que hacer en cliente actual o cliente Vip.')
    objetivo_cn = fields.Monetary('Objetivo CN', store=True, readonly=True,
                                  help='Parte del objetivo de ventas año actual que hay que hacer en Prospección buena, muy interesante, excelente y Cliente recuperar.')
    objetivo_cn_count = fields.Integer('Objetivo Ud.CN', store=True, readonly=True,
                                       help='Nº de oportunidades año actual que hay que hacer en Prospección buena, muy interesante, excelente y Cliente recuperar.')
    objetivo_cn_id = fields.Monetary('Objetivo anual CN', store=True, readonly=True, related='objetivo_anual_id.objetivo_cn',
                                     help='Parte del objetivo de ventas año actual que hay que hacer en Prospección buena, muy interesante, excelente y Cliente recuperar.')
    objetivo_count  = fields.Float('Total Op. objetivo', readonly=True, store=True)
    objetivo_equipo_id = fields.Many2one('objetivo.equipo', string='Objetivo del equipo', store=True, readonly=True,
                                         related='objetivo_anual_id.objetivo_equipo_id')
    objetivo_pendiente = fields.Monetary('Objetivo pendiente', store=True, readonly=True)
    objetivo_total = fields.Monetary('Objetivo total', store=True, readonly=True)
    objetivo_venta_id = fields.Monetary('Objetivo anual', store=True, readonly=True, related='objetivo_anual_id.objetivo_total',
                                        help='Objetivo de ventas año actual, cifra de crecimiento')
    op_activa = fields.Monetary('Op. activas', store=True, readonly=True, readonly=True,
                                help='Importe total de ventas en Oportunidades que estamos trabajando (no incluye las oportunidades que hay en las fases: Nuevo, Ganado y Perdido).'
                                     'Es posible que no coincida con la suma de cuenta nueva + base instalada si algún cliente no tiene esta clasificación asignada.')

    op_activa_count = fields.Integer('Nº Op. activas', store=True, readonly=True,
                                     help='Total oportunidades que estamos trabajando (no incluye las que están en las fases: Nuevo, Ganado y Perdido, tampoco las iniciativas).' \
                                            'Es posible que no coincida con el total de oportunidades activas del CRM, porque calcula la suma de cuenta nueva + base instalada.' \
                                            'Si algún cliente no tiene esta clasificación no contará como ACTIVA.')

    op_activa_vs_hoy_percent = fields.Float('Op. activas (%)', store=True, readonly=True,
                                            help='Porcentaje entre oportunidades Activas y Actuales.')

    @api.depends('objetivo_ca_count','op_hoy_ca_count')
    def get_op_ca_count_percent(self):
        total = 0
        if (self.objetivo_ca_count > 0):
            total = self.op_hoy_ca_count / self.objetivo_ca_count * 100
        self.op_ca_count_percent = total
    op_ca_count_percent = fields.Float('Progreso Op. CA (%)', store=False, readonly=True, compute='get_op_ca_count_percent')

    @api.depends('objetivo_cn_count','op_hoy_cn_count')
    def get_op_cn_count_percent(self):
        total = 0
        if (self.objetivo_cn_count > 0):
            total = self.op_hoy_cn_count / self.objetivo_cn_count * 100
        self.op_cn_count_percent = total
    op_cn_count_percent = fields.Float('Progreso Op. CN (%)', store=False, readonly=True, compute='get_op_cn_count_percent')

    op_ganada = fields.Monetary('Op. ganadas', store=True, readonly=True)
    op_ganada_ca_count = fields.Integer('Nº Op.Ganadas CA', store=True, readonly=True,
                                        help='Número de oportunidades en fase Ganado de Cliente Actual y VIP.')
    op_ganada_ca_count_percent = fields.Float('Op. ganadas CA (%)', store=True, readonly=True,
                                              help='Porcentaje entre oportunidades Ganadas en Cliente Actual/VIP y nº total de oportunidades en Cliente Actual y VIP.')
    op_ganada_cn_count = fields.Integer('Nº Op.Ganadas CN (%obj)', store=True, readonly=True,
                                        help='Nº de oportunidades en fase Ganado de Prospección buena, excelente, muy interesante y Cliente recuperar.')
    op_ganada_cn_count_percent = fields.Float('Op. ganadas CN (%obj)', store=True, readonly=True,
                                              help='Porcentaje entre oportunidades Ganadas en en prospección buena, muy interesante, excelente y cliente recuperar '
                                                   'y nº total de oportunidades en Prospección buena, muy interesante, excelente y Cliente recuperar.')
    op_ganada_count = fields.Integer('Nº Op. Ganadas total', store=True, readonly=True,
                                     help='Total oportunidades en fase Ganado año actual.')
    op_ganada_count_percent = fields.Float('Obj. Nº oportunidades (%obj)', store=True, readonly=True,
                                           help='Porcentaje entre oportunidades Ganadas y Actuales.')

    op_ganada_mes_ca_count = fields.Integer('Nº Op. Ganadas CA este mes', store=True, readonly=True)
    op_ganada_mes_ca_count_percent = fields.Float('Nº Op. Ganadas CA este mes (%obj)', store=True, readonly=True)
    op_ganada_mes_cn_count = fields.Integer('Nº Op. Ganadas CN este mes', store=True, readonly=True)
    op_ganada_mes_cn_count_percent = fields.Float('Nº Op. Ganadas CN este mes (%obj)', store=True, readonly=True)
    op_ganada_mes_count = fields.Integer('Nº Op. Ganadas este mes', store=True, readonly=True)
    op_ganada_mes_count_percent = fields.Float('Nº Op. Ganadas este mes (%obj)', store=True, readonly=True)

    op_hoy_ca_count = fields.Integer('Nº Op. Actuales CA', store=True, readonly=True,
                                     help='Número total de oportunidades en Cliente actual y Cliente VIP incluído Nuevo, Ganado y Perdido.')
    op_hoy_cn_count = fields.Integer('Nº Op. Actuales CN', store=True, readonly=True,
                                     help='Nº total de oportunidades en Prospección buena, muy interesante, excelente y Cliente recuperar.')
    op_hoy_count = fields.Integer('Nº Op. actuales', store=True, readonly=True,
                                     help='Oportunidades a fecha de la última actualización, incluyendo las nuevas, ganadas, perdidas y activas.')

    op_iniciada = fields.Monetary('2. Op. Iniciadas', store=True, readonly=True)
    op_iniciada_count = fields.Integer('Nº Op. Iniciadas', store=True, readonly=True)
    op_madura = fields.Monetary('3. Op. Maduras', store=True, readonly=True)
    op_madura_count = fields.Integer('Nº Op. Maduras', store=True, readonly=True)
    op_nueva = fields.Monetary('1. Op. Nuevas', store=True, readonly=True)
    op_nueva_count = fields.Integer('Nº Op. Nuevas', store=True, readonly=True)
    op_perdida = fields.Monetary('5. Op. Perdidas', store=True, readonly=True)
    op_perdida_ca_count = fields.Integer('Nº Op. Perdidas CA', store=True, readonly=True,
                                         help='Nº oportunidades en fase Perdido de clientes Actuales y VIP.')
    op_perdida_ca_count_percent = fields.Float('Op. Perdidas CA (%)', store=True, readonly=True,
                                               help='Porcentaje entre oportunidades Perdidas en Cliente Actual/VIP y nº total de oportunidades en Cliente Actual y VIP.')
    op_perdida_cn_count = fields.Integer('Nº Op. Perdidas CN', store=True, readonly=True,
                                         help='Nº oportunidades en fase Perdido de oportunidades en Prospección buena, muy interesante, excelente y Cliente recuperar.')
    op_perdida_cn_count_percent = fields.Float('Op. Perdidas CN (%)', store=True, readonly=True,
                                               help='Porcentaje entre oportunidades Perdidas en prospección buena, muy interesante, excelente y cliente recuperar '
                                                    'y nº total de oportunidades en Prospección buena, muy interesante, excelente y Cliente recuperar.')
    op_perdida_count = fields.Integer('Nº Op. perdidas', store=True, readonly=True,
                                      help='Total oportunidades en fase Perdido año actual.')
    op_perdida_count_percent = fields.Float('Op. Perdidas (% obj)', store=True, readonly=True,
                                              help='Porcentaje entre oportunidades Perdidas y Actuales.')
    op_perdida_mes_ca_count = fields.Integer('Nº Op. Perdidas CA este mes', store=True, readonly=True,
                                         help='Nº oportunidades en fase Perdido de clientes Actuales y VIP este mes.')
    op_perdida_mes_ca_count_percent = fields.Float('Op. Perdidas CA este mes sobre total', store=True, readonly=True,
                                               help='Porcentaje entre oportunidades Perdidas en Cliente Actual/VIP y nº total de oportunidades en Cliente Actual y VIP este mes.')
    op_perdida_mes_cn_count = fields.Integer('Nº Op. Perdidas CN este mes', store=True, readonly=True,
                                         help='Nº oportunidades en fase Perdido de oportunidades en Prospección buena, muy interesante, excelente y Cliente recuperar, este mes.')
    op_perdida_mes_cn_count_percent = fields.Float('Op. Perdidas CN este mes sobre total (%)', store=True, readonly=True,
                                               help='Porcentaje entre oportunidades Perdidas en prospección buena, muy interesante, excelente y cliente recuperar '
                                                    'y nº total de oportunidades en Prospección buena, muy interesante, excelente y Cliente recuperar, este mes.')
    op_perdida_mes_count = fields.Integer('Nº Op. Perdidas este mes', store=True, readonly=True)
    op_perdida_mes_count_percent = fields.Float('Nº Op. Perdidas este mes (% total)', store=True, readonly=True)
    op_prospeccion_count = fields.Integer('Nº Op. posteriores a objetivo', store=True, readonly=True,
                                          help='Total oportunidades creadas después del cierre del objetivo anual, es un buen medidor del esfuerzo y la motivación.')

    op_prospeccion_count_percent = fields.Float('Op. posteriores vs objetivo (%)', store=True, readonly=True,
                                                help='% de prospecciones creadas tras el cierre del objetivo, sobre el nº inicial de cierre.'
                                                     'Por ejemplo, si el objetivo son 80 y hay 40 nuevas, este valor será un 50%.')

    op_prospeccion_mes_count = fields.Integer('Nº Op. nuevas este mes', store=True, readonly=True,
                                              help = 'Total oportunidades creadas después del cierre del objetivo anual, '
                                                     'es un buen medidor del esfuerzo y la motivación, este mes.')
    op_prospeccion_mes_count_percent = fields.Float('Nº Op. nuevas este mes (% obj)', store=True, readonly=True,
                                                      help='% de prospecciones creadas tras el cierre del objetivo, sobre el nº inicial de cierre.'
                                                     'Por ejemplo, si el objetivo son 80 y hay 40 nuevas, este valor será un 50%; este mes.')
    op_sin_actividad_count = fields.Integer('Nº Op. sin actividad', store=True, readonly=True,
                                            help='Nº total de actividades sin actividad planificada. '
                                                 'Incluye ACTIVAS + NUEVAS.')
    op_sin_actividad_percent = fields.Float('Nº Op. no planificadas', store=True, readonly=True,
                                            help='Porcentaje entre actividades no planificadas y nº de oportunidades actuales.')
    op_vencida_count = fields.Integer('Nº Op. vencidas', store=True, readonly=True,
                                      help='Total Oportunidades con fecha de cierre vencida.')
    op_vencida_count_percent = fields.Float('Nº Op. Vencidas vs actuales (%)', store=True, readonly=True,
                                            help='Porcentaje entre oportunidades Vencidas y Actuales.')
    oportunidad_vs_objetivo_percent = fields.Float('Cobertura', store=True, readonly=True,
                                                   help='Porcentaje de diferencia entre objetivo venta año y el importe en oportunidades activas.')
    venta_ca = fields.Monetary('Venta CA', store=True, readonly=True,
                               help='Ventas en oportunidades ganadas en cliente actual y Vip.')
    venta_cn = fields.Monetary('Venta CN', store=True, readonly=True,
                               help='Ventas en oportunidades ganadas en Prospección buena, muy interesante, excelente y Cliente recuperar.')
    venta_mes = fields.Monetary('Vendido este mes', store=True, readonly=True)
    venta_mes_ca = fields.Monetary('Vendido este mes CA (€)', store=True, readonly=True)
    venta_mes_ca_percent = fields.Float('Vendido este mes CA (% obj)', store=True, readonly=True)
    venta_mes_cn = fields.Monetary('Vendido este mes CN (€)', store=True, readonly=True)
    venta_mes_cn_percent = fields.Monetary('Vendido este mes CN (% obj)', store=True, readonly=True)

    venta_percent = fields.Float('Objetivo de venta (%)', store=True, readonly=True,
                                 help='Porcentaje de consecución de objetivo total, año actual.')
    venta_total = fields.Monetary('Venta total', store=True, readonly=True,
                                  help='Ventas en oportunidades ganadas')
    venta_total_percent = fields.Float('Vendido (% obj)', store=True, readonly=True,
                                 help='Porcentaje de consecución de objetivo total, año actual.')

    def get_mes_objetivo_mensual_id_objetivo_mensual_lineas_count(self):
        self.objetivo_mensual_id_objetivo_mensual_lineas_count = len(self.linea_ids.ids)
    objetivo_mensual_id_objetivo_mensual_lineas_count = fields.Integer('Obj mensual count', store=True, readonly=True,
                                                                       compute='get_mes_objetivo_mensual_id_objetivo_mensual_lineas_count')

