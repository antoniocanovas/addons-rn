# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'crm.lead'

    vat   = fields.Char('NIF', related='partner_id.vat', readonly=False)

