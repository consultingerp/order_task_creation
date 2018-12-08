# -*- coding: utf-8 -*-

from openerp import api, models, fields, _

class ResPartner(models.Model):
	_inherit = "res.partner"

	search_words = fields.Text('Search Words', index=True)
	est_budget = fields.Float('Estimated Annual budget', index=True)
	current_sale = fields.Float('Sales this year (%)', index=True)
	prev_sale = fields.Float('Sales previous year (%)', index=True)
	


