# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    fixed_asset_category_id = fields.Many2one(
        string="Fixed Asset Category",
        comodel_name="fixed.asset.category",
    )
    fixed_asset_id = fields.Many2one(
        string="Fixed Asset",
        comodel_name="fixed.asset.asset",
        domain=[("type", "=", "normal"), ("state", "in", ["open", "close"])],
        help="Complete this field when selling an asset "
        "in order to facilitate the creation of the "
        "asset removal accounting entries via the "
        "asset 'Removal' button",
    )

    @api.multi
    def onchange_account_id(
        self, product_id, partner_id, inv_type, fposition_id, account_id
    ):
        _super = super(AccountInvoiceLine, self)
        res = _super.onchange_account_id(
            product_id, partner_id, inv_type, fposition_id, account_id
        )
        obj_account_account = self.env["account.account"]
        if account_id:
            asset_category = obj_account_account.browse(
                account_id
            ).fixed_asset_category_id
            if asset_category:
                if not res.get("value", False):
                    res["value"] = {}
                else:
                    res["value"]["fixed_asset_category_id"] = asset_category.id
        return res
