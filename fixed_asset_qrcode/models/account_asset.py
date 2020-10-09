# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import models


class AccountAssetAsset(models.Model):
    _name = "account.asset.asset"
    _inherit = [
        "account.asset.asset",
        "base.qr_document",
    ]
