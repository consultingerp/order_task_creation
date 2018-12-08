# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp import api, fields, models, _
from openerp.tools import float_is_zero, float_compare
from openerp.tools.misc import formatLang

from openerp.exceptions import UserError, RedirectWarning, ValidationError

import openerp.addons.decimal_precision as dp

class AccountInvoice(models.Model):
	_inherit = "account.invoice"

	emp_email = fields.Char(string="Employee E-mail", compute="_get_user_email")
	layout_product = fields.Char(compute="_get_main_product_id", string="Layout Product")
	delivery_condition = fields.Char(string='Delivery Time', translate=True, default="About 3-5 weeks after order clarity")

	@api.multi
	def _get_user_email(self):
		Employee = self.env['hr.employee']
		emp_email = Employee.search([('user_id','=', self.user_id.id)], limit=1).work_email
		self.emp_email = emp_email

	def find_translation(self):
		vals = []
		Tranlation = self.env['ir.translation']
		del_tran =''
		if self.partner_id.lang == 'de_DE':
			del_tran = Tranlation.search([('source', '=', 'About 3-4 weeks after order clarity')], limit=1).value
		else:
			del_tran = Tranlation.search([('source', '=', 'About 3-4 weeks after order clarity')], limit=1).source
		print "del_tran::::",del_tran
		vals.append(str(del_tran))
		return vals

	def find_del_tran(self):
		vals = []
		Tranlation = self.env['ir.translation']
		del_tran =''
		if self.partner_id.lang == 'de_DE':
			del_tran = Tranlation.search([('source', '=', 'EX WORKS')], limit=1).value
		else:
			del_tran = Tranlation.search([('source', '=', 'EX WORKS')], limit=1).source
		print "del_tran::::",del_tran
		vals.append(str(del_tran))
		return vals

	@api.multi
	def _get_main_product_id(self):
		SaleOrder = self.env['sale.order']
		layout_product = SaleOrder.search([('name','=', self.origin)], limit=1).layout_product
		self.layout_product = layout_product

	# @api.multi
	# def invoice_print(self):
	#     """ Print the invoice and mark it as sent, so that we can see more
	#         easily the next step of the workflow
	#     """
	#     self.ensure_one()
	#     self.sent = True
	#     return self.env['report'].get_action(self, 'source_reports.report_saleorder_invoice_custome')

	@api.multi
	def _find_account_number(self):
		bank_details = []
		PartnerBank = self.env['res.partner.bank']
		Bank = PartnerBank.search([('company_id', '=', self.env.user.company_id.id)], limit=1)
		bank_details.append({'acc_number': Bank.acc_number, 'bank_name' : Bank.bank_name, 'bic_number': Bank.bank_bic})
		return bank_details
