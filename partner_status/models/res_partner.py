# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    status_id = fields.Many2one('partner.status', string='Partner type')
    sale_contact = fields.Boolean('Commercial contact')

    @api.depends('child_ids.sale_contact','sale_contact')
    def get_sale_contacts_qty(self):
        contacts = 0
        if (self.sale_contact == True): contacts = 1
        for co in self.child_ids:
            if (co.sale_contact == True): contacts += 1
        self.sale_contact_qty = contacts
    sale_contact_qty = fields.Integer('Sale contacts', compute='get_sale_contacts_qty')

