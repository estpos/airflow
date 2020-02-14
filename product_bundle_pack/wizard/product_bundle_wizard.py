# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductBundle(models.TransientModel):
    _name = 'product.bundle'

    product_id = fields.Many2one(
        comodel_name='product.product',
        required=True,
        string=_('Bundle'))
    product_price = fields.Float(
        string=_('Price'))
    product_qty = fields.Integer( 
        required=True, 
        default=1,
        string=_('Quantity'))
    pack_ids = fields.One2many(
        comodel_name='product.pack',
        related='product_id.pack_ids',
        string=_('Select Products'))

    def add_product_bundle_button(self):
        for pack in self:
            if pack.product_id.is_pack:
                self.env['sale.order.line'].create({
                    'order_id': self._context['active_id'],
                    'product_id': pack.product_id.id,
                    'name': pack.product_id.name,
                    'price_unit': self.product_price,
                    'product_uom': pack.product_id.uom_id.id,
                    'product_uom_qty': self.product_qty
                })

        return True

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.product_price = self.product_id.lst_price
