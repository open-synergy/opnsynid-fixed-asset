# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import models


class ComplexFixedAssetInstallation(models.Model):
    _name = "complex_fixed_asset_installation"
    _inherit = [
        "mixin.documenso_signing_approval",
        "complex_fixed_asset_installation",
    ]

    _documenso_signing_create_page = True
