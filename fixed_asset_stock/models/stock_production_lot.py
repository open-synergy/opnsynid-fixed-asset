# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    asset_id = fields.Many2one(
        string="Fixed Asset",
        comodel_name="account.asset.asset",
        ondelete="restrict",
    )
    join_asset_ids = fields.One2many(
        string="Join Asset",
        comodel_name="account.asset.asset",
        inverse_name="join_lot_id",
    )
    join_asset_id = fields.Many2one(
        string="Join Asset",
        comodel_name="account.asset.asset",
    )
    lot_relation = fields.Selection(
        string="Lot Relation",
        selection=[
            ("o2o", "Lot is an asset"),
            ("o2m", "One lot split into multiple asset"),
            ("m2o", "Multiple lot join into one asset"),
            ("no", "No relation"),
        ],
        compute="_compute_lot_relation",
        store=True,
    )

    @api.depends(
        "asset_id",
        "join_asset_ids",
        "join_asset_id",
    )
    def _compute_lot_relation(self):
        for record in self:
            result = "no"
            if record.asset_id:
                result = "o2o"
            elif len(record.join_asset_ids) > 0:
                result = "o2m"
            elif record.join_asset_id:
                result = "m2o"
            record.lot_relation = result

    @api.multi
    def _get_initial_move(self):
        self.ensure_one()
        obj_quant = self.env["stock.quant"]
        quants = obj_quant.search(self._get_initial_move_quant_domain())
        # TODO: Refactor Please
        moves = set()
        for quant in quants:
            moves |= {move for move in quant.history_ids}
        moves = list(moves)
        if len(moves) == 1:
            return moves[0]
        else:
            return False

    @api.multi
    def _get_initial_move_quant_domain(self):
        self.ensure_one()
        return [("lot_id", "=", self.id)]
