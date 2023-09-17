# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sold(self):

        invoice = self.env['account.move'].create({
            'partner_id': self.buyer.id,
            'move_type': 'out_invoice',

        })

        return super(EstateProperty, self).action_sold()