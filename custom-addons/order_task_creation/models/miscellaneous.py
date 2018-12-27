# -*- coding: utf-8 -*-

from odoo import models, fields


class miscellaneous_entry(models.Model):
    _name='miscellaneous.entry'
    
    name=fields.Char('Name')


class misc_supplier_payment(models.Model):
    _name='misc.supplier.payment'
    
    name=fields.Char('Name')


class digital_sample(models.Model):
    _name='digital.sample'
    
    name=fields.Char('Name')


class sample(models.Model):
    _name='sample.sample'
    
    name=fields.Char('Name')    
