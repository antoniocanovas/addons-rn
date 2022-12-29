from odoo import _, api, fields, models
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class ObjetivoEquipo(models.Model):
    _name = 'objetivo.equipo'
    _description = 'Objetivo Equipo Anual'

    # Estos campos van en el módulo de facturación desde ERP:
    #    x_facturado  Incremento facturado
    #    x_facturado_op_ganada   Fact.Op.Ganadas

    name = fields.Char('Name')
    active = fields.Boolean('Activo', default=True)
    currency_id = fields.Many2one('res.currency', default=1)
    estado = fields.Selection(string='Estado', store=True, readonly=True,
        [('activo','Activo'),('archivado','Archivado')])

    act_finalizada_count = fields.Integer('Activ.finalizadas', readonly=True, store=True,
                                          help='Nº de actividades marcadas como hechas')
    act_planificada_count= fields.Integer('Activ.planificadas', readonly=True, store=True,
                                          help='Nº de actividades planificadas')
    act_vencida_count = fields.Integer('Activ.vencidas', readonly=True, store=True,
                                       help='Nº de oportunidades con actividad planificada sin actualizar (sin realizar).')
    act_vencida_percent = fields.Float('Activ.vencidas( %)', readonly=True, store=True,
                                       help='Porcentaje entre actividades planificadas sin actualizar y número de oportunidades actuales.')
    anho = fields.Integer('Año', readonly=True, store=True, required=True)

    def get_anho_percent(self):
        hoy = datetime.datetime.today()
        total = 0
        if hoy.year > self.anho:
            total = 100
        else:
            day_of_year = (hoy - datetime.datetime(hoy.year, 1, 1)).days * + 1
            total = day_of_year / 365 * 100
        self.anho_percent = total
    anho_percent = fields.Float('Días transcurridos', readonly=True, store=False, compute='get_anho_percent')

    anual_ids = fields.One2many('objetivo.anual', 'objetivo_equipo_id', string="Comerciales", store=True, readonly=True)
    anual_linea_ids = fields.One2many('objetivo.anual.linea', 'objetivo_equipo_id', string="Reg. Oportunidades", store=True, readonly=True)
    conseguido_ca_count_percent = fields.Float('Nº Op. ganadas CA (% sobre objetivo)', store=True, readonly=True)
    conseguido_cn_count_percent = fields.Float('Nº Op. ganadas CN (% sobre objetivo)', store=True, readonly=True)
    cumplido_ca_anterior = fields.Monetary('Cumplido CA A-1 (€)', store=True, readonly=True)
    cumplido_total = fields.Monetary('Total Año -1', store=True, readonly=True)
    equipo_id = fields.Many2one('crm.team', string="Equipo de ventas", store=True, readonly=True)
    ganada_ca_count = fields.Integer('Nº Op. Ganadas CA', store=True, readonly=True)
    ganada_cn_count = fields.Integer('Nº Op. Ganadas CN', store=True, readonly=True)

    def get_grupo_ca_hoy_percent(self): # VOY POR AQUÍ !!!
        for record in self:
            resultado, objetivo, objetivo_equipo = 0, 0, 0
            equipos = self.env['objetivo.equipo'].sudo().search([('sanho', '=', record.x_anho)])
            for eq in equipos:
                objetivo_equipo = self.env['x_objetivo_equipos'].sudo().search([('id', '=', eq.id)]).x_objetivo_ca
                objetivo += objetivo_equipo

            if objetivo > 0:
                resultado = record.x_venta_ca / objetivo * 100
            record['x_grupo_ca_hoy_percent'] = resultado
    grupo_ca_hoy_percent = fields.Float('grupo_ca_hoy_percent', store=False, reaonly=True, compute='get_grupo_ca_hoy_percent')



    @api.depends('objetivo_total','cumplido_total')
    def get_incremento_objetivo_anual_percent(self):
        total = 0
        if self.cumplido_total > 0:
            total = 100 * (self.objetivo_total / self.x_cumplido_total) - 100
        self.incremento_objetivo_anual_percent = total
    incremento_objetivo_anual_percent = fields.Float('Variación obj.anual', store=True, readonly=True,
                                                     compute='get_incremento_objetivo_anual_percent',
                                                     help='Porcentaje de diferencia entre objetivo total de este año y el del año pasado.')

    def get_iniciativa_count(self):
        total = 0
        iniciativas = self.env['crm.lead'].search([('user_id', '=', self.comercial_id.id), ('type', '=', 'lead')])
        if iniciativas: total = len(iniciativas)
        self.iniciativa_count = total
    iniciativa_count = fields.Integer('Iniciativas', store=False, readonly=True, compute='get_iniciativa_count')

    kpi_captacion = fields.Float('KPI Captación', store=True, readonly=1,
                                 help='Relación entre las oportunidades GANADAS, y la suma de GANADAS+PERDIDAS.'
                                      'Refleja qué tanto por ciento de oportunidades ganamos del total. '
                                      'Por ejemplo un 33% indica que ganamos una de cada 3.'
                                      'Para CUENTA NUEVA.')

    kpi_fidelizacion = fields.Float('KPI Fidelización', store=True, readonly=1,
                                 help='Relación entre las oportunidades GANADAS, y la suma de GANADAS+PERDIDAS.'
                                      'Refleja qué tanto por ciento de oportunidades ganamos del total.'
                                      'Por ejemplo un 33% indica que ganamos una de cada 3.'
                                      'Para CUENTA ACTUAL (base instalada).')

    linea_ids = fields.One2many('objetivo.anual.linea', 'objetivo_id', string='Líneas')

    nota = fields.Text('Notas')

    objetivo_ca = fields.Monetary('Objetivo CA', store=True,
                                  help='Parte del objetivo de venta año actual que hay que hacer en cliente actual o cliente Vip.')
    objetivo_ca_count = fields.Integer('Objetivo Ud.CA', store=True,
                                       help='Número de oportunidades año actual que hay que hacer en Cliente Actual o Cliente VIP.')
    objetivo_cn = fields.Monetary('Objetivo CN', store=True,
                                  help='Parte del objetivo de ventas año actual que hay que hacer en Prospección buena, muy interesante, excelente y Cliente recuperar.')
    objetivo_cn_count = fields.Integer('Objetivo Ud.CN', store=True,
                                       help='Nº de oportunidades año actual que hay que hacer en Prospección buena, muy interesante, excelente y Cliente recuperar.')

    @api.depends('objetivo_ca_count', 'objetivo_cn_count')
    def get_objetivo_count(self):
        self.cumplido_total = (self.cumplido_ca_anterior + self.cumplido_cn_anterior)
    objetivo_count  = fields.Float('Objetivo Nº oportunidades', readonly=True, store=False, compute='get_objetivo_count',
                                       help='Objetivo en número de oportunidades total año actual (nº oport en Venta cruzada más nº oport en Nuevo negocio).')

    objetivo_equipo_id = fields.Many2one('objetivo.equipo', string='Objetivo del equipo', store=True, readonly=True)

    @api.depends('objetivo_total', 'venta_total')
    def get_objetivo_pendiente(self):
        self.objetivo_pendiente = (self.objetivo_total + self.venta_total)
    objetivo_pendiente = fields.Monetary('Objetivo pendiente', store=True, readonly=True, compute='get_objetivo_pendiente')

    @api.depends('objetivo_ca', 'objetivo_cn')
    def get_objetivo_total(self):
        self.objetivo_total = (self.objetivo_ca + self.objetivo_cn)
    objetivo_total = fields.Monetary('Objetivo total', store=True, readonly=True, compute='get_objetivo_total')

    objetivo_ud_ca = fields.Integer('Objetivo Ud. CA', store=True, readonly=True)
    objetivo_ud_cn = fields.Integer('Objetivo Ud. CN', store=True, readonly=True)

    op_activa = fields.Monetary('Op. activas', store=True, readonly=True,
                                help='Importe total de ventas en Oportunidades que estamos trabajando (no incluye las oportunidades que hay en las fases: Nuevo, Ganado y Perdido).'
                                     'Es posible que no coincida con la suma de cuenta nueva + base instalada si algún cliente no tiene esta clasificación asignada.')

    op_activa_ca  = fields.Monetary('Para negociar CA', store=True, readonly=True,
                                help='Importe total de venta en oportunidades de Venta Cruzada que estamos trabajando '
                                     '(no incluye las oportunidades que hay en las fases: Nuevo, Ganado y Perdido), en Cliente Actual y VIP.')

    op_activa_cn = fields.Monetary('Para negociar CN', store=True, readonly=True,
                                help='Importe total de ventas en Oportunidades en Nuevo negocio que estamos trabajando '
                                     '(no incluye las oportundades en las fases: Nuevo, Ganado y Perdido) en Prospección buena, muy interesante, excelente y Cliente recuperar.')

    op_activa_count = fields.Integer('Nº Op. activas', store=True, readonly=True,
                                     'help':'Total oportunidades que estamos trabajando (no incluye las que están en las fases: Nuevo, Ganado y Perdido, tampoco las iniciativas).' \
                                            'Es posible que no coincida con el total de oportunidades activas del CRM, porque calcula la suma de cuenta nueva + base instalada.' \
                                            'Si algún cliente no tiene esta clasificación no contará como ACTIVA.')

    op_activa_vs_hoy_percent = fields.Float('Op. activas (%)', store=True, readonly=True,
                                            help='Porcentaje entre oportunidades Activas y Actuales.')

    op_activa_vs_media_delegacion_percent = fields.Float('Potencial vs delegación', store=True, readonly=True)
    op_activa_vs_media_global_percent = fields.Float('Potencial vs Global', store=True, readonly=True)

    op_activas_vs_delegacion = fields.Integer('Activas VS Equipo', store=True, readonly=True,
                                              help='Comparación entre la cantidad de oportunidades ACTIVAS de este comercial, '
                                                   'con la media de los comerciales de su equipo/delegación.')

    op_activas_vs_global = fields.Integer('Activas VS Global', store=True, readonly=True,
                                          help='Comparación entre la cantidad de oportunidades ACTIVAS de este comercial, con la media de todos los comerciales.')

    def get_op_ca_count_percent(self):
        total = 0
        if (self.objetivo_ca_count > 0):
            total = self.op_hoy_ca_count / self.objetivo_ca_count * 100
        self.op_ca_count_percent = total
    op_ca_count_percent = fields.Float('Progreso Op. CA (%)', store=False, readonly=True, compute='get_op_ca_count_percent')

    def get_op_cn_count_percent(self):
        total = 0
        if (self.objetivo_cn_count > 0):
            total = self.op_hoy_cn_count / self.objetivo_cn_count * 100
        self.op_cn_count_percent = total
    op_cn_count_percent = fields.Float('Progreso Op. CN (%)', store=False, readonly=True, compute='get_op_cn_count_percent')

    op_ganada_ca_count = fields.Integer('Nº Op.Ganadas CA', store=True, readonly=True,
                                        help='Número de oportunidades en fase Ganado de Cliente Actual y VIP.')

    op_ganada_ca_count_percent = fields.Float('Op. ganadas CA (%)', store=True, readonly=True,
                                              help='Porcentaje entre oportunidades Ganadas en Cliente Actual/VIP y nº total de oportunidades en Cliente Actual y VIP.')

    op_ganada_cn_count = fields.Integer('Nº Op.Ganadas CN', store=True, readonly=True,
                                        help='Nº de oportunidades en fase Ganado de Prospección buena, excelente, muy interesante y Cliente recuperar.')

    op_ganada_cn_count_percent = fields.Float('Op. ganadas CN (%)', store=True, readonly=True,
                                              help='Porcentaje entre oportunidades Ganadas en en prospección buena, muy interesante, excelente y cliente recuperar '
                                                   'y nº total de oportunidades en Prospección buena, muy interesante, excelente y Cliente recuperar.')

    op_ganada_count = fields.Integer('Nº Op. Ganadas total', store=True, readonly=True,
                                     help='Total oportunidades en fase Ganado año actual.')

    op_ganada_count_percent = fields.Float('Obj. Nº oportunidades (%)', store=True, readonly=True,
                                           help='Porcentaje entre oportunidades Ganadas y Actuales.')

    op_hoy_ca_count = fields.Integer('Nº Op. Actuales CA', store=True, readonly=True,
                                     help='Número total de oportunidades en Cliente actual y Cliente VIP incluído Nuevo, Ganado y Perdido.')

    op_hoy_cn_count = fields.Integer('Nº Op. Actuales CN', store=True, readonly=True,
                                     help='Nº total de oportunidades en Prospección buena, muy interesante, excelente y Cliente recuperar.')

    op_hoy_count = fields.Integer('Nº Op. actuales', store=True, readonly=True,
                                     help='Oportunidades a fecha de la última actualización, incluyendo las nuevas, ganadas, perdidas y activas.')

    op_hoy_vs_delegacion = fields.Integer('VS Equipo', store=True, readonly=True,
                                          help='Comparación entre la cantidad de oportunidades de este comercial, '
                                               'con la media de los comerciales de su equipo/delegación.')

    op_hoy_vs_global = fields.Integer('VS Central', store=True, readonly=True,
                                      help='Comparación entre la cantidad de oportunidades de este comercial, con la media de todos los comerciales.')

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

    x_op_perdida_count_percent = fields.Float('Op. Perdidas (%)', store=True, readonly=True,
                                              help='Porcentaje entre oportunidades Perdidas y Actuales.')

    op_prospeccion_count = fields.Integer('Nº Op. posteriores a objetivo', store=True, readonly=True,
                                          help='Total oportunidades creadas después del cierre del objetivo anual, es un buen medidor del esfuerzo y la motivación.')

    op_prospeccion_count_percent = fields.Float('Op. posteriores vs objetivo (%)', store=True, readonly=True,
                                                help='% de prospecciones creadas tras el cierre del objetivo, sobre el nº inicial de cierre.'
                                                     'Por ejemplo, si el objetivo son 80 y hay 40 nuevas, este valor será un 50%.')

    op_sin_actividad_count = fields.Integer('Nº Op. sin actividad', store=True, readonly=True,
                                            help='Nº total de actividades sin actividad planificada. '
                                                 'Incluye ACTIVAS + NUEVAS.')

    op_sin_actividad_percent = fields.Float('Nº Op. no planificadas', store=True, readonly=True,
                                            help='Porcentaje entre actividades no planificadas y nº de oportunidades actuales.')

    op_vencida_count = fields.Integer('Nº Op. vencidas', store=True, readonly=True,
                                      help='Total Oportunidades con fecha de cierre vencida.')

    op_vencida_count_percent = fields.Float('Nº Op. Vencidas vs actuales (%)', store=True, readonly=True,
                                            help='Porcentaje entre oportunidades Vencidas y Actuales.')

    @api.depends('op_activa','objetivo_pendiente')
    def get_oportunidad_vs_objetivo_percent(self):
        if self.objetivo_pendiente > 0:
            self.oportunidad_vs_objetivo_percent = self.op_activa / self.objetivo_pendiente * 100
        else:
            self.oportunidad_vs_objetivo_percent = 100
    oportunidad_vs_objetivo_percent = fields.Float('Cobertura', store=True, readonly=True, compute='get_oportunidad_vs_objetivo_percent',
                                                   help='Porcentaje de diferencia entre objetivo venta año y el importe en oportunidades activas.')

    responsable_id = fields.Many2one('res.users', string='Responsable', store=True, required=True)

    venta_ca = fields.Monetary('Venta CA', store=True, readonly=True,
                               help='Ventas en oportunidades ganadas en cliente actual y Vip.')
    venta_ca_percent = fields.Float('Venta CA (%)', store=True, readonly=True,
                                    help='Porcentaje de consecución de objetivo en venta cruzada, cliente actual y Vip.')

    venta_cn = fields.Monetary('Venta CN', store=True, readonly=True,
                               help='Ventas en oportunidades ganadas en Prospección buena, muy interesante, excelente y Cliente recuperar.')
    venta_cn_percent = fields.Float('Venta CN (%)', store=True, readonly=True,
                                    help='Porcentaje de consecución de Objetivo en Nuevo negocio año actual en Prospección buena, muy interesante, excelente y Cliente recuperar.')

    venta_percent = fields.Float('Objetivo de venta (%)', store=True, readonly=True,
                                 help='Porcentaje de consecución de objetivo total, año actual.')

    venta_total = fields.Monetary('Venta total', store=True, readonly=True,
                                  help='Ventas en oportunidades ganadas')

    venta_vs_delegacion = fields.Monetary('Venta vs equipo', store=True, readonly=True,
                                          help='En importe, comparación con la venta media de todos los comerciales de su equipo.')

    venta_vs_global = fields.Monetary('Venta vs Global', store=True, readonly=True,
                                      help='En importe, comparación con la venta media de todos los comerciales.')



    #### REVISAR ::: !!!
    def get_objetivo_anual_id_objetivo_mensuales_count(self):
        for record in self:
            meses = self.env['objetivo_mensual'].search([('objetivo_anual_id', '=', record.id)])
            record['objetivo_anual_id_objetivo_mensuales_count'] = len(meses.ids)
    objetivo_anual_id_objetivo_mensuales_count = fields.Integer('Objetivo anual count', store=False, readonly=True,
                                                                compute='get_objetivo_anual_id_objetivo_mensuales_count')
    def get_objetivo_id__x_objetivo_anual_lineas_count(self):
        self.objetivo_id_objetivo_anual_lineas_count = len(self.linea_ids.ids)
    objetivo_id_objetivo_anual_lineas_count = fields.Integer('Objetivo count', store=False, readonly=True,
                                                                compute='get_objetivo_id__x_objetivo_anual_lineas_count')
