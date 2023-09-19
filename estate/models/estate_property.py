# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

from datetime import date, timedelta
from random import randint


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _order = 'id desc'

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availibility = fields.Date(copy=False, default=lambda self: date.today() + timedelta(days=90))
    expected_price = fields.Monetary(required=True)
    selling_price = fields.Monetary( copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),

    ])
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled'),
    ], default='new'
    )
    offer_ids = fields.One2many('estate.property.offer', 'property_id')
    property_type_id = fields.Many2one('estate.property.type', required=True)
    tag_ids = fields.Many2many('estate.property.tag')
    buyer = fields.Many2one('res.partner')
    salesman = fields.Many2one('res.users', default=lambda self: self.env.user)
    total_area = fields.Float(compute='_compute_total_area')
    best_price = fields.Monetary(compute='_compute_best_price')
    offer_accept_reason = fields.Text()
    currency_id = fields.Many2one('res.currency')
    offer_accept_date = fields.Date()

    _sql_constraints = [
        (
            'expected_price_positive',
            'CHECK(expected_price >= 0)',
            'Expected price must be greater than 0.'
        )
    ]

    # @api.ondelete(at_uninstall=False)
    # def _unlink_if_state_new_cancel(self):
    #     if self.state not in ('new', 'cancelled'):
    #         raise ValidationError('Record can only be deleted in new or cancel states.')

    def unlink(self):
        for rec in self:
            if rec.state not in ('new', 'cancelled'):
                raise ValidationError('Record can only be deleted in new or cancel states.')
            return super(EstateProperty, self).unlink()

    @api.constrains('selling_price')
    def _check_selling_price(self):
        for rec in self:
            if rec.selling_price < rec.expected_price * 0.9:
                raise ValidationError(f'Selling price should be at least 90% expected price.')
            
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for rec in self:
            rec.best_price = False
            if rec.offer_ids:
                best_price = max(rec.offer_ids.mapped('price'))
                rec.best_price = best_price

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_orientation = 'north'
            self.garden_area = 10
        else:
            self.garden_orientation = False
            self.garden_area = False

    def action_sold(self):
        for rec in self:
            if rec.state == 'cancelled' :
                raise UserError('Cancelled property cannot be sold.')
            rec.state = 'sold'

    def action_cancel(self):
        for rec in self:
            rec.write({
                'state': 'cancelled'
            })


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _order = 'name'

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id')
    sequence = fields.Integer()
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id')
    offer_count = fields.Integer(compute='_compute_offer_count')

    def open_offers(self):
        for rec in self:
            return {
                'name': 'Offers',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'estate.property.offer',
                'domain': [('property_type_id', '=', rec.id)],
            }

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)

    _sql_constraints = [
        (
            'unq_name',
            'unique(name)',
            'Property type name already exist'
        ),
    ]


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _order = 'name'

    def _default_color(self):
        return randint(1, 11)
    
    name = fields.Char(required=True)
    color = fields.Integer(default=lambda self: self._default_color())

    _sql_constraints = [
        (
            'unq_name',
            'unique(name)',
            'Property tag name already exist'
        ),
    ]


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _order = 'price desc'
    _rec_name='partner_id'

    price = fields.Monetary()
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ], copy=False
    )
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True, ondelete='cascade')
    validty = fields.Integer()
    date_deadline = fields.Date(compute='_compute_date_deadline')
    property_type_id = fields.Many2one(related='property_id.property_type_id', store=True)
    currency_id = fields.Many2one(related='property_id.currency_id', store=True)
    _sql_constraints = [
        (
            'price_positive',
            'CHECK(price > 0)',
            'Price must be greater than 0.'
        ),
    ]

    @api.model
    def create(self, values):
        estate_property = self.env['estate.property'].browse(values.get('property_id'))
        estate_property.state = 'offer_received'
        if values.get('price') <= estate_property.best_price:
            raise ValidationError(f"The offer must be higher than {estate_property.best_price}")
        res = super(EstatePropertyOffer, self).create(values)
        return res

    @api.depends('validty', 'create_date')
    def _compute_date_deadline(self):
        for rec in self:
            rec.date_deadline = rec.create_date + timedelta(days=rec.validty) if rec.create_date else False

    def action_accept(self):
        for rec in self:
            return {
                'name': 'Accept Reason',
                'type': 'ir.actions.act_window',
                'res_model': 'accept.reason.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_property_id': rec.property_id.id, 'default_offer_id': rec.id}
            }


    def action_refuse(self):
        for rec in self:
            rec.status = 'refused'