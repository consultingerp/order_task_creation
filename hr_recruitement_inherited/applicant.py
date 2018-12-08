# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from openerp import api, fields, models, tools
from openerp.tools.translate import _
from openerp.exceptions import UserError

class Applicant(models.Model):
    _inherit = "hr.applicant"

    def create(self, vals):
    	new_application = super(Applicant, self).create(vals)
    	print "new_application"
    	return new_application