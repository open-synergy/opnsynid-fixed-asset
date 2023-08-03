# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FixedAssetDepreciationLineSubtype(models.Model):
    _name = "fixed.asset_depreciation_line_subtype"
    _description = "Depreciation Line Subtype"

    name = fields.Char(
        string="Depreciation Line Subtype",
        required=True,
    )
