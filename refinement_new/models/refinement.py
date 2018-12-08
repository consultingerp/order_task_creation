# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import Warning
from lxml import etree
import datetime
import time

class BrandingPosition(models.Model):
    _name = 'branding.position'
    _description = 'Branding'
    _order = "name"
          
    name = fields.Char(string="Branding Position", required=True)
    product_id = fields.Many2one('product.product', string="SKU", required=True)
    branding_ids = fields.Many2many('branding.item', 'branding_position_rel', 'position_id', 'brand_item', string="Branding Item", required=True)

    @api.model
    def create(self, vals):
        position = super(BrandingPosition, self).create(vals)
        for branding_id in position.branding_ids:
            branding_id.position_id = position.id
        return position
    @api.multi
    def write(self, vals):
        return super(BrandingPosition, self).write(vals)

    @api.multi
    def unlink(self):
        return super(BrandingPosition, self).unlink()

 
class BrandingItem(models.Model):
    _name='branding.item'
    # _rec_name = 'brand_item'

    name = fields.Char(help="Name", required=True)
    brand_item = fields.Char(string="Branding Item")
    pre_cost_ids = fields.Many2many('pre.cost', 'precost_rel', 'branding_id', 'pre_cost_id', string="Pre Cost")
    no_color = fields.Integer(string="Number of Color", help="Number of color per item")
    selling_price = fields.Float(string="Selling Price")
    purchase_price = fields.Float(string="Purchase Price")
    product_id = fields.Many2one("product.product", string="SKU")
    # position_ids = fields.Many2one('branding.position', string="Branding Position")

    @api.model
    def create(self, vals):
        Product = self.env['product.product']
        product_vals = {'name': vals.get('name'), 'default_code':vals.get('brand_item'), 'type':'consu', 'list_price': vals.get('selling_price'), 'standard_price': vals.get('purchase_price')}
        product_id = Product.create(product_vals)
        vals.update({'name': vals.get('name'),'product_id':product_id.id})
        return super(BrandingItem, self).create(vals)

    @api.multi
    def write(self, vals):
        return super(BrandingItem, self).write(vals)

    @api.multi
    def unlink(self):
        for record in self:
            record.product_id.unlink()
        return super(BrandingItem, self).unlink()

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        context = dict(self._context) or {}
        brand_ids = []
        Product = self.env['product.product'].browse(context.get('product_id'))
        sql_query = """ SELECT brand_item from branding_position_rel where position_id = %s """
        # for getting the branding item from the 
        if context.get('model') == 'sol' and not context.get('product_id') and not context.get('position_id'):
            position_ids = self.env['branding.position'].search([])
            for position in position_ids:
                self.env.cr.execute(sql_query, (position.id,))
                result_query = self.env.cr.dictfetchall()
                for brand_id in result_query:
                    brand_ids.append(brand_id['brand_item'])
            args.append(['id','in',brand_ids])
        # for getting the branding item from the position id if selected
        elif context.get('model') == 'sol' and context.get('position_id'):
            position_id  = context.get('position_id')
            self.env.cr.execute(sql_query, (position_id,))
            result_query = self.env.cr.dictfetchall()
            for brand_id in result_query:
                brand_ids.append(brand_id['brand_item'])
            args.append(['id','in',brand_ids])
        # for getting the branding item from the products only
        elif context.get('model') == 'sol' and context.get('product_id') and not context.get('position_id'):
            for brand_id in Product.branding_ids:
                brand_ids.append(brand_id.id)
            args.append(['id','in',brand_ids])

        recs = self.search(args, limit=limit)
        return recs.name_get()

    @api.multi
    @api.depends('name', 'title')
    def name_get(self):
        context = dict(self._context) or {}
        result = []
        for item in self:
            name = item.name
            if context.get('model') == 'sol':
                name = item.name
            result.append((item.id, name))
        return result


class PreCost(models.Model):
    _name='pre.cost'
    _rec_name = 'pre_cost'

    name = fields.Char(required=True)
    pre_cost = fields.Char(string="PreCost ID")
    is_variable_cost = fields.Boolean(string="Is Variable Cost")
    is_optional = fields.Boolean(string="Is Option")
    selling_price = fields.Float(string="Selling Price")
    purchase_price = fields.Float(string="Purchase Price")
    product_id = fields.Many2one("product.product", string="Product ID")

    @api.model
    def create(self, vals):
        Product = self.env['product.product']
        precost_name = ''
        if vals.get('is_optional') == True:
            precost_name = vals.get('name') + '(optional)'
        else:
            precost_name = vals.get('name')
        product_vals = {'name': precost_name,'default_code':vals.get('pre_cost'), 'type':'consu', 'list_price': vals.get('selling_price'), 'standard_price': vals.get('purchase_price')}
        product_id = Product.create(product_vals)
        vals.update({'name': precost_name ,'product_id':product_id.id})
        return super(PreCost, self).create(vals)

    @api.multi
    def write(self, vals):
        for record in self:
            if vals.get('is_optional') == True: 
                record.product_id.is_optional = True
            if vals.get('is_optional') == False:
                record.product_id.is_optional = False
        return super(PreCost, self).write(vals)

    @api.multi
    def unlink(self):
        for record in self:
            record.product_id.unlink()
        return super(PreCost, self).unlink()


class HandlingGroup(models.Model):
    _name='handling.group'
    _rec_name = 'handle_grp'

    name = fields.Char(required=True)
    handle_grp = fields.Char(string="Handling Group ID")
    selling_price = fields.Float(string="Selling Price")
    purchase_price = fields.Float(string="Purchase Price")
    product_id = fields.Many2one("product.product", string="Product ID")

    @api.model
    def create(self, vals):
        Product = self.env['product.product']
        product_vals = {'name': vals.get('name'), 'default_code':vals.get('handle_grp'), 'type':'consu', 'list_price': vals.get('selling_price'), 'standard_price': vals.get('purchase_price')}
        product_id = Product.create(product_vals)
        vals.update({'name': vals.get('name'), 'product_id':product_id.id})
        return super(HandlingGroup, self).create(vals)

    @api.multi
    def write(self, vals):
        return super(HandlingGroup, self).write(vals)

    @api.multi
    def unlink(self):
        for record in self:
            record.product_id.unlink()
        return super(HandlingGroup, self).unlink()