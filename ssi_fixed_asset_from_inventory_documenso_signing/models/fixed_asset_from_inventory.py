# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import models


class FixedAssetFromInventory(models.Model):
    _name = "fixed_asset_from_inventory"
    _inherit = [
        "mixin.documenso_signing_approval",
        "fixed_asset_from_inventory",
    ]

    _documenso_signing_create_page = True
