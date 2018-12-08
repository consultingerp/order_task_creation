# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _


class stock_incoterms(models.Model):
    _inherit = "stock.incoterms"

    name = fields.Char('Name', required=True, help="Incoterms are series of sales terms. They are used to divide transaction costs and responsibilities between buyer and seller and reflect state-of-the-art transportation practices.", translate=True)
