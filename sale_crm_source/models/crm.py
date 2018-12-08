# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import logging
from operator import itemgetter
from werkzeug import url_encode

from openerp import SUPERUSER_ID
from openerp import tools, api
from openerp.addons.base.res.res_partner import format_address
from openerp.addons.crm import crm_stage
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import email_re, email_split
from openerp.exceptions import UserError, AccessError


class crm_team(osv.Model):
    _inherit = "crm.team"

    def _get_default_team_id(self, cr, uid, context=None, user_id=None):
        if context is None:
            context = {}
        if 'default_team_id' in context:
            return context['default_team_id']
        if user_id is None:
            user_id = uid
        team_ids = self.search(cr, SUPERUSER_ID, ['|', ('user_id', '=', user_id), ('member_ids', '=', user_id)], limit=1, context=context)
        team_id = team_ids[0] if team_ids else False
        if not team_id and context.get('default_team_id'):
            team_id = context['default_team_id']
        if not team_id:
            team_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'sales_team.team_sales_department')
        return team_id


# class crm_lead(format_address, osv.osv):
# 	""" CRM Lead Case """
# 	_inherit = "crm.lead"

# 	def merge_opportunity(self, cr, uid, ids, user_id=False, team_id=False, context=None):
# 		opp_id = super(crm_lead, self).merge_opportunity(cr, uid, ids, user_id=user_id, team_id=team_id, context=context)
# 		print "Opportnity Id:::::::",opp_id
# 		return opp_id


    # def merge_call_details(self, cr, uid, ids, user_id=False, team_id=False, context=None):
    # """
    # Different cases of merge:
    # - merge leads together = 1 new lead
    # - merge at least 1 opp with anything else (lead or opp) = 1 new opp

    # :param list ids: leads/opportunities ids to merge
    # :return int id: id of the resulting lead/opp
    # """
    # if context is None:
    #     context = {}

    # if len(ids) <= 1:
    #     raise UserError(_('Please select more than one element (lead or opportunity) from the list view.'))

    # opportunities = self.browse(cr, uid, ids, context=context)
    # sequenced_opps = []
    # # Sorting the leads/opps according to the confidence level of its stage, which relates to the probability of winning it
    # # The confidence level increases with the stage sequence, except when the stage probability is 0.0 (Lost cases)
    # # An Opportunity always has higher confidence level than a lead, unless its stage probability is 0.0
    # for opportunity in opportunities:
    #     sequence = -1
    #     if opportunity.stage_id and opportunity.stage_id.on_change:
    #         sequence = opportunity.stage_id.sequence
    #     sequenced_opps.append(((int(sequence != -1 and opportunity.type == 'opportunity'), sequence, -opportunity.id), opportunity))

    # sequenced_opps.sort(reverse=True)
    # opportunities = map(itemgetter(1), sequenced_opps)
    # ids = [opportunity.id for opportunity in opportunities]
    # highest = opportunities[0]
    # opportunities_rest = opportunities[1:]

    # tail_opportunities = opportunities_rest

    # fields = list(CRM_LEAD_FIELDS_TO_MERGE)
    # merged_data = self._merge_data(cr, uid, ids, highest, fields, context=context)

    # if user_id:
    #     merged_data['user_id'] = user_id
    # if team_id:
    #     merged_data['team_id'] = team_id

    # # Merge notifications about loss of information
    # opportunities = [highest]
    # opportunities.extend(opportunities_rest)

    # self.merge_dependences(cr, uid, highest.id, tail_opportunities, context=context)

    # # Check if the stage is in the stages of the sales team. If not, assign the stage with the lowest sequence
    # if merged_data.get('team_id'):
    #     team_stage_ids = self.pool.get('crm.stage').search(cr, uid, [('team_ids', 'in', merged_data['team_id']), ('type', 'in', [merged_data.get('type'), 'both'])], order='sequence', context=context)
    #     if merged_data.get('stage_id') not in team_stage_ids:
    #         merged_data['stage_id'] = team_stage_ids and team_stage_ids[0] or False
    # # Write merged data into first opportunity
    # self.write(cr, uid, [highest.id], merged_data, context=context)
    # # Delete tail opportunities 
    # # We use the SUPERUSER to avoid access rights issues because as the user had the rights to see the records it should be safe to do so
    # self.unlink(cr, SUPERUSER_ID, [x.id for x in tail_opportunities], context=context)

    # return highest.id