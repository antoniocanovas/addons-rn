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
    estado = fields.Selection([('pending','En curso'),('won','Ganado'),('lost','Perdido')],
                              string='Estado', store=True, readonly=True)

    @api.depends('active')
    def _get_lead_es_perdida(self):
        for record in self:
            lost = False
            if record.active == False: lost = True
            record['es_perdida'] = lost
    es_perdida = fields.Boolean('Es perdida', store=True, compute=_get_lead_es_perdida)
