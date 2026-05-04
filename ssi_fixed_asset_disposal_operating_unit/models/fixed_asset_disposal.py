# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FixedAssetDisposal(models.Model):
    _name = "fixed_asset.disposal"
    _inherit = [
        "fixed_asset.disposal",
        "mixin.single_operating_unit",
    ]
