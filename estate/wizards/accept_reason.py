# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class AcceptReaonWizard(models.TransientModel):
    _name = 'accept.reason.wizard'
    _description = 'Accept Reason'

    reason = fields.Text(required=True)
    property_id = fields.Many2one('estate.property')
    offer_id = fields.Many2one('estate.property.offer')
    date = fields.Date(default=fields.Date.context_today)

    def action_accept(self):
        for rec in self:
            rec.property_id.write({
                'selling_price': rec.offer_id.price,
                'buyer': rec.offer_id.partner_id.id,
                'state': 'offer_accepted',
                'offer_accept_reason': rec.reason,
                
            })
            rec.offer_id.status = 'accepted'