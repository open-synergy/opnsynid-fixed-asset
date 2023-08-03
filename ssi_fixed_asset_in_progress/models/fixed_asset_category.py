# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FixedAssetCategory(models.Model):
    _name = "fixed.asset.category"
    _inherit = "fixed.asset.category"

    account_fixed_asset_in_progress_id = fields.Many2one(
        string="Asset in Progress Account",
        comodel_name="account.account",
    )
    fixed_asset_in_progress_journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
    )
