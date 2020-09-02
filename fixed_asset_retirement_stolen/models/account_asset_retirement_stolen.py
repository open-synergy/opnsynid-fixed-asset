# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, api


class FixedAssetRetirementStolen(models.Model):
    _name = "account.asset_retirement_stolen"
    _inherit = ["account.asset_retirement_common"]
    _description = "Fixed Asset Retirement by Stolen"
    _table = "account_asset_retirement"

    @api.model
    def _default_type_id(self):
        return self.env.ref(
            "fixed_asset_retirement_stolen."
            "retirement_type_stolen").id

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        type_id = self.env.ref(
            "fixed_asset_retirement_stolen."
            "retirement_type_stolen", False) and self.env.ref(
                "fixed_asset_retirement_stolen."
                "retirement_type_stolen") or self.env["account."
                                                      "asset_retirement_type"]
        args.append(("type_id", "=", type_id.id))
        return super(FixedAssetRetirementStolen, self).search(
            args=args, offset=offset, limit=limit,
            order=order, count=count)
