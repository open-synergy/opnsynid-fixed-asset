# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models


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
    join_lot_id = fields.Many2one(
        string="Join Lot",
        comodel_name="stock.production.lot",
        ondelete="restrict",
    )
    join_lot_ids = fields.One2many(
        string="Join Lots",
        comodel_name="stock.production.lot",
        inverse_name="join_asset_id",
    )
    asset_relation = fields.Selection(
        string="Asset Relation",
        selection=[
            ("o2o", "Asset is a lot"),
            ("o2m", "One asset split into multiple lot"),
            ("m2o", "Multiple asset join into one lot"),
            ("no", "No relation"),
        ],
        compute="_compute_asset_relation",
        store=True,
    )

    @api.depends(
        "lot_id",
        "join_lot_ids",
        "join_lot_id",
    )
    def _compute_asset_relation(self):
        for record in self:
            result = "no"
            if record.lot_id:
                result = "o2o"
            elif len(record.join_lot_ids) > 0:
                result = "o2m"
            elif record.join_lot_id:
                result = "m2o"
            record.asset_relation = result
