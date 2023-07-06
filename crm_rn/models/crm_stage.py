# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api

class CrmStage(models.Model):
    _inherit = 'crm.stage'

    en_curso = fields.Boolean('En curso', store=True)
