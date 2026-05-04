# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FixedAssetAsset(models.Model):
    _name = "fixed.asset.asset"
    _inherit = [
        "fixed.asset.asset",
        "mixin.single_operating_unit",
    ]
