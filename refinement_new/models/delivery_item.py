# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _

class DeliveryItem(models.Model):
	_name = 'delivery.item'
	_order = 'name'

	name = fields.Char('Delivery Time', translate=True)

