from odoo import _, api, fields, models
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class ObjetivoGrupo(models.Model):
    _name = 'objetivo.grupo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Objetivo Grupo Anual'


    name = fields.Char('Name', store=True, readonly=False)
    active = fields.Boolean('Activo', default=True)
    currency_id = fields.Many2one('res.currency', default=1)
    estado = fields.Selection([('activo','Activo'),('archivado','Archivado')],
                              string='Estado', store=True, readonly=True)

    def get_grupo_act_finalizada_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.act_finalizada_count
        self.act_finalizada_count = total
    act_finalizada_count = fields.Integer('Activ.finalizadas', readonly=True, store=False, compute='get_grupo_act_finalizada_count',
                                          help='Nº de actividades marcadas como hechas')

    def get_grupo_act_planificada_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.act_planificada_count
        self.act_planificada_count = total
    act_planificada_count= fields.Integer('Activ.planificadas', readonly=True, store=False, compute='get_grupo_act_planificada_count',
                                          help='Nº de actividades planificadas')

    def get_grupo_act_vencida_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.act_vencida_count
        self.act_vencida_count = total
    act_vencida_count = fields.Integer('Activ.vencidas', readonly=True, store=False, compute='get_grupo_act_vencida_count',
                                       help='Nº de oportunidades con actividad planificada sin actualizar (sin realizar).')

    def get_grupo_act_vencida_percent(self):
        total = 0
        if (self.act_planificada_count > 0):
            total = self.act_vencida_count / (self.act_planificada_count) * 100
        self.act_vencida_percent = total
    act_vencida_percent = fields.Float('Activ.vencidas( %)', readonly=True, store=False, compute='get_grupo_act_vencida_percent',
                                       help='Porcentaje entre actividades planificadas sin actualizar y número de oportunidades actuales.')

    anho = fields.Integer('Año', readonly=False, store=True, required=True)

    def get_anho_percent(self):
        hoy = datetime.today()
        total = 0
        if hoy.year > self.anho:
            total = 100
        else:
            day_of_year = (hoy - datetime(hoy.year, 1, 1)).days * + 1
            total = day_of_year / 365 * 100
        self.anho_percent = total
    anho_percent = fields.Float('Días transcurridos', readonly=True, store=False, compute='get_anho_percent')

    def get_grupo_cumplido_ca_anterior(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.cumplido_ca_anterior
        self.cumplido_ca_anterior = total
    cumplido_ca_anterior = fields.Monetary('Año anterior', store=False, readonly=True, compute='get_grupo_cumplido_ca_anterior')


    def get_grupo_cumplido_cn_anterior(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.cumplido_cn_anterior
        self.cumplido_cn_anterior = total
    cumplido_cn_anterior = fields.Monetary('Año anterior', store=False, readonly=True, compute='get_grupo_cumplido_cn_anterior')

    def get_grupo_cumplido_total(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.cumplido_total
        self.cumplido_total = total
    cumplido_total = fields.Monetary('Año anterior', store=False, readonly=True, compute='get_grupo_cumplido_total')

    def get_grupo_facturado(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.facturado
        self.facturado = total
    facturado = fields.Monetary('Facturado', store=False, readonly=False, compute='get_grupo_facturado')

    def get_grupo_facturado_op_ganada(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.facturado_op_ganada
        self.facturado_op_ganada = total
    facturado_op_ganada = fields.Monetary('Facturado', store=False, readonly=False, compute='get_grupo_facturado_op_ganada')

    def get_grupo_incremento_objetivo_anual_percent(self):
        total = 0
        if self.cumplido_total > 0:
            total = 100 * (self.objetivo_total / self.cumplido_total) - 100
        self.incremento_objetivo_anual_percent = total
    incremento_objetivo_anual_percent = fields.Float('Variación obj.anual', store=False, readonly=True,
                                                     compute='get_grupo_incremento_objetivo_anual_percent',
                                                     help='Porcentaje de diferencia entre objetivo total de este año y el del año pasado.')

    def get_grupo_iniciativa_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.iniciativa_count
        self.iniciativa_count = total
    iniciativa_count = fields.Integer('Iniciativas', store=False, readonly=True, compute='get_grupo_iniciativa_count')

    def get_grupo_kpi_captacion(self):
        total = 0
        if (self.op_perdida_cn_count + self.op_ganada_cn_count > 0):
            total = self.op_ganada_cn_count / (self.op_perdida_cn_count + self.op_ganada_cn_count) * 100
        self.kpi_captacion = total
    kpi_captacion = fields.Float('KPI Captación', store=False, readonly=1, compute='get_grupo_kpi_captacion',
                                 help='Relación entre las oportunidades GANADAS, y la suma de GANADAS+PERDIDAS.'
                                      'Refleja qué tanto por ciento de oportunidades ganamos del total. '
                                      'Por ejemplo un 33% indica que ganamos una de cada 3.'
                                      'Para CUENTA NUEVA.')


    def get_grupo_kpi_fidelizacion(self):
        total = 0
        if (self.op_perdida_ca_count + self.op_ganada_ca_count > 0):
            total = self.op_ganada_ca_count / (self.op_perdida_ca_count + self.op_ganada_ca_count) * 100
        self.kpi_fidelizacion = total
    kpi_fidelizacion = fields.Float('KPI Fidelización', store=False, readonly=1, compute='get_grupo_kpi_fidelizacion',
                                    help='Relación entre las oportunidades GANADAS, y la suma de GANADAS+PERDIDAS.'
                                         'Refleja qué tanto por ciento de oportunidades ganamos del total.'
                                         'Por ejemplo un 33% indica que ganamos una de cada 3.'
                                         'Para CUENTA ACTUAL (base instalada).')

    nota = fields.Text('Notas')


    def get_grupo_objetivo_ca(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.objetivo_ca
        self.objetivo_ca = total
    objetivo_ca = fields.Monetary('Objetivo CA', store=False, readonly=True, compute='get_grupo_objetivo_ca',
                                  help='Parte del objetivo de venta año actual que hay que hacer en cliente actual o cliente Vip.')

    def get_grupo_objetivo_ca_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.objetivo_ca_count
        self.objetivo_ca_count = total
    objetivo_ca_count = fields.Integer('Objetivo Ud.CA', store=False, readonly=True, compute='get_grupo_objetivo_ca_count',
                                       help='Número de oportunidades año actual que hay que hacer en Cliente Actual o Cliente VIP.')


    def get_grupo_objetivo_cn(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.objetivo_cn
        self.objetivo_cn = total
    objetivo_cn = fields.Monetary('Objetivo CN', store=False, readonly=True, compute='get_grupo_objetivo_cn',
                                  help='Parte del objetivo de ventas año actual que hay que hacer en Prospección buena, muy interesante, excelente y Cliente recuperar.')

    def get_grupo_objetivo_cn_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.objetivo_cn_count
        self.objetivo_cn_count = total
    objetivo_cn_count = fields.Integer('Objetivo Ud.CN', store=False, readonly=True, compute='get_grupo_objetivo_cn_count',
                                       help='Nº de oportunidades año actual que hay que hacer en Prospección buena, muy interesante, excelente y Cliente recuperar.')

    def get_grupo_objetivo_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.objetivo_count
        self.objetivo_count = total
    objetivo_count  = fields.Float('Objetivo Nº oportunidades', readonly=True, store=False, compute='get_grupo_objetivo_count',
                                       help='Objetivo en número de oportunidades total año actual (nº oport en Venta cruzada más nº oport en Nuevo negocio).')


    @api.depends('objetivo_total','venta_total')
    def get_grupo_objetivo_pendiente(self):
        self.objetivo_pendiente = self.objetivo_total - self.venta_total
    objetivo_pendiente = fields.Monetary('Objetivo pendiente', store=True, readonly=True, compute='get_grupo_objetivo_pendiente')

    def get_grupo_objetivo_total(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.objetivo_total
        self.objetivo_total = total
    objetivo_total = fields.Monetary('Objetivo total', store=False, readonly=True, compute='get_grupo_objetivo_total')


    def get_grupo_op_activa(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_activa
        self.op_activa = total
    op_activa = fields.Monetary('Op. activas', store=False, readonly=True, compute='get_grupo_op_activa',
                                help='Importe total de ventas en Oportunidades que estamos trabajando (no incluye las oportunidades que hay en las fases: Nuevo, Ganado y Perdido).'
                                     'Es posible que no coincida con la suma de cuenta nueva + base instalada si algún cliente no tiene esta clasificación asignada.')


    def get_grupo_op_activa_ca(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_activa_ca
        self.op_activa_ca = total
    op_activa_ca  = fields.Monetary('Para negociar CA', store=False, readonly=True, compute='get_grupo_op_activa_ca',
                                help='Importe total de venta en oportunidades de Venta Cruzada que estamos trabajando '
                                     '(no incluye las oportunidades que hay en las fases: Nuevo, Ganado y Perdido), en Cliente Actual y VIP.')

    def get_grupo_op_activa_cn(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_activa_cn
        self.op_activa_cn = total
    op_activa_cn = fields.Monetary('Para negociar CN', store=False, readonly=True, compute='get_grupo_op_activa_cn',
                                help='Importe total de ventas en Oportunidades en Nuevo negocio que estamos trabajando '
                                     '(no incluye las oportundades en las fases: Nuevo, Ganado y Perdido) en Prospección buena, muy interesante, excelente y Cliente recuperar.')

    def get_grupo_op_activa_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_activa_count
        self.op_activa_count = total
    op_activa_count = fields.Integer('Nº Op. activas', store=False, readonly=True, compute='get_grupo_op_activa_count',
                                     help = 'Total oportunidades que estamos trabajando (no incluye las que están en las fases: Nuevo, Ganado y Perdido, tampoco las iniciativas).' \
                                            'Es posible que no coincida con el total de oportunidades activas del CRM, porque calcula la suma de cuenta nueva + base instalada.' \
                                            'Si algún cliente no tiene esta clasificación no contará como ACTIVA.')

    def get_grupo_op_activa_vs_hoy_percent(self):
        total = 0
        if self.op_hoy_count > 0:
            total = self.op_activa_count / self.op_hoy_count * 100
        self.op_activa_vs_hoy_percent = total
    op_activa_vs_hoy_percent = fields.Float('Op. activas (%)', store=False, readonly=True, compute='get_grupo_op_activa_vs_hoy_percent',
                                            help='Porcentaje entre oportunidades Activas y Actuales.')

    def get_grupo_op_ca_count_percent(self):
        total = 0
        if (self.objetivo_ca_count > 0):
            total = self.op_hoy_ca_count / self.objetivo_ca_count * 100
        self.op_ca_count_percent = total
    op_ca_count_percent = fields.Float('Progreso Op. CA (%)', store=False, readonly=True, compute='get_grupo_op_ca_count_percent')

    def get_grupo_op_cn_count_percent(self):
        total = 0
        if (self.objetivo_cn_count > 0):
            total = self.op_hoy_cn_count / self.objetivo_cn_count * 100
        self.op_cn_count_percent = total
    op_cn_count_percent = fields.Float('Progreso Op. CN (%)', store=False, readonly=True, compute='get_grupo_op_cn_count_percent')


    def get_grupo_op_ganada_ca_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_ganada_ca_count
        self.op_ganada_ca_count = total
    op_ganada_ca_count = fields.Integer('Nº Op.Ganadas CA', store=False, readonly=True, compute='get_grupo_op_ganada_ca_count',
                                        help='Número de oportunidades en fase Ganado de Cliente Actual y VIP.')


    def get_grupo_op_ganada_ca_count_percent(self):
        total = 0
        if (self.op_hoy_ca_count > 0):
            total = self.op_ganada_ca_count / self.op_hoy_ca_count * 100
        self.op_ganada_ca_count_percent = total
    op_ganada_ca_count_percent = fields.Float('Op. ganadas CA (% sobre objetivo)', store=False, readonly=True,
                                              compute = 'get_grupo_op_ganada_ca_count_percent',
                                              help='Porcentaje entre oportunidades Ganadas en Cliente Actual/VIP y nº total de oportunidades en Cliente Actual y VIP.')

    def get_grupo_op_ganada_cn_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_ganada_cn_count
        self.op_ganada_cn_count = total
    op_ganada_cn_count = fields.Integer('Nº Op.Ganadas CN', store=False, readonly=True,
                                        compute='get_grupo_op_ganada_cn_count',
                                        help='Nº de oportunidades en fase Ganado de Prospección buena, excelente, muy interesante y Cliente recuperar.')


    def get_grupo_op_ganada_cn_count_percent(self):
        total = 0
        if (self.op_hoy_ca_count > 0):
            total = self.op_ganada_cn_count / self.op_hoy_cn_count * 100
        self.op_ganada_cn_count_percent = total
    op_ganada_cn_count_percent = fields.Float('Op. ganadas CN (% sobre objetivo)', store=False, readonly=True,
                                              compute='get_grupo_op_ganada_cn_count_percent',
                                              help='Porcentaje entre oportunidades Ganadas en en prospección buena, muy interesante, excelente y cliente recuperar '
                                                   'y nº total de oportunidades en Prospección buena, muy interesante, excelente y Cliente recuperar.')

    def get_grupo_op_ganada_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_ganada_count
        self.op_ganada_count = total
    op_ganada_count = fields.Integer('Total Op. Ganadas', store=False, readonly=True, compute='get_grupo_op_ganada_count',
                                     help='Total oportunidades en fase Ganado año actual.')

    def get_grupo_op_ganada_count_percent(self):
        total = 0
        if (self.op_hoy_ca_count > 0):
            total = self.op_ganada_count / self.op_hoy_count * 100
        self.op_ganada_count_percent = total
    op_ganada_count_percent = fields.Float('Progreso Op. ganadas (% sobre objetivo', store=False, readonly=True,
                                           compute='get_grupo_op_ganada_count_percent',
                                           help='Porcentaje entre oportunidades Ganadas y Actuales.')

    def get_grupo_op_hoy_ca_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_hoy_ca_count
        self.op_hoy_ca_count = total
    op_hoy_ca_count = fields.Integer('Nº Op. Actuales CA', store=False, readonly=True, compute='get_grupo_op_hoy_ca_count',
                                     help='Número total de oportunidades en Cliente actual y Cliente VIP incluído Nuevo, Ganado y Perdido.')

    def get_grupo_op_hoy_cn_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_hoy_cn_count
        self.op_hoy_cn_count = total
    op_hoy_cn_count = fields.Integer('Nº Op. Actuales CN', store=False, readonly=True, compute='get_grupo_op_hoy_cn_count',
                                     help='Nº total de oportunidades en Prospección buena, muy interesante, excelente y Cliente recuperar.')


    def get_grupo_op_hoy_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_hoy_count
        self.op_hoy_count = total
    op_hoy_count = fields.Integer('Nº Op. actuales', store=False, readonly=True, compute='get_grupo_op_hoy_count',
                                     help='Oportunidades a fecha de la última actualización, incluyendo las nuevas, ganadas, perdidas y activas.')


    def get_grupo_op_perdida_ca_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_perdida_ca_count
        self.op_perdida_ca_count = total
    op_perdida_ca_count = fields.Integer('Nº Op. Perdidas CA', store=False, readonly=True, compute='get_grupo_op_perdida_ca_count',
                                         help='Nº oportunidades en fase Perdido de clientes Actuales y VIP.')

    def get_grupo_op_perdida_ca_count_percent(self):
        total = 0
        if (self.op_hoy_ca_count > 0):
            total = self.op_perdida_ca_count / self.op_hoy_ca_count * 100
        self.op_perdida_ca_count_percent = total
    op_perdida_ca_count_percent = fields.Float('Tasa de Perdidas CA (%)', store=False, readonly=True, compute='get_grupo_op_perdida_ca_count_percent',
                                               help='Porcentaje entre oportunidades Perdidas en Cliente Actual/VIP y nº total de oportunidades en Cliente Actual y VIP.')

    def get_grupo_op_perdida_cn_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_perdida_cn_count
        self.op_perdida_cn_count = total
    op_perdida_cn_count = fields.Integer('Nº Op. Perdidas CN', store=False, readonly=True, compute='get_grupo_op_perdida_cn_count',
                                         help='Nº oportunidades en fase Perdido de oportunidades en Prospección buena, muy interesante, excelente y Cliente recuperar.')


    def get_grupo_op_perdida_cn_count_percent(self):
        total = 0
        if (self.op_hoy_cn_count > 0):
            total = self.op_perdida_cn_count / self.op_hoy_cn_count * 100
        self.op_perdida_cn_count_percent = total
    op_perdida_cn_count_percent = fields.Float('Op. Perdidas CN (%)', store=False, readonly=True, compute='get_grupo_op_perdida_cn_count_percent',
                                               help='Porcentaje entre oportunidades Perdidas en prospección buena, muy interesante, excelente y cliente recuperar '
                                                    'y nº total de oportunidades en Prospección buena, muy interesante, excelente y Cliente recuperar.')

    def get_grupo_op_perdida_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_perdida_count
        self.op_perdida_count = total
    op_perdida_count = fields.Integer('Nº Op. perdidas', store=False, readonly=True, compute='get_grupo_op_perdida_count',
                                      help='Total oportunidades en fase Perdido año actual.')

    def get_grupo_op_perdida_count_percent(self):
        total = 0
        if (self.op_hoy_cn_count > 0):
            total = self.op_perdida_count / self.op_hoy_count * 100
        self.op_perdida_count_percent = total
    op_perdida_count_percent = fields.Float('Op. Perdidas (%)', store=False, readonly=True,
                                            compute='get_grupo_op_perdida_count_percent',
                                            help='Porcentaje entre oportunidades Perdidas y Actuales.')

    def get_grupo_op_prospeccion_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_prospeccion_count
        self.op_prospeccion_count = total
    op_prospeccion_count = fields.Integer('Posterior a objetivo', store=False, readonly=True, compute='get_grupo_op_prospeccion_count',
                                          help='Total oportunidades creadas después del cierre del objetivo anual, es un buen medidor del esfuerzo y la motivación.')


    def get_grupo_op_prospeccion_count_percent(self):
        total = 0
        cantidad_inicial = self.op_hoy_count - self.op_prospeccion_count
        if (cantidad_inicial > 0):
            total = (self.op_hoy_count - cantidad_inicial) / cantidad_inicial * 100
        self.op_prospeccion_count_percent = total
    op_prospeccion_count_percent = fields.Float('Op. posteriores vs objetivo (%)', store=False, readonly=True,
                                                compute='get_grupo_op_prospeccion_count_percent',
                                                help='% de prospecciones creadas tras el cierre del objetivo, sobre el nº inicial de cierre.'
                                                     'Por ejemplo, si el objetivo son 80 y hay 40 nuevas, este valor será un 50%.')


    def get_grupo_op_sin_actividad_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_sin_actividad_count
        self.op_sin_actividad_count = total
    op_sin_actividad_count = fields.Integer('Nº Op. sin actividad', store=False, readonly=True,
                                            compute='get_grupo_op_sin_actividad_count',
                                            help='Nº total de actividades sin actividad planificada. '
                                                 'Incluye ACTIVAS + NUEVAS.')

    def get_grupo_op_sin_actividad_percent(self):
        total = 0
        if (self.op_hoy_count - self.op_perdida_count - self.op_ganada_count > 0):
            total = self.op_sin_actividad_count / (self.op_hoy_count - self.op_perdida_count - self.op_ganada_count) * 100
        self.op_sin_actividad_percent = total
    op_sin_actividad_percent = fields.Float('Nº Op. no planificadas', store=False, readonly=True,
                                            compute='get_grupo_op_sin_actividad_percent',
                                            help='Porcentaje entre actividades no planificadas y nº de oportunidades actuales.')

    def get_grupo_op_vencida_count(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.op_vencida_count
        self.op_vencida_count = total
    op_vencida_count = fields.Integer('Nº Op. vencidas', store=False, readonly=True, compute='get_grupo_op_vencida_count',
                                      help='Total Oportunidades con fecha de cierre vencida.')


    def get_grupo_op_vencida_percent(self):
        total = 0
        if (self.op_hoy_count > 0):
            total = self.op_vencida_count / self.op_hoy_count * 100
        self.op_vencida_percent = total
    op_vencida_percent = fields.Float('Op. Vencidas (%)', store=False, readonly=True, compute='get_grupo_op_vencida_percent',
                                            help='Porcentaje entre oportunidades Vencidas y Actuales.')

    def get_grupo_oportunidad_vs_objetivo_percent(self):
        total = 100
        if (self.objetivo_pendiente > 0):
            total = self.op_activa / self.objetivo_pendiente * 100
        self.oportunidad_vs_objetivo_percent = total
    oportunidad_vs_objetivo_percent = fields.Float('Cobertura', store=False, readonly=True, compute='get_grupo_oportunidad_vs_objetivo_percent',
                                                   help='Porcentaje de diferencia entre objetivo venta año y el importe en oportunidades activas.')

    def get_grupo_venta_ca(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.venta_ca
        self.venta_ca = total
    venta_ca = fields.Monetary('Venta CA', store=False, readonly=True, compute='get_grupo_venta_ca',
                               help='Ventas en oportunidades ganadas en cliente actual y Vip.')

    def get_grupo_venta_ca_percent(self):
        total = 0
        if (self.objetivo_ca > 0):
            total = self.op_vencida_ca / self.objetivo_ca * 100
        self.venta_ca_percent = total
    venta_ca_percent = fields.Float('Venta CA (% sobre objetivo)', store=False, readonly=True,
                                    compute='get_grupo_venta_ca_percent',
                                    help='Porcentaje de consecución de objetivo en venta cruzada, cliente actual y Vip.')

    def get_grupo_venta_cn(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.venta_cn
        self.venta_cn = total
    venta_cn = fields.Monetary('Venta CN', store=False, readonly=True, compute='get_grupo_venta_cn',
                               help='Ventas en oportunidades ganadas en Prospección buena, muy interesante, excelente y Cliente recuperar.')


    def get_grupo_venta_cn_percent(self):
        total = 0
        if (self.objetivo_cn > 0):
            total = self.venta_cn / self.objetivo_cn * 100
        self.venta_cn_percent = total
    venta_cn_percent = fields.Float('Venta CN (% sobre objetivo)', store=False, readonly=True, compute='get_grupo_venta_cn_percent',
                                    help='Porcentaje de consecución de Objetivo en Nuevo negocio año actual en Prospección buena, muy interesante, excelente y Cliente recuperar.')

    def get_grupo_venta_percent(self):
        total = 0
        if (self.objetivo_total > 0):
            total = self.venta_total / self.objetivo_total * 100
        self.venta_percent = total
    venta_percent = fields.Float('Vendido (% sobre objetivo)', store=False, readonly=True, compute='get_grupo_venta_percent',
                                 help='Porcentaje de consecución de objetivo total, año actual.')

    def get_grupo_venta_total(self):
        total = 0
        equipos = self.env['objetivo.equipo'].search([('anho', '=', self.anho)])
        for eq in equipos:
            total += eq.venta_total
        self.venta_total = total
    venta_total = fields.Monetary('Venta total', store=False, readonly=True, compute='get_grupo_venta_total',
                                  help='Ventas en oportunidades ganadas')

    def actualizar_objetivo_grupo(self):
        return True
