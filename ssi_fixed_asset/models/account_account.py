# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    fixed_asset_category_id = fields.Many2one(
        string="Fixed Asset Category",
        comodel_name="fixed.asset.category",
        help="Default Fixed Asset Category when creating invoice lines "
        "with this account.",
    )
