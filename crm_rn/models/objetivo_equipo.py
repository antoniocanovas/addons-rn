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

    name = fields.Char('Name', store=True, readonly=True)
    active = fields.Boolean('Activo', default=True)
    currency_id = fields.Many2one('res.currency', default=1)
#    estado = fields.Selection([('activo','Activo'),('archivado','Archivado')],
#                              string='Estado', store=True, readonly=True)

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

    def get_grupo_ca_hoy_percent(self):
        resultado, objetivo, objetivo_equipo = 0, 0, 0
        equipos = self.env['objetivo.equipo'].sudo().search([('anho', '=', self.anho)])
        for eq in equipos:
            objetivo_equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', eq.id)]).objetivo_ca
            objetivo += objetivo_equipo
        if objetivo > 0:
            resultado = self.venta_ca / objetivo * 100
        self.grupo_ca_hoy_percent = resultado
    grupo_ca_hoy_percent = fields.Float('grupo_ca_hoy_percent', store=False, reaonly=True, compute='get_grupo_ca_hoy_percent')

    def get_grupo_ca_objetivo_percent(self):
        resultado, objetivo, objetivo_equipo = 0, 0, 0
        equipos = self.env['objetivo.equipo'].sudo().search([('anho', '=', self.anho)])
        for eq in equipos:
            objetivo_equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', eq.id)]).objetivo_ca
            objetivo += objetivo_equipo
        if objetivo > 0:
            resultado = self.objetivo_ca / objetivo * 100
        self.grupo_ca_objetivo_percent = resultado
    grupo_ca_objetivo_percent = fields.Float('grupo_ca_objetivo_percent', store=False, reaonly=True, compute='get_grupo_ca_objetivo_percent')

    def get_grupo_ca_op_hoy_percent(self):
        resultado, objetivo, objetivo_equipo = 0, 0, 0
        equipos = self.env['objetivo.equipo'].sudo().search([('anho', '=', self.anho)])
        for eq in equipos:
            objetivo_equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', eq.id)]).objetivo_ca_count
            objetivo += objetivo_equipo
        if objetivo > 0:
            resultado = self.op_hoy_ca_count / objetivo * 100
        self.grupo_ca_op_hoy_percent = resultado
    grupo_ca_op_hoy_percent = fields.Float('grupo_ca_op_hoy_percent', store=False, reaonly=True, compute='get_grupo_ca_op_hoy_percent')

    def get_grupo_ca_op_objetivo_percent(self):
        resultado, objetivo, objetivo_equipo = 0, 0, 0
        equipos = self.env['objetivo.equipo'].sudo().search([('anho', '=', self.anho)])
        for eq in equipos:
            objetivo_equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', eq.id)]).objetivo_ca_count
            objetivo += objetivo_equipo
        if objetivo > 0:
            resultado = self.objetivo_ca_count / objetivo * 100
        self.grupo_ca_op_objetivo_percent = resultado
    grupo_ca_op_objetivo_percent = fields.Float('grupo_ca_op_objetivo_percent', store=False, reaonly=True, compute='get_grupo_ca_op_objetivo_percent')

    # Ahora con CN:
    def get_grupo_cn_hoy_percent(self):
        resultado, objetivo, objetivo_equipo = 0, 0, 0
        equipos = self.env['objetivo.equipo'].sudo().search([('anho', '=', self.anho)])
        for eq in equipos:
            objetivo_equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', eq.id)]).objetivo_cn
            objetivo += objetivo_equipo
        if objetivo > 0:
            resultado = self.venta_ca / objetivo * 100
        self.grupo_cn_hoy_percent = resultado
    grupo_cn_hoy_percent = fields.Float('grupo_ca_hoy_percent', store=False, reaonly=True, compute='get_grupo_cn_hoy_percent')

    def get_grupo_cn_objetivo_percent(self):
        resultado, objetivo, objetivo_equipo = 0, 0, 0
        equipos = self.env['objetivo.equipo'].sudo().search([('anho', '=', self.anho)])
        for eq in equipos:
            objetivo_equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', eq.id)]).objetivo_cn
            objetivo += objetivo_equipo
        if objetivo > 0:
            resultado = self.objetivo_cn / objetivo * 100
        self.grupo_cn_objetivo_percent = resultado
    grupo_cn_objetivo_percent = fields.Float('grupo_cn_objetivo_percent', store=False, reaonly=True, compute='get_grupo_cn_objetivo_percent')

    def get_grupo_cn_op_hoy_percent(self):
        resultado, objetivo, objetivo_equipo = 0, 0, 0
        equipos = self.env['objetivo.equipo'].sudo().search([('anho', '=', self.anho)])
        for eq in equipos:
            objetivo_equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', eq.id)]).objetivo_cn_count
            objetivo += objetivo_equipo
        if objetivo > 0:
            resultado = self.op_hoy_cn_count / objetivo * 100
        self.grupo_ca_op_hoy_percent = resultado
    grupo_cn_op_hoy_percent = fields.Float('grupo_cn_op_hoy_percent', store=False, reaonly=True, compute='get_grupo_cn_op_hoy_percent')

    def get_grupo_cn_op_objetivo_percent(self):
        resultado, objetivo, objetivo_equipo = 0, 0, 0
        equipos = self.env['objetivo.equipo'].sudo().search([('anho', '=', self.anho)])
        for eq in equipos:
            objetivo_equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', eq.id)]).objetivo_cn_count
            objetivo += objetivo_equipo
        if objetivo > 0:
            resultado = self.objetivo_cn_count / objetivo * 100
        self.grupo_cn_op_objetivo_percent = resultado
    grupo_cn_op_objetivo_percent = fields.Float('grupo_cn_op_objetivo_percent', store=False, reaonly=True, compute='get_grupo_cn_op_objetivo_percent')


    @api.depends('objetivo_total','cumplido_total')
    def get_equipo_incremento_objetivo_anual_percent(self):
        total = 0
        if self.cumplido_total > 0:
            total = 100 * (self.objetivo_total / self.x_cumplido_total) - 100
        self.incremento_objetivo_anual_percent = total
    incremento_objetivo_anual_percent = fields.Float('Variación obj.anual', store=True, readonly=True,
                                                     compute='get_equipo_incremento_objetivo_anual_percent',
                                                     help='Porcentaje de diferencia entre objetivo total de este año y el del año pasado.')

    iniciativa_count = fields.Integer('Iniciativas', store=True, readonly=True)


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

    mes_ids = fields.One2many('objetivo.mensual', 'objetivo_equipo_id', string='Meses')
    nota = fields.Text('Notas')

    objetivo_ca = fields.Monetary('Objetivo CA', store=True, readonly=True,
                                  help='Parte del objetivo de venta año actual que hay que hacer en cliente actual o cliente Vip.')
    objetivo_ca_count = fields.Integer('Objetivo Ud.CA', store=True, readonly=True,
                                       help='Número de oportunidades año actual que hay que hacer en Cliente Actual o Cliente VIP.')
    objetivo_cn = fields.Monetary('Objetivo CN', store=True, readonly=True,
                                  help='Parte del objetivo de ventas año actual que hay que hacer en Prospección buena, muy interesante, excelente y Cliente recuperar.')
    objetivo_cn_count = fields.Integer('Objetivo Ud.CN', store=True, readonly=True,
                                       help='Nº de oportunidades año actual que hay que hacer en Prospección buena, muy interesante, excelente y Cliente recuperar.')
    objetivo_count  = fields.Float('Objetivo Nº oportunidades', readonly=True, store=True,
                                       help='Objetivo en número de oportunidades total año actual (nº oport en Venta cruzada más nº oport en Nuevo negocio).')
    objetivo_pendiente = fields.Monetary('Objetivo pendiente', store=True, readonly=True)

    objetivo_total = fields.Monetary('Objetivo total', store=True, readonly=True)

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
                                     help='Total oportunidades que estamos trabajando (no incluye las que están en las fases: Nuevo, Ganado y Perdido, tampoco las iniciativas).' \
                                            'Es posible que no coincida con el total de oportunidades activas del CRM, porque calcula la suma de cuenta nueva + base instalada.' \
                                            'Si algún cliente no tiene esta clasificación no contará como ACTIVA.')

    op_activa_vs_hoy_percent = fields.Float('Op. activas (%)', store=True, readonly=True,
                                            help='Porcentaje entre oportunidades Activas y Actuales.')

    op_activa_vs_media_global_percent = fields.Float('Potencial vs Global', store=True, readonly=True)

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

    op_ganada_ca_count_percent = fields.Float('Op. ganadas CA (% sobre objetivo)', store=True, readonly=True,
                                              help='Porcentaje entre oportunidades Ganadas en Cliente Actual/VIP y nº total de oportunidades en Cliente Actual y VIP.')

    op_ganada_cn_count = fields.Integer('Nº Op.Ganadas CN', store=True, readonly=True,
                                        help='Nº de oportunidades en fase Ganado de Prospección buena, excelente, muy interesante y Cliente recuperar.')

    op_ganada_cn_count_percent = fields.Float('Op. ganadas CN (% sobre objetivo)', store=True, readonly=True,
                                              help='Porcentaje entre oportunidades Ganadas en en prospección buena, muy interesante, excelente y cliente recuperar '
                                                   'y nº total de oportunidades en Prospección buena, muy interesante, excelente y Cliente recuperar.')

    op_ganada_count = fields.Integer('Total Op. Ganadas', store=True, readonly=True,
                                     help='Total oportunidades en fase Ganado año actual.')

    op_ganada_count_percent = fields.Float('Progreso Op. ganadas (% sobre objetivo', store=True, readonly=True,
                                           help='Porcentaje entre oportunidades Ganadas y Actuales.')

    op_hoy_ca_count = fields.Integer('Nº Op. Actuales CA', store=True, readonly=True,
                                     help='Número total de oportunidades en Cliente actual y Cliente VIP incluído Nuevo, Ganado y Perdido.')

    op_hoy_cn_count = fields.Integer('Nº Op. Actuales CN', store=True, readonly=True,
                                     help='Nº total de oportunidades en Prospección buena, muy interesante, excelente y Cliente recuperar.')

    op_hoy_count = fields.Integer('Nº Op. actuales', store=True, readonly=True,
                                     help='Oportunidades a fecha de la última actualización, incluyendo las nuevas, ganadas, perdidas y activas.')

    op_hoy_vs_global = fields.Integer('VS Central', store=True, readonly=True,
                                      help='Comparación entre la media de oportunidades por cada comercial en esta delegación, con la media total de  los comerciales.')

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

    op_perdida_count_percent = fields.Float('Op. Perdidas (%)', store=True, readonly=True,
                                            help='Porcentaje entre oportunidades Perdidas y Actuales.')

    op_prospeccion_count = fields.Integer('Posterior a objetivo', store=True, readonly=True,
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

    # En objetivo anual esta se llama op_vencida_count_percent:
    op_vencida_percent = fields.Float('Op. Vencidas (%)', store=True, readonly=True,
                                            help='Porcentaje entre oportunidades Vencidas y Actuales.')

    oportunidad_vs_objetivo_percent = fields.Float('Cobertura', store=True, readonly=True, compute='get_oportunidad_vs_objetivo_percent',
                                                   help='Porcentaje de diferencia entre objetivo venta año y el importe en oportunidades activas.')

    responsable_id = fields.Many2one('res.users', string='Responsable', store=True, readonly=True)

    venta_ca = fields.Monetary('Venta CA', store=True, readonly=True,
                               help='Ventas en oportunidades ganadas en cliente actual y Vip.')
    venta_ca_percent = fields.Float('Venta CA (% sobre objetivo)', store=True, readonly=True,
                                    help='Porcentaje de consecución de objetivo en venta cruzada, cliente actual y Vip.')

    venta_cn = fields.Monetary('Venta CN', store=True, readonly=True,
                               help='Ventas en oportunidades ganadas en Prospección buena, muy interesante, excelente y Cliente recuperar.')
    venta_cn_percent = fields.Float('Venta CN (% sobre objetivo)', store=True, readonly=True,
                                    help='Porcentaje de consecución de Objetivo en Nuevo negocio año actual en Prospección buena, muy interesante, excelente y Cliente recuperar.')

    venta_percent = fields.Float('Vendido (% sobre objetivo)', store=True, readonly=True,
                                 help='Porcentaje de consecución de objetivo total, año actual.')

    venta_total = fields.Monetary('Venta total', store=True, readonly=True,
                                  help='Ventas en oportunidades ganadas')

    venta_vs_global = fields.Monetary('Venta vs Global', store=True, readonly=True,
                                      help='Diferencia media de importe por usuario de la delegación, con respecto a la media global de todos los comerciales.')


    #### REVISAR ::: !!!
    def get_objetivo_equipo_id_objetivo_anual_lineas_count(self):
        for record in self:
            lineas = self.env['objetivo.anual.linea'].search([('objetivo_equipo_id', '=', record.id)])
            record['objetivo_equipo_id_objetivo_anual_lineas_count'] = len(lineas.ids)
    objetivo_equipo_id_objetivo_anual_lineas_count = fields.Integer('Obj. Equipo venta count', store=False, readonly=True,
                                                                compute='get_objetivo_equipo_id_objetivo_anual_lineas_count')
    def get_objetivo_equipo_id_objetivo_anuales_count(self):
        lineas = self.env['objetivo.anual'].search([('objetivo_equipo_id', '=', self.id)])
        self.objetivo_id_objetivo_anual_lineas_count = len(lineas.ids)
    objetivo_equipo_id_objetivo_anuales_count = fields.Integer('Objetivo equipo count', store=False, readonly=True,
                                                                compute='get_objetivo_equipo_id_objetivo_anuales_count')

    def objetivo_equipo_id_objetivo_mensuales_count(self):
        lineas = self.env['objetivo.mensual'].search([('objetivo_equipo_id', '=', self.id)])
        record['objetivo_equipo_id_objetivo_mensuales_count'] = len(lineas.ids)
    objetivo_equipo_id_objetivo_mensuales_count = fields.Integer('Obj. Equipo Ventas count', store=False, readonly=True,
                                                                 compute='get_objetivo_equipo_id_objetivo_mensuales_count')
