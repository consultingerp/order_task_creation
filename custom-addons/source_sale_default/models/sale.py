# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


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
        default_incoterm_id = self.env.ref('account.incoterm_EXW')
        return default_incoterm_id

    incoterm = fields.Many2one('account.incoterms',
                               default=_get_default_incoterm)

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.state == 'sale' and order.date_order:
                order.confirmation_date = order.date_order
        return res

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _get_default_dropship_route(self):
        default_dropship_id = self.env.ref(
            'stock_dropshipping.route_drop_shipping')
        return default_dropship_id

    route_id = fields.Many2one('stock.location.route', string='Route',
                               domain=[('sale_selectable', '=', True)],
                               default=_get_default_dropship_route)
