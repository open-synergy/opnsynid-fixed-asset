# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FixedAssetAsset(models.Model):
    _name = "fixed.asset.asset"
    _inherit = ["fixed.asset.asset", "mixin.qr_code"]

    _qr_code_create_page = True
