from odoo import _, api, fields, models
from datetime import datetime, date

import logging
_logger = logging.getLogger(__name__)


class ObjetivoAnual(models.Model):
    _name = 'objetivo.anual'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Objetivo anual'

    # Estos campos van en el módulo de facturación desde ERP:
    #    x_facturado  Incremento facturado
    #    x_facturado_op_ganada   Fact.Op.Ganadas

    name = fields.Char('Name')
    # El siguiente campo se llamaba x_activo y dependía de otro llamado x_estado (cambiar a estándar):
    active = fields.Boolean('Activo', default=True)
    currency_id = fields.Many2one('res.currency', default=1)

    estado = fields.Selection([('borrador','Borrador'),('activo','Activo'),('archivado','Archivado')],
                              string='Estado', store=True, readonly=True, default='borrador')

    act_finalizada_count = fields.Integer('Activ.finalizadas', readonly=True, store=True,
                                          help='Nº de actividades marcadas como hechas')
    act_planificada_count= fields.Integer('Activ.planificadas', readonly=True, store=True,
                                          help='Nº de actividades planificadas')
    act_vencida_count = fields.Integer('Activ.vencidas', readonly=True, store=True,
                                       help='Nº de oportunidades con actividad planificada sin actualizar (sin realizar).')
    act_vencida_percent = fields.Float('Activ.vencidas( %)', readonly=True, store=True,
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

    cambio_etapa_count = fields.Integer('Cambios de etapa', readonly=1, store=True)
    comercial_id = fields.Many2one('res.users', string="Comercial", store=True, required=True)
    cumplido_ca_anterior = fields.Float('Cumplido CA A-1(€)', readonly=False, store=True,
                                       help='Parte del objetivo de ventas año pasado que había que hacer en cliente actual y cliente Vip.')

    cumplido_cn_anterior = fields.Float('Cumplido CN A-1(€)', readonly=False, store=True,
                                       help='Parte del objetivo de ventas año pasado que había que hacer en Prospección buena, muy interesante, excelnte y Cliente recuperar.')

    @api.depends('cumplido_ca_anterior', 'cumplido_cn_anterior')
    def get_cumplido_total(self):
        self.cumplido_total = (self.cumplido_ca_anterior + self.cumplido_cn_anterior)
    cumplido_total  = fields.Float('Total Año-1', readonly=True, store=True, compute='get_cumplido_total',
                                       help='Objetivo de ventas año pasado, cifra de crecimiento.')

    def get_equipo_ca_hoy_percent(self):
        resultado = 0
        equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', self.objetivo_equipo_id.id)]).objetivo_ca
        if equipo > 0:
            resultado = self.venta_ca / equipo * 100
        self.equipo_ca_hoy_percent = resultado
    equipo_ca_hoy_percent = fields.Float('equipo_ca_hoy_percent', readonly=True, store=False, compute='get_equipo_ca_hoy_percent')

    def get_equipo_ca_objetivo_percent(self):
        resultado = 0
        equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', self.objetivo_equipo_id.id)]).objetivo_ca
        if equipo > 0:
            resultado = self.objetivo_ca / equipo * 100
        self.equipo_ca_objetivo_percent = resultado
    equipo_ca_objetivo_percent = fields.Float('equipo_ca_objetivo_percent', readonly=True, store=False, compute='get_equipo_ca_objetivo_percent')

    def get_equipo_ca_op_hoy_percent(self):
        resultado = 0
        equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', self.objetivo_equipo_id.id)]).objetivo_ca_count
        if equipo > 0:
            resultado = self.op_hoy_ca_count / equipo * 100
        self.equipo_ca_op_hoy_percent = resultado
    equipo_ca_op_hoy_percent = fields.Float('equipo_ca_op_hoy_percent', readonly=True, store=False, compute='get_equipo_ca_op_hoy_percent')

    def get_equipo_ca_op_objetivo_percent(self):
        resultado = 0
        equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', self.objetivo_equipo_id.id)]).objetivo_ca_count
        if equipo > 0:
            resultado = self.objetivo_ca_count / equipo * 100
        self.equipo_ca_op_objetivo_percent = resultado
    equipo_ca_op_objetivo_percent = fields.Float('equipo_ca_op_objetivo_percent', readonly=True, store=False, compute='get_equipo_ca_op_objetivo_percent')

    # Lo mismo para CN:
    def get_equipo_cn_hoy_percent(self):
        resultado = 0
        equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', self.objetivo_equipo_id.id)]).objetivo_cn
        if equipo > 0:
            resultado = self.venta_cn / equipo * 100
        self.equipo_cn_hoy_percent = resultado
    equipo_cn_hoy_percent = fields.Float('equipo_cn_hoy_percent', readonly=True, store=False, compute='get_equipo_cn_hoy_percent')

    def get_equipo_cn_objetivo_percent(self):
        resultado = 0
        equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', self.objetivo_equipo_id.id)]).objetivo_cn
        if equipo > 0:
            resultado = self.objetivo_cn / equipo * 100
        self.equipo_cn_objetivo_percent = resultado
    equipo_cn_objetivo_percent = fields.Float('equipo_cn_objetivo_percent', readonly=True, store=False, compute='get_equipo_cn_objetivo_percent')

    def get_equipo_cn_op_hoy_percent(self):
        resultado = 0
        equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', self.objetivo_equipo_id.id)]).objetivo_cn_count
        if equipo > 0:
            resultado = self.op_hoy_cn_count / equipo * 100
        self.equipo_cn_op_hoy_percent = resultado
    equipo_cn_op_hoy_percent = fields.Float('equipo_ca_op_hoy_percent', readonly=True, store=False, compute='get_equipo_cn_op_hoy_percent')

    def get_equipo_cn_op_objetivo_percent(self):
        resultado = 0
        equipo = self.env['objetivo.equipo'].sudo().search([('id', '=', self.objetivo_equipo_id.id)]).objetivo_cn_count
        if equipo > 0:
            resultado = self.objetivo_cn_count / equipo * 100
        self.equipo_cn_op_objetivo_percent = resultado
    equipo_cn_op_objetivo_percent = fields.Float('equipo_cn_op_objetivo_percent', readonly=True, store=False, compute='get_equipo_cn_op_objetivo_percent')

    equipo_id = fields.Many2one('crm.team', string="Equipo de ventas", related='comercial_id.sale_team_id', store=True, readonly=True)

    @api.depends('objetivo_total','cumplido_total')
    def get_incremento_objetivo_anual_percent(self):
        total = 0
        if self.cumplido_total > 0:
            total = 100 * (self.objetivo_total / self.cumplido_total) - 100
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
        self.objetivo_count = (self.cumplido_ca_anterior + self.cumplido_cn_anterior)
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
                                     help='Total oportunidades que estamos trabajando (no incluye las que están en las fases: Nuevo, Ganado y Perdido, tampoco las iniciativas).'
                                            'Es posible que no coincida con el total de oportunidades activas del CRM, porque calcula la suma de cuenta nueva + base instalada.'
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

    op_perdida_count_percent = fields.Float('Op. Perdidas (%)', store=True, readonly=True,
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

    # BOTONES O2M:
    def get_objetivo_mensual_count(self):
        for record in self:
            meses = self.env['objetivo.mensual'].search([('objetivo_anual_id', '=', record.id)])
            record['objetivo_mensual_count'] = len(meses.ids)
    objetivo_mensual_count = fields.Integer('Objetivo anual count', store=False, readonly=True,
                                                                compute='get_objetivo_mensual_count')
    def get_linea_ids_count(self):
        self.linea_count = len(self.linea_ids.ids)
    linea_count = fields.Integer('Objetivo count', store=False, readonly=True, compute='get_linea_ids_count')

    ### MÉTODOS DE BOTONES:
    def objetivo_anual_activar(self):
        self.estado = 'activo'

    def objetivo_anual_a_borrador(self):
        self.estado = 'borrador'

    def objetivo_anual_archivar(self):
        self.estado = 'archivado'


    # ACCIÓN DE ACTUALIZAR OBJETIVO ANUAL:
    def actualizar_objetivo_anual(self):
        # 11/08/20:
        # Pendiente cambiar los nombres de los campos para cn, cn y variables del tipo op_ganada_ca_count_percent, porque ahora debería ser op_ca_count_percent, en este y otros modelos.
        # Hay otro que es op_perdida_ca_count_percent que tampoco tiene sentido, debería ser (tasa de éxito) op_ganada_ca_count_percent (que precisamente es el anterior), revisar.
        # Subir progreso tras objetivo en origen, dejar tasa de éxito donde está.
        for record in self:
            # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
            # Inicio de variables, creación/eliminación de líneas de objetivo en base a oportunidades, si estado borrador
            # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
            esobjetivo = False
            opactivas, opactivas_ca, opactivas_cn, op_sintipocliente = 0, 0, 0, 0
            acum_opactivas, acum_opactivas_ca, acum_opactivas_cn, acum_op_sintipocliente, opvencidas, op_sin_actividad, actvencidas = 0, 0, 0, 0, 0, 0, 0
            ventaca, ventacn, ganadasca, ganadascn, perdidasca, perdidascn, act_finalizadas_count, venta_ca_percent, venta_cn_percent, venta_percent, perdido_ca_percent, perdido_cn_percent = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            op_ganada_cn_count_percent = 0
            op_ganada_ca_count_percent = 0
            op_ganada_count_percent = 0
            oportunidad_hoy_ca = 0
            oportunidad_hoy_cn = 0
            op_perdida_count_percent = 0
            op_prospeccion_count_percent = 0
            op_activa_vs_hoy_percent = 0
            op_sin_actividad_percent = 0
            op_vencida_count_percent = 0
            act_vencida_percent = 0
            fidelizacion = 0
            captacion = 0
            cantidad_inicial = 0
            cantidad_ganadas = 0
            cantidad_perdidas = 0
            cantidad_inicial = 0
            cambio_etapa_count = 0

            op_activa_delegacion, op_activa_global, vs_delegacion, vs_global, objetivos_delegacion_count, objetivos_central_count, media_global, media_delegacion = 0, 0, 0, 0, 0, 0, 0, 0
            cantidad_oportunidades_delegacion, cantidad_oportunidades_global, media_hoy_delegacion, media_hoy_global = 0, 0, 0, 0
            op_hoy_vs_delegacion, op_hoy_vs_global = 0, 0
            venta_delegacion, venta_global, venta_media_delegacion, venta_media_global, venta_vs_delegacion, venta_vs_global = 0, 0, 0, 0, 0, 0
            cantidad_oportunidades_activas_delegacion, cantidad_oportunidades_activas_global, media_activas_delegacion, media_activas_global, op_activas_vs_delegacion, op_activas_vs_global = 0, 0, 0, 0, 0, 0

            # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
            # Revisar todas las oportunidades del comercial y crear líneas:
            # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

            # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
            # Si el objetivo está en borrador, eliminamos las líneas para que se creen de nuevo en esta acción actualizadas:
            # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
            if record.estado == 'borrador':
                record.linea_ids.unlink()
                esobjetivo = True

            # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
            # Oportunidades de este comercial, activas, y pendientes (no ganadas, no perdidas, no iniciativas):
            # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
            fechanueva = str(record.anho - 1) + '-12-31'
            esnuevo = datetime.strptime(fechanueva, '%Y-%m-%d')

            # 8/7/2021 Modificación porque no pilla las oportunidades en curso al SIN DATE_CLOSED, tener el filtro 'date_closed > esnuevo':
            # 8/7/2021 (original) oportus = self.env['crm.lead'].search([('user_id','=',record.comercial_id.id),('estado','in',['pending','won']),('active','=',True),('date_closed','>',esnuevo)])
            oportus = self.env['crm.lead'].search(
                [('user_id', '=', record.comercial_id.id), ('estado', 'in', ['pending', 'won']), ('active', '=', True)])

            # Control de las que ya están, y quitarlas si se han asignado a otro comercial:
            yaestan = []
            for li in record.linea_ids:
                if (li.oportunidad_id.id not in yaestan) and (li.comercial_id.id == li.oportunidad_id.user_id.id):
                    yaestan.append(li.oportunidad_id.id)
                elif (li.comercial_id.id != li.oportunidad_id.user_id.id):
                    li.unlink()

            if record.estado != 'archivado':
                for opo in oportus:
                    if opo.create_date > esnuevo:
                        esnueva = True
                    else:
                        esnueva = False
                    # 8/7/2021 Modificación para el control del search 'date_closed' del año anterior si existen no archivadas (ver comentario anterior de esta fecha):
                    # 8/7/2021 (original)   if (opo.id not in yaestan):
                    # 8/7/2021 (test para borrar de la misma fecha)    if (opo.id not in yaestan) and (opo.date_closed) and (opo.date_closed &gt; esnuevo):
                    if (opo.id not in yaestan) and not (opo.date_closed) or (opo.id not in yaestan) and (
                            opo.date_closed > esnuevo):
                        nombre = opo.name + ' - ' + opo.stage_id.name
                        nuevalinea = self.env['objetivo.anual.linea'].create(
                            {'oportunidad_id': opo.id, 'objetivo_id': record.id, 'estado_inicial_id': opo.stage_id.id,
                             'importe_inicial': opo.expected_revenue, 'name': nombre, 'es_objetivo': esobjetivo,
                             'cliente_id': opo.partner_id.id,
                             'es_cuenta_nueva': opo.is_prospection, 'es_nueva': esnueva,
                             'comercial_id': opo.user_id.id})

                # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
                # CALCULOS RELATIVOS A LA ACTIVIDAD COMERCIAL (tanto en borrador para diseño, como en objetivo ya confirmado):
                # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
                oportunidades = self.env['crm.lead'].search(
                    [('user_id', '=', record.comercial_id.id), ('estado', '=', 'pending'), ('type', '=', 'opportunity')])
                for op in oportunidades:
                    if op.activity_type_id.id == False:
                        op_sin_actividad += 1
                    if str(date.today()) > str(op.date_deadline):
                        opvencidas += 1
                    if (op.stage_id.en_curso == True) and (op.is_prospection == False) and (
                    op.partner_status_id.id):  # 2023 ¿hace falta si ya está estado arriba?
                        opactivas_ca += 1
                        acum_opactivas_ca += op.expected_revenue
                    if (op.stage_id.en_curso == True) and (op.is_prospection == True) and (op.partner_status_id.id):
                        opactivas_cn += 1
                        acum_opactivas_cn += op.expected_revenue
                    if (op.stage_id.en_curso == True) and not (op.partner_status_id.id):
                        op_sintipocliente += 1
                        acum_op_sintipocliente += op.expected_revenue

                opactivas = opactivas_ca + opactivas_cn + op_sintipocliente
                acum_opactivas = acum_opactivas_ca + acum_opactivas_cn + acum_op_sintipocliente
                # Control 1:
                # raise Warning('CA: ' + str(acum_opactivas_ca) + ' - CAnum: ' + str(opactivas_ca) + ' - CN: ' + str(acum_opactivas_cn) + ' - Total: ' + str(opactivas))

                cantidad_oportunidades = len(self.env['objetivo.anual.linea'].search(
                    [('objetivo_id', '=', record.id), ('oportunidad_id.type', '=', 'opportunity')]).ids)
                cantidad_inicial = len(self.env['objetivo.anual.linea'].search(
                    [('id', 'in', record.linea_ids.ids), ('es_objetivo', '=', True),
                     ('oportunidad_id.type', '=', 'opportunity')]).ids)
                cantidad_objetivo = record.objetivo_ca_count + record.objetivo_cn_count

                # Actividades vencidas:
                actividades = self.env['mail.activity'].search([('user_id', '=', record.comercial_id.id)])
                num_actividades = len(actividades.ids)
                for ac in actividades:
                    if str(date.today()) > str(ac.date_deadline):
                        actvencidas += 1

                    # Actividades planificadas:
                act_activas = len(self.env['mail.activity'].search([('user_id', '=', record.comercial_id.id)]).ids)
                # Actividades finalizadas, hay que buscar ESTE AÑO, en todas las que haya trabajado, sean suyas ahora o no:
                finicio = str(record.anho) + '-01-01'
                actividades_finalizadas = self.env['crm.activity.report'].search(
                    [('user_id', '=', record.comercial_id.id), ('date', '>', finicio)])
                act_finalizada_count = len(actividades_finalizadas.ids)

                # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
                # CRear el registro de "Equipo de ventas" y el "Mensual", SI NO EXISTEN:
                # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
                objetivoequipo = self.env['objetivo.equipo'].search(
                    [('anho', '=', record.anho), ('equipo_id', '=', record.equipo_id.id)])
                if not objetivoequipo.id:
                    nombre = str(record.anho) + ' / ' + record.equipo_id.name
                    objetivoequipo = self.env['objetivo.equipo'].create(
                        {'anho': record.anho, 'equipo_id': record.equipo_id.id, 'name': nombre})

                mes = str(date.today())[5:7]
                objetivomensual = self.env['objetivo.mensual'].search([('objetivo_anual_id', '=', record.id), ('mes', '=', mes)])
                if not objetivomensual.id:
                    nombre = mes + '/' + str(record.anho)
                    objetivomensual = self.env['objetivo.mensual'].create(
                        {'mes': mes, 'objetivo_anual_id': record.id, 'name': nombre})

            # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
            # Cálculos relativos a Objetivos validados (no borrador, no archivados):
            # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
            if record.estado == 'activo':
                # Calcular las ventas (oportunidades ganadas tanto para € como para unidades CN y CA):
                for li in record.linea_ids:
                    if (li.es_cuenta_nueva == False) and (li.oportunidad_id.estado == 'won'):
                        ventaca += li.oportunidad_id.expected_revenue
                        ganadasca += 1
                    elif (li.es_cuenta_nueva == True) and (li.oportunidad_id.estado == 'won'):
                        ventacn += li.oportunidad_id.expected_revenue
                        ganadascn += 1
                    #   Cambiado 05/08/20: elif (li.es_cuenta_nueva == False) and (li.oportunidad_id.estado == 'lost'):
                    elif (li.es_cuenta_nueva == False) and (li.es_perdida == True) and (
                            li.oportunidad_id.type == 'opportunity'):
                        perdidasca += 1
                    # Cambiado 05/08/20:  elif (li.es_cuenta_nueva == True) and (li.oportunidad_id.estado == 'lost'):
                    elif (li.es_cuenta_nueva == True) and (li.es_perdida == True) and (
                            li.oportunidad_id.type == 'opportunity'):
                        perdidascn += 1

                    # Porcentajes del total para ventas, unidades y totales cn+ca:
                if record.objetivo_ca > 0:
                    venta_ca_percent = ventaca / record.objetivo_ca * 100
                if record.objetivo_cn > 0:
                    venta_cn_percent = ventacn / record.objetivo_cn * 100

                # Oportunidades hoy en CA y CN y totales:
                # Modificado para que tome todas, 28/08/2020 igual que en pestaña "Actividades:"
                #  for li in record.linea_ids:
                #    if (li.es_cuenta_nueva == False) and (li.oportunidad_id.estado != 'lost'):
                #      oportunidad_hoy_ca +=1
                #    elif  (li.es_cuenta_nueva == True) and (li.oportunidad_id.estado != 'lost'):
                #      oportunidad_hoy_cn +=1
                oportunidad_hoy_ca = len(self.env['objetivo.anual.linea'].search(
                    [('id', 'in', record.linea_ids.ids), ('es_cuenta_nueva', '=', False),
                     ('oportunidad_id.type', '=', 'opportunity')]))
                oportunidad_hoy_cn = len(self.env['objetivo.anual.linea'].search(
                    [('id', 'in', record.linea_ids.ids), ('es_cuenta_nueva', '=', True),
                     ('oportunidad_id.type', '=', 'opportunity')]))

                ## Miguel cambia el cálculo 11/08, ya no tiene sentido el que se llame 'ganada', pendiente cambiar en todos los modelos:
                # 12/08/20: modifico tras error al dividir por cero (la acción nocturna no va):
                #  if record.objetivo_ca_count &gt; 0:
                if oportunidad_hoy_ca > 0:
                    op_ganada_ca_count_percent = ganadasca / oportunidad_hoy_ca * 100
                #  if record.objetivo_cn_count &gt; 0:
                if oportunidad_hoy_cn > 0:
                    op_ganada_cn_count_percent = ganadascn / oportunidad_hoy_cn * 100

                ventatotal = ventaca + ventacn
                if record.objetivo_total > 0:
                    venta_percent = ventatotal / (record.objetivo_total) * 100
                else:
                    venta_percent = 0
                cuentas_objetivo = record.objetivo_ca_count + record.objetivo_cn_count
                if (cuentas_objetivo > 0):
                    # Actualizado a petición de Miguel 11/08 para que sea sobre las actuales en vez de sobre el objetivo:
                    op_ganada_count_percent = (ganadasca + ganadascn) / cantidad_oportunidades * 100

                # ACTUALIZAR LOS CAMPOS DE LA LÍNEA DE ESTE MES Y COMERCIAL:
#                acc_mes = self.env['ir.actions.server'].browse(208)
                ctx = dict(self.env.context or {})
                ctx.update({'active_id': objetivomensual.id, 'active_model': 'objetivo.mensual'})
#                resp_mes = actualizar_objetivo_mensual().with_context(ctx).run()
                self.env['objetivo.mensual'].actualizar_objetivo_mensual()

                # VAMOS CON KPI:
                # Eficiencia y Perdidas (ganadas o perdidas/ objetivo ud op anual)
                cantidad_ganadas = ganadasca + ganadascn
                cantidad_perdidas = perdidasca + perdidascn

                # Otras estadísticas:
                if cantidad_oportunidades > 0:
                    op_perdida_count_percent = cantidad_perdidas / cantidad_oportunidades * 100
                    op_vencida_count_percent = opvencidas / cantidad_oportunidades * 100
                else:
                    op_perdida_count_percent = 0
                    op_vencida_count_percent = 0

                if (cantidad_oportunidades - cantidad_perdidas) > 0:
                    op_activa_vs_hoy_percent = opactivas / cantidad_oportunidades * 100
                else:
                    op_activa_vs_hoy_percent = 0

                if (num_actividades > 0):
                    act_vencida_percent = actvencidas / num_actividades * 100
                else:
                    act_vencida_percent = 0

                if (cantidad_oportunidades - cantidad_perdidas - cantidad_ganadas > 0):
                    op_sin_actividad_percent = op_sin_actividad / (
                                cantidad_oportunidades - cantidad_perdidas - cantidad_ganadas) * 100
                else:
                    op_sin_actividad_percent = 0

                if cantidad_inicial > 0:
                    op_prospeccion_count_percent = (cantidad_oportunidades - cantidad_inicial) / cantidad_inicial * 100
                else:
                    op_prospeccion_count_percent = 0

                # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
                # KPIs FIDELIZACIÓN (cuenta actual) y CAPTACIÓN (cuenta nueva) en pestaña "Seguimiento":
                # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
                if (perdidasca + ganadasca > 0):
                    fidelizacion = ganadasca / (ganadasca + perdidasca) * 100
                if (perdidascn + ganadascn > 0):
                    captacion = ganadascn / (ganadascn + perdidascn) * 100

                # Porcentaje de perdidas:
                if (oportunidad_hoy_ca > 0):
                    perdido_ca_percent = perdidasca / oportunidad_hoy_ca * 100
                if (oportunidad_hoy_cn > 0):
                    perdido_cn_percent = perdidascn / oportunidad_hoy_cn * 100

                # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
                # 07/2021 KPIs de mercado potencial por comparativas con la delegación y la central (sumo
                # lo de la delegación y posteriormente hago el porcentaje):
                # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
                oportunidades = self.env['crm.lead'].search([('estado', '=', 'pending'), ('type', '=', 'opportunity')])
                objetivos_delegacion_count = len(
                    self.env['objetivo.anual'].search([('anho', '=', record.anho), ('equipo_id', '=', record.equipo_id.id)]))
                objetivos_central_count = len(self.env['objetivo.anual'].search([('anho', '=', record.anho)]))

                for op in oportunidades:
                    op_activa_global += op.expected_revenue
                    cambio_etapa_count += op.cambio_etapa_count
                    if (op.empresa_id.id == record.comercial_id.empresa_id.id):
                        op_activa_delegacion += op.expected_revenue
                media_delegacion = op_activa_delegacion / objetivos_delegacion_count
                media_global = op_activa_global / objetivos_central_count

                if (acum_opactivas < media_delegacion):
                    vs_delegacion = (1 - (acum_opactivas / media_delegacion)) * -100
                elif (media_delegacion != 0):
                    vs_delegacion = ((acum_opactivas / media_delegacion) - 1) * 100

                if (acum_opactivas < media_global):
                    vs_global = (1 - (acum_opactivas / media_global)) * -100
                elif (media_global != 0):
                    vs_global = ((acum_opactivas / media_global) - 1) * 100

                # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
                # 08/2021 KPIs de:
                # si pasamos por objetivos_anho => mal porque actualiza datos de este comercial en base a los de otros comerciales que aún no se han recalculado, se hará por líneas de oportunidad.
                # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
                # 1. Capacidad de generar nuevas oportunidades por comparativas con global (en unidades):
                # Para número de oportunidades de hoy del comercial utilizamos la variable 'cantidad_oportunidades'
                cantidad_oportunidades_delegacion = len(self.env['objetivo.anual.linea'].search(
                    [('equipo_id', '=', record.equipo_id.id), ('anho', '=', record.anho),
                     ('oportunidad_id.type', '=', 'opportunity')]).ids)
                cantidad_oportunidades_global = len(self.env['objetivo.anual.linea'].search(
                    [('anho', '=', record.anho), ('oportunidad_id.type', '=', 'opportunity')]).ids)
                # Cálculo de medias por equipo y central (aprovechamos datos generales del apartdo anterior (objetivos_delegacion_count y objetivos_central_count):
                media_hoy_delegacion = int(cantidad_oportunidades_delegacion / objetivos_delegacion_count)
                media_hoy_global = int(cantidad_oportunidades_global / objetivos_central_count)
                # TEST: raise Warning(str(media_hoy_delegacion) + " " + str(media_hoy_global))
                op_hoy_vs_delegacion = cantidad_oportunidades - media_hoy_delegacion
                op_hoy_vs_global = cantidad_oportunidades - media_hoy_global
                # TEST: raise Warning(str(op_hoy_vs_delegacion) + " " + str(op_hoy_vs_global))

                # 2. GAP de ventas con el global (en €)
                # Utilizamos 'ventatotal' para el valor del comercial
                lineas = self.env['objetivo.anual.linea'].search([('anho', '=', record.anho), ('estado', '=', 'won')])
                for li in lineas:
                    venta_global += li.importe_actual
                    if (li.equipo_id.id == record.equipo_id.id):
                        venta_delegacion += li.importe_actual

                # Cálculo de medias (aprovechamos datos generales del apartdo anterior (objetivos_delegacion_count y objetivos_central_count):

                if objetivos_delegacion_count:  media_venta_delegacion = venta_delegacion / objetivos_delegacion_count
                if objetivos_central_count:     media_venta_global = venta_global / objetivos_central_count

                venta_vs_delegacion = ventatotal - media_venta_delegacion
                venta_vs_global = ventatotal - media_venta_global
                # TEST: raise Warning("Comercial: " + str(ventatotal) + " - Delegación: "+ str(venta_delegacion) + " - Media delegación: " + str(media_venta_delegacion) + " - Media global:" + str(media_venta_global) + " - venta_vs_delegacion: " + str(venta_vs_delegacion) + " - vs global:" + str(venta_vs_global))

                # 3. Esfuerzo requerido, lo mismo del punto 1, pero sólo con las oportunidades 'activas':
                # Para número de oportunidades de hoy del comercial utilizamos la variable 'opactivas'
                cantidad_oportunidades_activas_delegacion = len(self.env['objetivo.anual.linea'].search(
                    [('equipo_id', '=', record.equipo_id.id), ('anho', '=', record.anho),
                     ('oportunidad_id.type', '=', 'opportunity'), ('oportunidad_id.stage_id.en_curso', '=', True)]).ids)
                cantidad_oportunidades_activas_global = len(self.env['objetivo.anual.linea'].search(
                    [('anho', '=', record.anho), ('oportunidad_id.type', '=', 'opportunity'),
                     ('oportunidad_id.stage_id.en_curso', '=', True)]).ids)
                # Cálculo de medias por equipo y central (aprovechamos datos generales del apartdo anterior (objetivos_delegacion_count y objetivos_central_count):
                media_activas_delegacion = int(cantidad_oportunidades_activas_delegacion / objetivos_delegacion_count)
                media_activas_global = int(cantidad_oportunidades_activas_global / objetivos_central_count)
                # TEST: raise Warning(str(media_activas_delegacion) + " " + str(media_activas_global))
                op_activas_vs_delegacion = opactivas - media_activas_delegacion
                op_activas_vs_global = opactivas - media_activas_global
                # TEST: raise Warning(str(op_activas_vs_delegacion) + " " + str(op_activas_vs_global))

            # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
            # Actualizo el registro de objetivo anual con las variables anteriores, para hacer una única escritura:
            # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
            if record.estado != 'archivado':
                record.write({'venta_ca': ventaca, 'venta_cn': ventacn, 'venta_total': ventaca + ventacn,
                              'op_activa_ca': acum_opactivas_ca, 'op_activa_cn': acum_opactivas_cn,
                              'op_ganada_ca_count': ganadasca, 'op_ganada_cn_count': ganadascn,
                              'op_ganada_count': ganadasca + ganadascn,
                              'op_perdida_ca_count': perdidasca, 'op_perdida_ca_count_percent': perdido_ca_percent,
                              'op_perdida_cn_count': perdidascn, 'op_perdida_cn_count_percent': perdido_cn_percent,
                              'venta_ca_percent': venta_ca_percent, 'venta_cn_percent': venta_cn_percent,
                              'op_ganada_ca_count_percent': op_ganada_ca_count_percent,
                              'op_ganada_cn_count_percent': op_ganada_cn_count_percent,
                              'venta_percent': venta_percent, 'op_ganada_count_percent': op_ganada_count_percent,
                              'op_sin_actividad_count': op_sin_actividad, 'op_vencida_count': opvencidas,
                              'op_activa_count': opactivas, 'op_activa': acum_opactivas,
                              'act_vencida_count': actvencidas, 'act_planificada_count': act_activas,
                              'act_finalizada_count': act_finalizada_count,
                              'objetivo_equipo_id': objetivoequipo.id, 'op_hoy_ca_count': oportunidad_hoy_ca,
                              'op_hoy_cn_count': oportunidad_hoy_cn,
                              'op_hoy_count': cantidad_oportunidades, 'op_perdida_count': cantidad_perdidas,
                              'op_prospeccion_count': cantidad_oportunidades - cantidad_inicial,
                              'op_perdida_count_percent': op_perdida_count_percent,
                              'op_prospeccion_count_percent': op_prospeccion_count_percent,
                              'op_activa_vs_hoy_percent': op_activa_vs_hoy_percent,
                              'op_sin_actividad_percent': op_sin_actividad_percent,
                              'op_vencida_count_percent': op_vencida_count_percent,
                              'act_vencida_percent': act_vencida_percent,
                              'kpi_fidelizacion': fidelizacion, 'kpi_captacion': captacion,
                              'op_activa_vs_media_delegacion_percent': vs_delegacion,
                              'op_activa_vs_media_global_percent': vs_global,
                              'op_hoy_vs_delegacion': op_hoy_vs_delegacion, 'op_hoy_vs_global': op_hoy_vs_global,
                              'venta_vs_delegacion': venta_vs_delegacion, 'venta_vs_global': venta_vs_global,
                              'op_activas_vs_delegacion': op_activas_vs_delegacion,
                              'op_activas_vs_global': op_activas_vs_global,
                              'cambio_etapa_count': cambio_etapa_count
                              })
