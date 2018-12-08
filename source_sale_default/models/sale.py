# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time

class SaleOrder(models.Model):
	_inherit = "sale.order"

	@api.model
	def default_get(self, fields):
		rec = super(SaleOrder, self).default_get(fields)
		if rec.get('note'):
			rec.update({'note':''})
		return rec

	@api.model
	def _get_default_incoterm(self):
	    default_incoterm_id = self.env.ref('stock.incoterm_EXW')
	    return default_incoterm_id

	incoterm = fields.Many2one('stock.incoterms', 'Incoterms', help="International Commercial Terms are a series of predefined commercial terms used in international transactions.", default=_get_default_incoterm)
	confirm_order = fields.Datetime(string='Confirm Date', index=True, copy=False)

	@api.multi
	def action_confirm(self):
		for order in self:
			if order.state == 'sale' and order.date_order:
				order.confirm_order = order.date_order
			else:
				order.confirm_order = fields.Datetime.now()
		return super(SaleOrder, self).action_confirm()

class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"

	@api.model
	def _get_default_dropship_route(self):
	    default_dropship_id = self.env.ref('stock_dropshipping.route_drop_shipping')
	    return default_dropship_id

	route_id = fields.Many2one('stock.location.route', string='Route', domain=[('sale_selectable', '=', True)], default=_get_default_dropship_route)
