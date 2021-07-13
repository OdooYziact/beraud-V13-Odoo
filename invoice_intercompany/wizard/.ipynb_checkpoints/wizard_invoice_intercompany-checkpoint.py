# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)


class InvoiceIntercompany(models.TransientModel):
    _name = 'invoice.intercompany'

    date = fields.Date('Date de fin')
    description = fields.Text(readonly=True) # Only for popup

    def get_timesheets(self):
        invoiceable_timesheets = False

        if self.date:
            timesheets = self.env['account.analytic.line'].sudo().search([
                ('is_timesheet', '=', True),
                ('is_invoiced', '=', False),
                ('date', '<=', self.date)
            ])
            if timesheets:
                invoiceable_timesheets = timesheets.filtered(lambda x: x.company_id != x.user_id.company_id)
                
        return invoiceable_timesheets

    def get_time_to_invoice_per_company(self, invoiceable_timesheets):
        """
        Return dict like {'res.company(x,)', [list of timesheet_ids], 'res.company(y,)': [12,15,98,966]}
        :param timesheets:
        """
        companies = self.env['res.company'].search([])
        timesheet_per_companies = {}

        for company_id in companies:
            # Building dict like timesheet_per_companies {'res.company(x,)': [time_to_pay], 'res.company(y,)': [time_to_pay], …}
            # {'Atom': [Beraud_timesheet_spent_m_project, …]}
            if not company_id in timesheet_per_companies:
                timesheet_per_companies[company_id] = []

            for timesheet in invoiceable_timesheets:
                # Add another test on difference between company_id and user default company
                if timesheet.company_id.id == company_id.id and timesheet.user_id.company_id.id != company_id.id:
                    timesheet_per_companies[company_id].append(timesheet.id)
                    
        return timesheet_per_companies

    def create_full_invoices(self, timesheet_per_companies):
        company_env = self.env['res.company']
        companies = company_env.search([])
        analytic_line_env = self.env['account.analytic.line']
        time_spent_product_id = self.env.ref('invoice_intercompany.product_time_spent')
        
        logger.warning(timesheet_per_companies)
        
        for company_id in companies:
            lines = analytic_line_env.browse(timesheet_per_companies[company_id])
            
            if lines:
                
                logger.warning('//////////////////////////////////////////////////////////////////////////////////////')
                logger.warning(lines, lines.ids)
                logger.warning('//////////////////////////////////////////////////////////////////////////////////////')
            
                # Loading Client (partner) and Vendor (companie) for sale invoice
                sale_company_id = company_env.search([('id', '!=', company_id.id)]) # Sale Vendor (so, not curent company_id (cf. for))
                sale_partner_id = company_id.partner_id # Sale Customer (so parnter linked to the courrent company (cf. for))

                # Loading Client (partner) and Vendor (companie) for purchase invoice
                purchase_company_id = company_id # Customer
                purchase_partner_id = company_env.search([('id', '!=', company_id.id)]).partner_id # Supplier / Vendor

                # Preparing invoices values 
                sale_invoice_values = self._prepare_account_move_values('in_invoice', sale_partner_id, lines)  # Supplier / Vendor
                purchase_invoice_values = self._prepare_account_move_values('out_invoice', purchase_partner_id, lines) # Customer

                # Preparing invoices lines values 
                sale_invoice_line = self._prepare_invoice_line_values(sum(lines.mapped('amount')), time_spent_product_id, sale_company_id)
                purchase_invoice_line = self._prepare_invoice_line_values(sum(lines.mapped('amount')), time_spent_product_id, purchase_company_id)

                #Add lines values to invoice values
                sale_invoice_values['invoice_line_ids'] = sale_invoice_line
                purchase_invoice_values['invoice_line_ids'] = purchase_invoice_line

                # Creating invoices with values
                is_sale_invoice_created = self.env['account.move'].with_context({'force_company': sale_company_id.id}).create(sale_invoice_values)
                is_purchase_invoice_created = self.env['account.move'].with_context({'force_company': purchase_company_id.id}).create(purchase_invoice_values)

                if is_sale_invoice_created and is_purchase_invoice_created:
                    lines.write({'is_invoiced': True})
                    is_sale_invoice_created.write({'account_analytic_line_ids': [(6, False, lines.ids)]})
                    is_purchase_invoice_created.write({'account_analytic_line_ids': [(6, False, lines.ids)]})
        
            
    
    def _prepare_account_move_values(self, type, partner_id, lines):
        """
        @params: type, string ['out_invoice','in_invoice'], respectively sales and purchases
        Returns : Dict of create values (account_move // account_invoice)
        """
        account_move_values = {
            'type': type,
            'partner_id': partner_id,
            'invoice_line_ids': []
        }
        
        return account_move_values
    
    def _prepare_invoice_line_values(self, product_quantity, product_id, company_id):
        """
        time_spent_product_id is defined in current module data
        returns : Dict of create values (account_move_line // account_invoice_line)
        """
        
        account_move_line_values = [(0, False, {
          'product_id': product_id.with_context({'force_company': company_id.id}).id,
            'quantity': product_quantity,
            'price_unit': product_id.list_price,
        })]
        
        return account_move_line_values

    def run(self):
        timesheets = self.sudo().get_timesheets()
        if timesheets:
            ordered_timesheets = self.sudo().get_time_to_invoice_per_company(timesheets)
            self.create_full_invoices(ordered_timesheets)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
    def clear_is_invoiced_bool(self, ids=[]):
        """
        This function can not be run in web.
        Use this by shell
        """
        aal_env = self.env['account.analytic.line']
        aal = False
        if not ids:
            aal = aal_env.search([('is_invoiced', '=', True)])
        else:
            aal = aal_env.browse(ids)
        
        aal.write({'is_invoiced': False})
        
        return True
            
