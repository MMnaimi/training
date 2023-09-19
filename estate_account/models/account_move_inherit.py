# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command

class EstateProperty(models.Model):
    _inherit = 'account.move'


    property_id = fields.Many2one('estate.property')


    def open_estate_property(self):
        for rec in self:
            return {
                'name': 'Estate Property',
                'type': 'ir.actions.act_window',
                'res_model': 'estate.property',
                'view_mode': 'form',
                'res_id': rec.property_id.id,
            }
        