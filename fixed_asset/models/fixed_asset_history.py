# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import fields, models


class FixedAssetHistory(models.Model):
    _name = "fixed.asset.history"
    _description = "Asset History"
    _order = "date desc"

    name = fields.Char(string="History name", size=64, select=1)
    user_id = fields.Many2one(
        string="User",
        comodel_name="res.users",
        required=True,
    )
    date = fields.Date(
        string="Date",
        required=True,
        default=datetime.now().strftime("%Y-%m-%d"),
    )
    asset_id = fields.Many2one(
        string="Asset",
        comodel_name="fixed.asset.asset",
        required=True,
        ondelete="cascade",
    )
    method_time = fields.Selection(
        string="Time Method",
        selection=[
            ("year", "Number of Years"),
        ],
        required=True,
    )
    method_number = fields.Integer(
        string="Number of Years",
        help="The number of years needed to depreciate your asset",
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
        string="Note",
    )
