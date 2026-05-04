# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FixedAssetUsefulLifeEstimationChange(models.Model):
    _name = "fixed_asset_useful_life_estimation_change"
    _inherit = [
        "fixed_asset_useful_life_estimation_change",
        "mixin.single_operating_unit",
    ]
