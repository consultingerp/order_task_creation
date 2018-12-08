# -*- coding: utf-8 -*-

from openerp import api, models, fields, _

class product_template(models.Model):
	_inherit = "product.template"

	vendor_sku = fields.Char('Vendor SKU')


class product_product(models.Model):
    _inherit = "product.product"

	# vendor_sku = fields.Char('Vendor SKU')

