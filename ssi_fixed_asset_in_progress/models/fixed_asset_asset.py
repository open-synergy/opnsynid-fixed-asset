# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FixedAssetAsset(models.Model):
    _inherit = "fixed.asset.asset"
    _name = "fixed.asset.asset"

    fixed_asset_in_progress_id = fields.Many2one(
        string="Fixed Asset in Progress",
        comodel_name="fixed_asset.in_progress",
        ondelete="restrict",
        copy=False,
        readonly=True,
    )
