# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import fields, models


class AccountAssetDepreciationLineSubtype(models.Model):
    _name = "account.asset_depreciation_line_subtype"
    _description = "Depreciation Line Subtype"

    name = fields.Char(
        string="Depreciation Line Subtype",
        required=True,
    )
