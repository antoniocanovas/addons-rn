# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    empresa_id = fields.Many2one('res.company', string='Empresa', store=True)
    equipo_ids = fields.Many2many('crm.team', string='Equipos', store=True)