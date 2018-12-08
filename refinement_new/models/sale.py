# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, float_round, DEFAULT_SERVER_DATETIME_FORMAT
from collections import OrderedDict


class SaleOrder(models.Model):
	_inherit = "sale.order"

	@api.model
	def _get_default_delivery(self):
		delivery_condition = 'About 3-5 weeks after order clarity'
		if self.env.user.lang == 'de_DE' or self.partner_id and self.partner_id.lang == 'de_DE':
			delivery_condition = 'Ca. 3-5 Wochen nach Auftragsklarheit'
		return delivery_condition

	refine_brand_ids = fields.One2many('refine.branding.line', 'sale_id', string='Refinement Lines', copy=False)
	refine_total = fields.Float(string='Total', store=True, readonly=True, compute='_compute_total', copy=False)
	margin = fields.Monetary(compute='_product_margin', help="It gives profitability by calculating the difference between the Unit Price and the cost.", currency_field='currency_id', digits=dp.get_precision('Product Price'))
	emp_email = fields.Char(string="Employee E-mail", compute="_get_user_email")
	layout_product = fields.Char(compute="set_layout_prodyct", string="Layout Product")
	sale_line_id = fields.Many2one('sale.order.line', compute="_set_product_line_id", string="Main Product Line")
	show_tier_price = fields.Boolean("Show Tier Price", default=True, help="Check for showing Tier prices on Layout Quotation")
	delivery_condition = fields.Char(compute='get_delivery_condition', string='Delivery Time', readonly=False, store=True, default=lambda self: self._get_default_delivery())

	@api.multi
	@api.onchange('partner_id')
	def onchange_partner_id(self):
		context = self.env.context or {}
		super(SaleOrder, self).onchange_partner_id()
		delivery_condition = 'About 3-5 weeks after order clarity'
		if context.get('lang') == 'de_DE':
			delivery_condition = 'Ca. 3-5 Wochen nach Auftragsklarheit'
		
		if self.partner_id and self.partner_id.lang == 'de_DE' and self.user_id.lang == 'de_DE':
			delivery_condition = 'Ca. 3-5 Wochen nach Auftragsklarheit'
		elif self.partner_id and self.partner_id.lang == 'de_DE' and self.user_id.lang != 'de_DE':
			delivery_condition = 'Ca. 3-5 Wochen nach Auftragsklarheit'
		elif self.partner_id and self.partner_id.lang == 'en_US' and self.user_id.lang != 'en_US':
			delivery_condition = 'About 3-5 weeks after order clarity'
		self.delivery_condition = delivery_condition

	@api.multi
	def get_delivery_condition(self):
		context = self.env.context or {}
		condition = 'About 3-5 weeks after order clarity'
		for order in self:
			if order.partner_id.lang == 'de_DE':
				condition = 'Ca. 3-5 Wochen nach Auftragsklarheit'
		self.delivery_condition = condition

	@api.multi
	def action_quotation_send(self):
		self.ensure_one()
		'''  Override to use a modified template that includes a portal signup link '''
		action_dict = super(SaleOrder, self).action_quotation_send()
		try:
			template_id = self.env.ref('refinement_new.email_template_edi_sale_layout').id
			# assume context is still a dict, as prepared by super
			ctx = action_dict['context']
			ctx['default_template_id'] = template_id
			ctx['default_use_template'] = True
			action_dict.update(context = ctx)
		except Exception:
			pass
		return action_dict

	@api.one
	@api.depends('order_line.branding_id','order_line.brand_pos_id','order_line.product_id')
	def _set_product_line_id(self):
		SaleLine = self.env['sale.order.line']
		if len(self.order_line) and isinstance(self.id, int):
			# Need to check the branding id and position id for the getting the template product
			#Set the line id based on 2 conditions should not be template product
			# should not be branding 
			if any(line.branding_id for line in self.mapped('order_line')):
				self._cr.execute("SELECT min(id) from sale_order_line where order_id = %s and branding_id is not NULL and brand_pos_id is not NULL" % self.id)
			else:
				self._cr.execute("SELECT min(id) from sale_order_line where order_id = %s" % self.id)
			result_query = self._cr.dictfetchall()
			line_id = result_query and result_query[0]['min']
			if line_id:
				self.sale_line_id = SaleLine.browse(line_id)

	@api.multi
	def set_layout_prodyct(self):
		for order in self:
			if len(order.order_line):
				for product in order.mapped('order_line')[0].product_id:	
					order.layout_product= product.name

	@api.multi
	def find_payment_term_trans(self):
		Translation = self.env['ir.translation']
		vals = []
		translation = ''
		for order in self:
			if self.env.user.lang != 'de_DE' and order.partner_id.lang == 'de_DE':
				translation = Translation.search([('source', '=', order.payment_term_id.name)], limit=1).value
			elif self.env.user.lang == 'de_DE' and order.partner_id.lang == 'de_DE':
				translation = Translation.search([('value', '=', order.payment_term_id.name)], limit=1).value
			elif self.env.user.lang == 'en_US' and order.partner_id.lang == 'en_US':
				translation = Translation.search([('source', '=', order.payment_term_id.name)], limit=1).source
			elif self.env.user.lang == 'de_DE' and order.partner_id.lang != 'de_DE':
				translation = Translation.search([('value', '=', order.payment_term_id.name)], limit=1).source				
			vals.append(translation)
		return vals

	@api.multi
	def find_del_tran(self):
		context = self.env.context or {}
		vals = []
		Translation = self.env['ir.translation']
		del_tran =''
		for order in self:
			if order.partner_id.lang == 'de_DE' and order.user_id.lang != 'de_DE':
				del_tran = Translation.search([('source', '=', order.incoterm.name),('lang','=','de_DE')],limit=1).value
			elif order.partner_id.lang == 'de_DE' and order.user_id.lang == 'de_DE':
				del_tran = order.incoterm.name
			elif order.partner_id.lang != 'de_DE' and order.user_id.lang == 'de_DE':
				del_tran = Translation.search([('value', '=', order.incoterm.name)],limit=1).source
			vals.append(str(del_tran))
		return vals

	@api.multi
	def find_translation_footer1(self):
		vals = []
		footer1 =''
		for order in self:
			if order.partner_id.lang == 'de_DE':
				footer1 = "Kontaktieren Sie uns, wenn Sie Fragen zum Angebot oder veränderte Projektanforderungen haben."
				footer2 = "Wir beraten Sie gerne. Wir sind telefonisch erreichbar von Mo-Fr. von 8:00 bis 18:00 Uhr."
			else:
				footer1 = 'Please contact us in case you have questions regarding your quotation or changed project requirements.'
				footer2 = 'We are happy to consult you. Our office hours are Mo-Fr. 8:00 to 18:00.'
			vals.append(str(footer1))
			vals.append(str(footer2))
		return vals

	@api.multi
	def find_translation_footer2(self):
		vals = []
		footer2 =''
		for order in self:
			if order.partner_id.lang == 'de_DE':
				footer1 = 'Der Zwischenverkauf ist vorbehalten. Aus technischen Gründen behalten wir uns die Mehr- oder Minderlieferung von 10% vor.Bei einer Minderlieferung erstellen wir Ihnen eine entsprechende Gutschrift. Eine Nachproduktion oder Ähnliches ist ausgeschlossen.'
				footer2 = 'Bei einer Mehrlieferung wird Ihnen diese entsprechend berechnet.'
			else:
				footer1 = 'For technical reasons, we reserve the right to make a short or excess delivery of up to 10%.Any additional costs incurred by film or repro work will be charged additionally.'
				footer2 = 'We refund the difference in case of a short delivery.'
			vals.append(str(footer1))
			vals.append(str(footer2))
		return vals

	@api.multi
	def _get_user_email(self):
		Employee = self.env['hr.employee']
		emp_email = Employee.search([('user_id','=', self.user_id.id)], limit=1).work_email
		self.emp_email = emp_email

	@api.depends('refine_brand_ids.subtotal')
	def _compute_total(self):
		"""
		Compute the total amounts of the Refinement Line.
		"""
		for order in self:
			amount_total = 0.0
			for line in order.refine_brand_ids:
				amount_total += line.subtotal
			order.update({
			    'refine_total': order.pricelist_id.currency_id.round(amount_total),
			})

	@api.depends('refine_brand_ids.tax_id', 'refine_brand_ids.qty', 'refine_brand_ids.unit_price')
	def compute_refine_tax(self):
		refine_tax_amount = 0.0
		for refine_line in self.refine_brand_ids:
			# refine_price = refine_line.unit_price
			for line_tax_id in refine_line.tax_id:
				refine_taxes = line_tax_id.compute_all(refine_line.unit_price, refine_line.sale_id.currency_id, refine_line.qty, product=refine_line.product_id, partner=refine_line.sale_id.partner_id)
				refine_tax_amount += sum(t.get('amount', 0.0) for t in refine_taxes.get('taxes', []))
		return refine_tax_amount			

	@api.depends('order_line.price_total', 'refine_total' )
	def _amount_all(self):
		"""
		Compute the total amounts of the SO.
		"""
		for order in self:
			amount_untaxed = amount_tax = 0.0
			refine_tax_amount = order.compute_refine_tax()
			# refine_tax_amount = 0.0
			for line in order.order_line:
				amount_untaxed += line.price_subtotal
				# FORWARDPORT UP TO 10.0
				if order.company_id.tax_calculation_rounding_method == 'round_globally':
					price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
					taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
					amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
				else:
					amount_tax += line.price_tax
			if refine_tax_amount:
				amount_tax+=refine_tax_amount
			if order.refine_total:
				amount_untaxed = order.refine_total + amount_untaxed
			order.update({
			'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
			'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
			'amount_total': amount_untaxed + amount_tax,
			})

	@api.multi
	def reset_lines(self):
		if len(self.mapped('refine_brand_ids')) >=1:
			for line in self.mapped('refine_brand_ids'):
				line.unlink()
		else:
			raise UserError(_('Nothing to reset'))

		return True

	def _get_price(self, pricelist, product, qty):
		sale_price_digits = self.env['decimal.precision'].precision_get('Product Price')
		price = pricelist.price_get(product.id, qty, False)
		if not price:
			price = product.list_price
		return float_round(price, precision_digits=sale_price_digits)

	@api.one
	def find_nearest_sale_qty(self, array, value):
		n = [abs(i-value) for i in array]
		idx = n.index(min(n))
		return array[idx]

	@api.one
	def find_nearest_pur_qty(self, array, value):
		n = [abs(i-value) for i in array]
		idx = n.index(min(n))
		return array[idx]

	@api.one
	def find_sale_price(self, product_id, qty=0.0, pricelist_id=False):
		ctx = self.env.context.copy()
		frm_cur = self.env.user.company_id.currency_id
		to_cur = self.pricelist_id.currency_id
		price = 0.0
		item_price_range =[]
		if product_id.item_ids and qty>1:
			for item in product_id.mapped('item_ids'):
				item_price_range.append(item.min_quantity)
			for item in product_id.mapped('item_ids'):
				if item.min_quantity == qty:
					price = frm_cur.with_context(ctx).compute(item.fixed_price, to_cur, round=False)
				else:
					nearest_item_qty = self.find_nearest_sale_qty(item_price_range, qty)
					if item.min_quantity == nearest_item_qty[0]:
						price = frm_cur.with_context(ctx).compute(item.fixed_price, to_cur, round=False)
		else:
			price = frm_cur.with_context(ctx).compute(product_id.list_price, to_cur, round=False)
		return price

	def find_cost_price(self, product_id, qty=0.0):
		ctx = self.env.context.copy()
		frm_cur = self.env.user.company_id.currency_id
		to_cur = self.pricelist_id.currency_id
		cost_price = 0.0
		item_price_range =[]
		if product_id.seller_ids and qty>1:
			for seller in product_id.mapped('seller_ids'):
				item_price_range.append(seller.min_qty)
			for seller in product_id.mapped('seller_ids'):
				if seller.min_qty == qty:
					 cost_price = frm_cur.with_context(ctx).compute(seller.price, to_cur, round=False)
				else:
					nearest_item_qty = self.find_nearest_pur_qty(item_price_range, qty)
					if seller.min_qty == nearest_item_qty[0]:
						cost_price = frm_cur.with_context(ctx).compute(seller.price, to_cur, round=False)
		else:
			cost_price = frm_cur.with_context(ctx).compute(product_id.standard_price, to_cur, round=False)
		return cost_price


	@api.multi
	def compute_refinement_lines(self):
		line_ids = []
		RefineLine = self.env['refine.branding.line']
		BrandLine = self.env['branding.item']
		PreCost = self.env['refine.branding.line']
		HandleGroup = self.env['refine.branding.line']
		refine_vals = {}
		refine_line_ids = []
		pre_cost_list = []
		pos_vals = {}
		handle_vals = {}
		price_unit = 0.00
		pos_price_unit = 0.00
		pre_price_unit = 0.00
		# if refinement lines exist system will ask 
		# to reset first to compute the refinement lines
		if len(self.refine_brand_ids):
			raise UserError(_('Please reset the refinement lines to compute the Refinement Cost.'))
			return False
		count = 0
		for line in self.order_line:
			# Testing for loop run time, use count
			count+=1
			# if not line.branding_id and not line.brand_pos_id:
			# 	raise UserError(_('Please check for the Branding and Position in Sale Line to compute the Refinement Cost.'))
			if line.brand_pos_id and line.branding_id or line.brand_pos_id or line.branding_id:
				#create refinement lines
				#prepare refine Vals
				if line.product_id.handling_group_id:
					if line.order_id.pricelist_id and line.order_id.partner_id:
						# price_unit = self._get_price(line.order_id.pricelist_id,line.product_id.handling_group_id.product_id, line.product_uom_qty )
						product = line.product_id.handling_group_id.product_id.with_context(
						    lang=line.order_id.partner_id.lang,
						    partner=line.order_id.partner_id.id,
						    quantity=line.product_uom_qty,
						    date_order=line.order_id.date_order,
						    pricelist=line.order_id.pricelist_id.id,
						    uom=line.product_uom.id,
						    fiscal_position=self.env.context.get('fiscal_position')
						)
						price_unit = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id, line.tax_id)
						vendor = line.product_id.handling_group_id.product_id.seller_ids
						vendor_id = vendor and vendor[0].name
						seller = line.product_id.handling_group_id.product_id._select_seller(
								line.product_id.handling_group_id.product_id,
								partner_id=vendor_id,
								quantity=line.product_uom_qty,
								date=line.order_id.date_order,
								uom_id=line.product_uom)
						if not seller:
							cost_price = line.product_id.handling_group_id.product_id.standard_price
						else:
							cost_price = self.env['account.tax']._fix_tax_included_price(seller.price, line.product_id.handling_group_id.product_id.supplier_taxes_id, line.tax_id)
						# cost_price = self.env['account.tax']._fix_tax_included_price(seller.price, line.product_id.handling_group_id.product_id.supplier_taxes_id, self.taxes_id) if seller else 0.0
					# price_unit = self.find_sale_price(line.product_id.handling_group_id.product_id, qty=line.product_uom_qty, pricelist_id=False)
					# cost_price = self.find_cost_price(line.product_id.handling_group_id.product_id, qty=line.product_uom_qty)

					handle_vals = {'product_id': line.product_id.handling_group_id.product_id.id,
								'position_id': line.brand_pos_id.id,
								'branding_id': line.branding_id.id,
								'qty': line.product_uom_qty,
								'product_uom_id':line.product_id.handling_group_id.product_id.uom_id.id,
								'unit_price':  price_unit,
								'cost_price': cost_price,
								'sale_id': line.order_id.id,
								'sale_line_id': line.id,
								'line_id': line.id,
				}
				if line.branding_id.product_id:
					if line.order_id.pricelist_id and line.order_id.partner_id:
						product = line.branding_id.product_id.with_context(
						    lang=line.order_id.partner_id.lang,
						    partner=line.order_id.partner_id.id,
						    quantity=line.product_uom_qty,
						    date_order=line.order_id.date_order,
						    pricelist=line.order_id.pricelist_id.id,
						    uom=line.product_uom.id,
						    fiscal_position=self.env.context.get('fiscal_position')
						)
						pos_price_unit = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id, line.tax_id)
						vendor = line.branding_id.product_id.seller_ids
						pos_vendor_id = vendor and vendor[0].name
						seller = line.branding_id.product_id._select_seller(
								line.branding_id.product_id,
								partner_id=pos_vendor_id,
								quantity=line.product_uom_qty,
								date=line.order_id.date_order,
								uom_id=line.product_uom)
						if not seller:
							cost_price = line.branding_id.product_id.standard_price
						else:
							cost_price = self.env['account.tax']._fix_tax_included_price(seller.price, line.branding_id.product_id.supplier_taxes_id, line.tax_id)
					# pos_price_unit = self.find_sale_price(line.branding_id.product_id, qty=line.product_uom_qty, pricelist_id=False)
					# cost_price = self.find_cost_price(line.branding_id.product_id, qty=line.product_uom_qty)
					pos_vals = {'product_id': line.branding_id.product_id.id,
									'position_id': line.brand_pos_id.id,
									'branding_id': line.branding_id.id,
									'qty': line.product_uom_qty,
									'product_uom_id':line.branding_id.product_id.uom_id.id,
									'unit_price': pos_price_unit,
									'cost_price':cost_price,
									'sale_id': line.order_id.id,
									'sale_line_id': line.id,
									'line_id': line.id,
					}
				for pre_cost in line.branding_id.mapped('pre_cost_ids'):
					qty = 0.0
					optional = False
					if pre_cost.is_optional == True:
						optional = True
					if pre_cost.is_variable_cost == True:
						qty = line.branding_id.no_color
					else:
						qty = 1.0
					if line.order_id.pricelist_id and line.order_id.partner_id:
						product = pre_cost.product_id.with_context(
						    lang=line.order_id.partner_id.lang,
						    partner=line.order_id.partner_id.id,
						    quantity=qty,
						    date_order=line.order_id.date_order,
						    pricelist=line.order_id.pricelist_id.id,
						    uom=line.product_uom.id,
						    fiscal_position=self.env.context.get('fiscal_position')
						)
						pre_price_unit = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id, line.tax_id)
						vendor = pre_cost.product_id.seller_ids
						pre_vendor_id = vendor and vendor[0].name
						seller = pre_cost.product_id._select_seller(
								pre_cost.product_id,
								partner_id=pre_vendor_id,
								quantity=qty,
								date=line.order_id.date_order,
								uom_id=line.product_uom)
						if not seller:
							cost_price = pre_cost.product_id.standard_price
						else:
							cost_price = self.env['account.tax']._fix_tax_included_price(seller.price, pre_cost.product_id.supplier_taxes_id, line.tax_id)
						# pre_price_unit = self._get_price(line.order_id.pricelist_id,pre_cost.product_id, qty )
					# pre_price_unit = self.find_sale_price(pre_cost.product_id, qty=qty, pricelist_id=False)
					# cost_price = self.find_cost_price(pre_cost.product_id, qty=qty)

					pre_cost_vals = {'product_id': pre_cost.product_id.id,
										'is_optional': optional,
										'position_id': line.brand_pos_id.id,
										'branding_id': line.branding_id.id,
										'qty': qty,
										'product_uom_id':pre_cost.product_id.uom_id.id,
										'unit_price': pre_price_unit,
										'cost_price': cost_price,
										'sale_id': line.order_id.id,
										'sale_line_id': line.id,
										'line_id': line.id,
					}
					refine_line_ids.append((0, 0, pre_cost_vals))
				if line.product_id.handling_group_id:
					refine_line_ids.append((0, 0, handle_vals))
				if line.branding_id.product_id:
					refine_line_ids.append((0, 0, pos_vals))
				line.order_id.refine_brand_ids = refine_line_ids
		count+=1
		return True

	@api.multi
	def write(self, vals):
		return super(SaleOrder, self).write(vals)

	@api.multi
	def _get_product_variants(self):
		vals = []
		for line in self.mapped('order_line'):
			if line.product_id.attribute_value_ids:
				for attr in line.product_id.mapped('attribute_value_ids'):
					vals.append({'attribute' : attr.attribute_id.name, 'value' : attr.name})
		return vals

	@api.multi
	def _get_product_pricelist(self):
		#Getting pricelist item for the report
		vals = []
		for line in self.mapped('order_line'):
			# OrderedDict(sorted(a.items(), key=lambda x: x[0]))
			for product_price_list_item in line.product_id.mapped('item_ids').sorted(key=lambda b: b.min_quantity):
			    # if line.product_id.product_tmpl_id == price_list_item.product_tmpl_id:
				vals.append({'item_name': product_price_list_item.min_quantity, 'price':product_price_list_item.fixed_price})
		return vals

	@api.depends('order_line.margin', 'refine_brand_ids.margin')
	def _product_margin(self):
		# Calculating margin on sales order including the marging on the refinement lines
		result = {}
		refine_margin = 0.0
		sale_margin = 0.0
		Currency = self.env['res.currency']
		# currency = self.pricelist_id.currency_id
		for refine_line in self.mapped('refine_brand_ids'):
			refine_margin += refine_line.margin
		for sale in self:
			for line in sale.order_line:
				if line.state == 'cancel':
					continue
				sale_margin += line.margin
			sale.margin = sale_margin + refine_margin
			

