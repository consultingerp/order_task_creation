# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.tools.translate import _
import base64

class product_template(models.Model):
	_inherit="product.template"

	handling_group_id = fields.Many2one('handling.group', string='Handling Group')
	branding_ids = fields.Many2many('branding.item', 'branding_item_rel', 'product_id', 'brand_id', string="Branding Items")
	is_optional = fields.Boolean(string="Optional")
	brand = fields.Char(string="Brand", index=True)
	cat_page = fields.Char(string="Catalouge Page")
	material = fields.Char(string="Material")
	chara = fields.Char(string="Characteristics")
	dimension = fields.Char(string="Dimension")
	is_refinery = fields.Boolean(string="Is Refinery")
	is_template = fields.Boolean("Template Product", default=False)
	cust_terif_num = fields.Char(string="Customs Tariffs Number")
	mfg_country = fields.Many2one('res.country', string="Country of Manufacturer")
	self_life = fields.Char(string="Shelf Life")
	brand_inf = fields.Char(string=" Branding Information")

class product_product(models.Model):
	_inherit="product.product"

	is_template = fields.Boolean("Template Product", related='product_tmpl_id.is_template', default=False)


