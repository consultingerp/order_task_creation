# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CreateTask(models.TransientModel):
    _name = "create.task"
    _description='Create Task'
    
    project_id=fields.Many2one('project.project','Select Project')
    
    @api.multi
    def create_task(self):
        context = self.env.context or {}
        sale_obj=self.env['sale.order']
        order_line_obj=self.env['sale.order.line']
        task_obj=self.env['project.task']
        project_id=self.project_id.id
        sale_id=self._context.get('active_id')
        sale_browse=sale_obj.browse(sale_id)
        order_line_ids=[]
        line_ids=order_line_obj.search([('order_id','=',sale_id)], limit=1)
        for line in line_ids:
            order_line_ids.append(line.id)
        line=order_line_obj.browse(order_line_ids[0])
        name=line.product_id.name +" "+line.order_id.name
        if context.get('lang') == 'de_DE':
            stage_id = self.env['project.task.type'].search(
                [('name', '=', 'Neu'), ('project_ids', '=', project_id)])
        else:
            stage_id = self.env['project.task.type'].search(
                [('name', '=', 'New'), ('project_ids', '=', project_id)])
        task_vals={'name':name,
                   'project_id':project_id,
                   'order_id':sale_id,
                   'sale_task':True,
                   'stage_id': stage_id.id or False,
		           'partner_id':sale_browse.partner_id.id}
        task_obj.create(task_vals)
        sale_browse.write({'is_task':True})
        return True
    