class RefineBrandLine(models.Model):
	_name = 'refine.branding.line'

	@api.depends('qty', 'cost_price', 'unit_price','subtotal')
	def _product_margin(self):
		cur_obj = self.env['res.currency']
		line_margin = 0.0
		tmp_margin = 0.0
		for line in self:
			if line.product_id:
				tmp_margin = (line.subtotal - (line.cost_price * line.qty))
				line_margin= line.sale_id.pricelist_id.currency_id.round(tmp_margin)
			line.margin = tmp_margin

	product_id = fields.Many2one('product.product', string='Product')
	position_id = fields.Many2one('branding.position', string='Branding Position')
	branding_id = fields.Many2one('branding.item', string='Branding Item')
	precost_id = fields.Many2one('pre.cost', string='PreCost ID')
	qty = fields.Float(string='Quantity',digits=dp.get_precision('Product Unit of Measure'))
	product_uom_id = fields.Many2one('product.uom', string='Unit of Measure', required=True)
	unit_price = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'))
	subtotal = fields.Monetary(string='Subtotal', compute='_compute_subtotal', store=True)
	sale_id = fields.Many2one('sale.order', string='Sale Order')
	is_optional = fields.Boolean(string="Optional")
	tax_id = fields.Many2many('account.tax', string='Taxes', compute="_compute_tax_id")
	price_tax = fields.Monetary(compute='_compute_tax_amount', string='Taxes Amount', readonly=True, store=True)
	sale_line_id = fields.Many2one('sale.order.line', string="Sale Order Line")
	line_id = fields.Integer(string="Sale Line ID")
	currency_id = fields.Many2one(related='sale_line_id.order_id.currency_id', store=True, string='Currency', readonly=True)
	margin = fields.Monetary(compute='_product_margin', help="It gives profitability by calculating the difference between the Unit Price and the cost.", currency_field='currency_id', digits=dp.get_precision('Product Price'), store=True)	
	cost_price = fields.Float(string="Cost price")
	route_id = fields.Many2one(related='sale_line_id.route_id', string="Route")

	@api.depends('qty', 'unit_price')
	def _compute_subtotal(self):
		for line in self:
		    line.update({
		        'subtotal': line.qty * line.unit_price,
		    })

	@api.multi
	def refinement_calculator(self):
		#Deprecated method from the old refinement calculator #No use in new
		subtotal = 0.0
		refinery_qty = self.order_id.main_refine_qty
		for line in self:
			if line.product_id.factor == 'main':
				subtotal = line.product_uom_qty * line.product_id.lst_price
			elif line.product_id.factor == 'per_no':
				# Fix the code by Finding the main refinery product and use the number of color
				# multiply the num of color into the subtotal calculation
				if len(line.order_id.main_refine_product_ids)>=1:
					for product in line.order_id.main_refine_product_ids:
						# line_total = line.product_id.lst_price * product.no_colors
						subtotal = line.product_uom_qty * line.product_id.lst_price
				elif line.order_id.main_refine_product_id:  
					# line_total =  line.product_id.lst_price * line.order_id.main_refine_product_id.no_colors
					subtotal = line.product_uom_qty * line.product_id.lst_price
			elif line.product_id.factor == 'fixed':
				subtotal = line.product_uom_qty*line.product_id.lst_price
		return subtotal 

	@api.depends('qty', 'unit_price', 'tax_id')
	def _compute_tax_amount(self):
		for line in self:
			price = line.unit_price
			taxes = line.tax_id.compute_all(price, line.sale_id.currency_id, line.qty, product=line.product_id, partner=line.sale_id.partner_id)
			line.update({
				'price_tax': taxes['total_included'] - taxes['total_excluded'],
			})

	@api.depends('sale_line_id.tax_id')
	def _compute_tax_id(self):
		tax_ids = []
		for line in self:
			for sale_line_tax_id in line.mapped('sale_line_id').tax_id:
				tax_ids.append(sale_line_tax_id.id)
			line.tax_id = tax_ids
			#Remove the code for adding the single tax in the refinement line
			#
			# for line in self:
			# 	fpos = line.sale_id.fiscal_position_id or line.sale_id.partner_id.property_account_position_id
			# 	# If company_id is set, always filter taxes by the company
			# 	taxes = line.product_id.taxes_id.filtered(lambda r: not line.sale_id.company_id or r.company_id == line.sale_id.company_id)
			# 	line_tax_id = fpos.map_tax(taxes) if fpos else taxes
			# 	tax_ids.append(line_tax_id.id)
			# 	print "Tax_ids:::::::::::::::::",tax_ids
			# 	line.tax_id = tax_ids

	@api.multi
	def unlink(self):
		# for line in self:
		# 	if line.pre_cost.is_optional == False:
		# 		raise UserError(_('This is mandatory cost on this branding, Please contact to System Administrator'))
		return super(RefineBrandLine, self).unlink()
	

