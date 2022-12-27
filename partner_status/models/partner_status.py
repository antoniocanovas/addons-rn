from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)


class PartnerStatus(models.Model):
    _name = 'partner.status'
    _description = 'Partner Status'

    name = fields.Char('Name')
    is_prospection = fields.Boolean('Prospection', store=True)
    active = fields.Boolean('Active', default=True, store=True)