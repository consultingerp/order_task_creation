# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import datetime

class SaleOrder(models.Model):
    _inherit='sale.order'
    
    @api.depends('state')
    def _get_task(self):
        for order in self:
            task_ids=order.task
            
            order.update({
                'task_count': len(task_ids),  
            })

    is_task = fields.Boolean('Task', default=False)
    task = fields.One2many('project.task','order_id','Tasks')
    task_count = fields.Integer(string='# of Task', compute='_get_task',
                                readonly=True)
    
    @api.multi
    def action_view_task_source(self):
        task_ids = self.mapped('task')
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('order_task_creation.action_orders_task')
        list_view_id = imd.xmlid_to_res_id(
            'order_task_creation.view_task_tree_new')
        form_view_id = imd.xmlid_to_res_id(
            'order_task_creation.view_task_form_sale')

        result = {
            'name': action.name,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'],
                      [False, 'graph'], [False, 'kanban'],
                      [False, 'calendar'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(task_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % task_ids.ids
        elif len(task_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = task_ids.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
    
    @api.multi
    def create_task(self):
        context = self.env.context or {}
        OrderLine = self.env['sale.order.line']
        Task = self.env['project.task']
        task_ids = []
        if context.get('lang') == 'de_DE':
            stage_id = self.env['project.task.type'].search(
                [('name', '=', 'Neu')])
        else:
            stage_id = self.env['project.task.type'].search(
                [('name', '=', 'New')])

        if not self.order_line or len(self.order_line)<=0:
            raise UserError(_(
                'There is nothing to create a Sales Task! Please create some '
                'order line before creating Sales Task'))
        if len(self.order_line) and isinstance(self.id, int):
            self._cr.execute(
                "SELECT min(id) from sale_order_line where order_id = %s" %
                self.id)
            result_query = self._cr.dictfetchall()
            line_id = result_query and result_query[0]['min']

        if line_id:
            line  = OrderLine.browse(line_id)
            task_id = Task.create({
                        'name' : line.product_id.name + ' : ' +
                                 line.order_id.name,
                        'order_id': line.order_id.id,
                        'sale_task': True,
                        'stage_id': stage_id.id or False,
                        'partner_id': line.order_id.partner_id.id
            })
            task_ids.append(task_id.id)
        self.write({'is_task':True})
        return {
                'name': _('Sales Task'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.task',
                'view_id': self.env.ref(
                            'order_task_creation.view_task_form_sale').id,
                'type': 'ir.actions.act_window',
                'res_id': task_ids and task_ids[0],
                'target': 'current'
        }


class project_task(models.Model):
    _inherit='project.task'

    @api.depends('delivery_date', 'fix')
    def _compute_yearly_week(self):
        for record in self:
            if record.delivery_date:
                record_date=record.delivery_date
                date_record=datetime.strptime(record_date, '%Y-%m-%d')
                week=date_record.isocalendar()[1]
                record.year_week = week

    order_id=fields.Many2one('sale.order','Sales Order', index=True)
    refinement_data = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                       'Refinement Data', index=True)
    delivery_billing_adress = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                               'Delivery & Billing address',
                                               index=True)
    vallue_tax_id = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                     'Vallue Added Tax ID', index=True)
    delivery_date=fields.Date('Delivery Date', index=True)
    year_week= fields.Char(compute='_compute_yearly_week', index=True)
    payment = fields.Many2many('miscellaneous.entry',
                               'payment_manager_task_rel', 'partner_id',
                               'task_id',
                               string='Payment')
    payment_supplier = fields.Many2many('misc.supplier.payment',
                                        'supplier_manager_task_rel',
                                        'supplier_id', 'task_id1',
                                        string='Payment Supplier')
    digital_sample = fields.Many2many('digital.sample',
                                      'digital_manager_task_rel', 'digital_id',
                                      'task_id2',
                                      string='Digital Sample')
    sample = fields.Many2many('sample.sample', 'sample_manager_task_rel',
                              'sample_id', 'task_id3', string='Sample')
    comment=fields.Text('Comment', index=True)
    fix=fields.Boolean('Fix')
    sale_task=fields.Boolean('Sale Task')

    @api.multi
    def action_view_order(self):
        order_ids = self.mapped('order_id')
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('sale.action_orders')
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'],
                      [False, 'graph'], [False, 'kanban'],
                      [False, 'calendar'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(order_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % order_ids.ids
        elif len(order_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = order_ids.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
    
    @api.multi
    def open_to_form_view(self):
        self.ensure_one()
        context = self.env.context or {}
        document_id = self.id
        return {
            'name': _('Sales Task'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref(
                'order_task_creation.view_task_form_sale').id,
            'res_model': 'project.task', 
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'current',
            'res_id': document_id,
        }

    @api.multi
    def _read_group_stage_ids_inherit(self, domain, read_group_order=None,
                                      access_rights_uid=None):
        context = self.env.context or {}
        stage_obj = self.env['project.task.type']
        order = stage_obj._order
        access_rights_uid = access_rights_uid or self.uid
        if read_group_order == 'stage_id desc':
            order = '%s desc' % order
        if not context.get('default_sale_task'):
            if 'default_project_id' in context:
                search_domain = ['|', (
                'project_ids', '=', context['default_project_id']),
                                 ('id', 'in', self.ids)]
            else:
                search_domain = [('id', 'in', self.ids)]
        if context.get('default_sale_task'):
            search_domain = [('sales_stage', '=', True)]
        stage_ids = stage_obj._search(search_domain, order=order,
                                      access_rights_uid=access_rights_uid)
        stages = stage_obj.browse(stage_ids)
        result = stages.name_get()
        # restore order of the search
        result.sort(
            lambda x, y: cmp(stage_ids.index(x[0]), stage_ids.index(y[0])))
        fold = {}
        for stage in stages:
            fold[stage.id] = stage.fold or False
        return result, fold
    _group_by_full = {
        'stage_id': _read_group_stage_ids_inherit,
    }


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'
    
    sales_stage = fields.Boolean(string="Sales Task Stage", default=False)
