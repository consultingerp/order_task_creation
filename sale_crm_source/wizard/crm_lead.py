# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp.osv import fields, osv
from openerp.tools.translate import _

class crm_merge_opportunity(osv.osv_memory): 
	_inherit = 'crm.merge.opportunity'

	def action_merge(self, cr, uid, ids, context=None):
		context = dict(context or {})

		lead_obj = self.pool.get('crm.lead')
		wizard = self.browse(cr, uid, ids[0], context=context)
		opportunity2merge_ids = wizard.opportunity_ids

		#TODO: why is this passed through the context ?
		context['lead_ids'] = [opportunity2merge_ids[0].id]

		merge_id = lead_obj.merge_opportunity(cr, uid, [x.id for x in opportunity2merge_ids], wizard.user_id.id, wizard.team_id.id, context=context)

		# The newly created lead might be a lead or an opp: redirect toward the right view
		merge_result = lead_obj.browse(cr, uid, merge_id, context=context)

		if merge_result.type == 'opportunity':
			return lead_obj.redirect_opportunity_view(cr, uid, merge_id, context=context)
		else:
			return lead_obj.redirect_lead_view(cr, uid, merge_id, context=context)