class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"
	

	brand_pos_id = fields.Many2one('branding.position', string="Branding Position")
	branding_id = fields.Many2one('branding.item', string="Branding Item")

	@api.multi
	@api.onchange('product_id')
	def product_id_change(self):
		# Odoo Ticket:#id=2833
		res = super(SaleOrderLine, self).product_id_change()
		desc = ''
		if self.product_id.brand and len(self.product_id.brand.strip()):
			desc+= "\n" + "Brand: " + self.product_id.brand

		if self.product_id.material and len(self.product_id.material.strip()):
			desc+= "\n" + "Material: " +self.product_id.material

		if self.product_id.chara and len(self.product_id.chara.strip()):
			desc+= "\n" + "Characteristics: " +self.product_id.chara

		if self.product_id.dimension and len(self.product_id.dimension.strip()):
			desc+= "\n" + "Dimension: " +self.product_id.dimension

		if self.product_id.cust_terif_num and len(self.product_id.cust_terif_num.strip()):
			desc+= "\n" + "Customs Tariffs Number: " +self.product_id.cust_terif_num

		if self.product_id.mfg_country:
			desc+= "\n" + "Country of Manufacturer: " + self.product_id.mfg_country.name

		if self.product_id.self_life and len(self.product_id.self_life.strip()):
			desc+= "\n" + "Shelf Life: "+self.product_id.self_life

		if self.product_id.brand_inf and len(self.product_id.brand_inf.strip()):
			desc+= "\n" + "Branding Information: "+self.product_id.brand_inf

		if self.product_id.weight and self.product_id.weight > 0.0 or self.product_id.weight < 0.0:
			desc+= "\n" + "Weight: "+str(self.product_id.weight)

		if self.product_id.volume and self.product_id.volume > 0.0 or self.product_id.volume < 0.0:
			desc+= "\n" + "Volume: "+ str(self.product_id.volume)
			
		self.brand_pos_id = False 
		self.branding_id= False
		self.name = str(self.name) + str(desc)
		return res

	@api.one
	def find_nearest_pur_qty(self, array, value):
		n = [abs(i-value) for i in array]
		idx = n.index(min(n))
		return array[idx]

	# @api.model
	# def _find_cost_price(self, product, product_uom_qty, currency=False):
	# 	ctx = self.env.context.copy()
	# 	frm_cur = self.env.user.company_id.currency_id
	# 	cost_price = 0.0
	# 	item_price_range = []
	# 	if self.product_id.seller_ids and self.product_uom_qty>1:
	# 		for seller in self.product_id.mapped('seller_ids'):
	# 			item_price_range.append(seller.min_qty)
	# 		for seller in self.product_id.mapped('seller_ids'):
	# 			if seller.min_qty == product_uom_qty:
	# 				 cost_price = seller.price
	# 			else:
	# 				nearest_item_qty = self.find_nearest_pur_qty(item_price_range, product_uom_qty)
	# 				if seller.min_qty == nearest_item_qty[0]:
	# 					cost_price = seller.price
	# 	else:
	# 		cost_price = self.product_id.standard_price
	# 	return cost_price

		# 	for seller in self.product_id.mapped('seller_ids'):
		# 	for seller in self.product_id.mapped('seller_ids'):
		# 		if seller.min_qty == product_uom_qty:
		# 			 cost_price = seller.price
		# else:
		# 	cost_price = self.product_id.standard_price
		# return cost_price
    # def _suggest_quantity(self):
    #     '''
    #     Suggest a minimal quantity based on the seller
    #     '''
    #     if not self.product_id:
    #         return

    #     seller_min_qty = self.product_id.seller_ids\
    #         .filtered(lambda r: r.name == self.order_id.partner_id)\
    #         .sorted(key=lambda r: r.min_qty)
    #     if seller_min_qty:
    #         self.product_qty = seller_min_qty[0].min_qty or 1.0
    #         self.product_uom = seller_min_qty[0].product_uom
    #     else:
    #         self.product_qty = 1.0

	@api.onchange('product_id', 'product_uom','product_uom_qty')
	def product_id_change_margin(self):
		if not self.order_id.pricelist_id or not self.product_id or not self.product_uom:
			return
		# if self.product_uom_qty>1:
		# 	purchase_price = self._find_cost_price(self.product_id, self.product_uom_qty)
		# else:
		# 	purchase_price = self._compute_margin(self.order_id, self.product_id, self.product_uom)
		# self._suggest_quantity()
		vendor_id = False
		if self.product_id.seller_ids:
			vendor_id = self.product_id.seller_ids[0].name
		seller = self.product_id._select_seller(
				self.product_id,
				partner_id=vendor_id,
				quantity=self.product_uom_qty,
				date=self.order_id.date_order,
				uom_id=self.product_uom)
		if not seller:
			purchase_price = self.product_id.standard_price
		else:
			purchase_price= self.env['account.tax']._fix_tax_included_price(seller.price, self.product_id.supplier_taxes_id, self.tax_id)
		self.purchase_price = purchase_price



	# @api.model
	# def create(self, vals):
	# 	print "Vals:::::::Before:::::::::",vals
	# 	# Calculation of the margin for programmatic creation of a SO line. It is therefore not
	# 	# necessary to call product_id_change_margin manually
	# 	if 'purchase_price' not in vals:
	# 		order_id = self.env['sale.order'].browse(vals['order_id'])
	# 		product_id = self.env['product.product'].browse(vals['product_id'])
	# 		product_uom_id = self.env['product.uom'].browse(vals['product_uom'])
	# 		vals['purchase_price'] = self._compute_margin(order_id, product_id, product_uom_id)
	# 	elif vals['product_uom_qty'] > 1 and 'purchase_price' in vals:
	# 		product_id = self.env['product.product'].browse(vals['product_id'])
	# 		pricelist_currency = self.env['sale.order'].browse(vals['order_id']).pricelist_id.currency_id
	# 		purchase_price = self._find_cost_price(product_id, vals['product_uom_qty'], pricelist_currency)
	# 		print "PPPPPPPPPPPPPPPP",purchase_price
	# 		vals['purchase_price'] = purchase_price
	# 		print "vals['purchase_price']:::::::::::::::::::0",vals['purchase_price']

	# 	print "Vals::::::::AFTER::::::::",vals
	# 	print t
	# 	return super(sale_order_line, self).create(vals)

	# @api.model
	# def _get_purchase_price(self, pricelist, product, product_uom, date):
	# 	print "Purchase:::::::::::::::::::",product
	# 	ctx = self.env.context.copy()
	# 	ctx['date'] = date
	# 	frm_cur = self.env.user.company_id.currency_id
	# 	to_cur = pricelist.currency_id
	# 	purchase_price = product.standard_price
	# 	if self.product_uom_qty > 1:
	# 		purchase_price = self.find_cost_price(product, qty=self.product_uom_qty)
			
	# 	if product_uom != product.uom_id:
	# 		purchase_price = self.env['product.uom']._compute_price(product.uom_id.id, purchase_price, to_uom_id=product_uom.id)

	# 	price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
	# 	return {'purchase_price': price}

	@api.multi
	def write(self, vals):
		for line in self:
			product_uom_qty = vals['product_uom_qty'] if 'product_uom_qty' in vals else False
			if product_uom_qty >= 1 and 'purchase_price' in vals:
				product_id = vals['product_id'] if 'product_id' in vals else line.product_id
				if isinstance(product_id, (int,long)):
					product_id = self.env['product.product'].browse(product_id)
				qty = product_uom_qty
				vendor_id = product_id.seller_ids[0].name if product_id.seller_ids else False
				seller = product_id._select_seller(
						product_id,
						partner_id=vendor_id,
						quantity=line.product_uom_qty,
						date=line.order_id.date_order,
						uom_id=line.product_uom)
				vals['purchase_price'] = self.env['account.tax']._fix_tax_included_price(seller.price, product_id.supplier_taxes_id, self.tax_id) if seller else 0.0

				# vals['purchase_price'] = self.order_id.find_cost_price(product_id, qty=qty)
		return super(SaleOrderLine, self).write(vals)




