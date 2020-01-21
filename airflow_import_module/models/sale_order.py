# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

from logging import getLogger
_logger = getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    web_order_nr = fields.Char(string=_('Web Order Nr'))