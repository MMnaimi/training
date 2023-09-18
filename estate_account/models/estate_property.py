# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command

class EstateProperty(models.Model):
    _inherit = 'estate.property'

    invoice_id = fields.Many2one('account.move')

    def action_sold(self):

        invoice = self.env['account.move'].create({
            'partner_id': self.buyer.id,
            'move_type': 'out_invoice',
            
            'invoice_line_ids': [
                Command.create({
                    'name': f'6% of the selling price',
                    'quantity': 1,
                    'price_unit': self.selling_price * 0.06
                }),
                Command.create({
                    'name': 'administrative fees',
                    'quantity': 1,
                    'price_unit': 100
                })
            ]
        })
        self.invoice_id = invoice.id

        return super(EstateProperty, self).action_sold()
    

    def open_invoice(self):
        for rec in self:
            return {
                'name': 'Invoice',
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': rec.invoice_id.id,
            }