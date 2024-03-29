# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    lot_id = fields.Many2one(string="Lot/Serial", comodel_name='stock.production.lot')
    is_sale_related = fields.Boolean(compute="_compute_sale")

    def _compute_sale(self):
        is_sale_related = False
        for ticket in self:
            sale_id = self.env['sale.order'].search([('ticket_id', '=', ticket.id)])
            if sale_id:
                is_sale_related = True
            ticket.is_sale_related = is_sale_related

    def action_create_quotation(self):
        action = {
            'name': "create quotation",
            'type': "ir.actions.act_window",
            'target': 'inline',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'view_id': self.env.ref('sale.view_order_form').id,
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_company_id': self.company_id.id,
                'default_ticket_id': self.id
            }
        }

        return action

    def action_park_machine(self):
        action = {
            'name': "Parc Machine",
            'type': "ir.actions.act_window",
            'target': 'current',
            'view_type': 'form',
            'views': [
                [self.env.ref('park_machine.pm_machine_tree').id, "list"],
                [self.env.ref('park_machine.pm_machine_form').id, "form"]
            ],
            'res_model': 'stock.production.lot',
            'view_id': self.env.ref('park_machine.pm_machine_tree').id,
            # 'domain': [('lot_id', '=', self.id)], # Last chance, first, try auto-filtered
            'context': {
                'search_default_name': self.lot_id.name,
            }
        }

        return action

