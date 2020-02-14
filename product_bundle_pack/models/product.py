# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from logging import getLogger

_logger = getLogger(__name__)


class ProductPack(models.Model):
    _name = 'product.pack'

    product_id = fields.Many2one(
        comodel_name='product.product',
        required=True,
        string=_('Product'))
    qty_uom = fields.Float(
        required=True,
        defaults=1.0,
        string=_('Quantity'))
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string=_('Product pack'))
    image = fields.Binary(
        related='product_id.image_variant_256',
        store=True,
        string=_('Image'))
    price = fields.Float(
        related='product_id.lst_price',
        string=_('Product Price'))
    uom_id = fields.Many2one(
        related='product_id.uom_id',
        readonly=True,
        string=_('Unit of Measure'))
    name = fields.Char(
        related='product_id.name', 
        readonly=True,
        string=_('Product Name'))


class ProductProduct(models.Model):
    _inherit = 'product.template'

    is_pack = fields.Boolean(
        string=_('Is Product Pack'))
    cal_pack_price = fields.Boolean(
        string=_('Calculate Pack Price'))
    pack_ids = fields.One2many(
        comodel_name='product.pack',
        inverse_name='product_tmpl_id',
        string=_('Product Pack'))

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)

        if res.cal_pack_price:
            if 'pack_ids' in vals or 'cal_pack_price' in vals:

                total = 0
                for pack_product in res.pack_ids:
                    qty = pack_product.qty_uom
                    price = pack_product.product_id.list_price
                    total += qty * price

                if total:
                    res.list_price = total

        return res

    def write(self, vals):
        res = super(ProductProduct, self).write(vals)

        for record in self:
            if record.cal_pack_price:
                if 'pack_ids' in vals or 'cal_pack_price' in vals:

                    total = 0
                    for pack_product in record.pack_ids:
                        qty = pack_product.qty_uom
                        price = pack_product.product_id.list_price
                        total += qty * price

                    if total:
                        record.list_price = total

        return res
