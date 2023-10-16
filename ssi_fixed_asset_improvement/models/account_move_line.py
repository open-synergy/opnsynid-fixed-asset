# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = "account.move.line"

    fixed_asset_improvement_id = fields.Many2one(
        "fixed_asset_improvement",
        string="Asset Improvement",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
