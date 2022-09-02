# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models


class AccountAsset(models.Model):
    _inherit = "account.asset.asset"

    lot_id = fields.Many2one(
        string="Lot",
        comodel_name="stock.production.lot",
        ondelete="restrict",
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
    )
