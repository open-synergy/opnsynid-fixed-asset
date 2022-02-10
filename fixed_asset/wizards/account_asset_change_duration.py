# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import time

from odoo import api, fields, models


class AssetModify(models.TransientModel):
    _name = "asset.modify"
    _description = "Modify Asset"

    @api.model
    def _default_asset_id(self):
        return self.env.context.get("active_id", False)

    asset_id = fields.Many2one(
        string="# Asset",
        comodel_name="fixed.asset.asset",
        default=lambda self: self._default_asset_id(),
    )
    method_time = fields.Selection(
        string="Method Time",
        related="asset_id.method_time",
        readonly=True,
    )
    name = fields.Char(
        string="Reason",
        size=64,
        required=True,
    )
    method_number = fields.Integer(
        string="Number of Depreciations/Years",
        required=True,
    )
    method_period = fields.Selection(
        string="Period Length",
        selection=[
            ("month", "Month"),
            ("quarter", "Quarter"),
            ("year", "Year"),
        ],
        help="Period length for the depreciation accounting entries",
    )
    method_end = fields.Date(
        string="Ending date",
    )
    note = fields.Text(
        string="Notes",
    )

    @api.model
    def default_get(self, fields):
        _super = super(AssetModify, self)
        res = _super.default_get(fields)
        obj_account_asset = self.env["fixed.asset.asset"]
        asset_id = self._context.get("active_id", False)

        asset = obj_account_asset.browse(asset_id)
        if "name" in fields:
            res.update({"name": asset.name})
        if "method_number" in fields and asset.method_time in ["number", "year"]:
            res.update({"method_number": asset.method_number})
        if "method_period" in fields:
            res.update({"method_period": asset.method_period})
        if "method_end" in fields and asset.method_time == "end":
            res.update({"method_end": asset.method_end})
        return res

    @api.multi
    def _prepare_data_history(self):
        self.ensure_one()
        data = {
            "asset_id": self.asset_id.id,
            "name": self.name,
            "method_time": self.asset_id.method_time,
            "method_number": self.asset_id.method_number,
            "method_period": self.asset_id.method_period,
            "method_end": self.asset_id.method_end,
            "user_id": self.env.user.id,
            "date": time.strftime("%Y-%m-%d"),
            "note": self.note,
        }
        return data

    @api.multi
    def _create_history(self):
        self.ensure_one()
        obj_asset_history = self.env["fixed.asset.history"]
        obj_asset_history.create(self._prepare_data_history())

    @api.multi
    def _prepare_data_asset(self):
        self.ensure_one()
        data = {
            "method_number": self.method_number,
            "method_period": self.method_period,
            "method_end": self.method_end,
        }
        return data

    @api.multi
    def _update_asset(self):
        self.ensure_one()
        self.asset_id.write(self._prepare_data_asset())

    @api.multi
    def modify(self):
        self.ensure_one()
        self._create_history()
        self._update_asset()
        self.asset_id.compute_depreciation_board()
        return {"type": "ir.actions.act_window_close"}
