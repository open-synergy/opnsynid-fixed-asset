# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    fixed_asset_id = fields.Many2one(
        string="Fixed Asset",
        comodel_name="fixed.asset.asset",
        ondelete="restrict",
        copy=False,
        readonly=True,
    )
    fixed_asset_category_id = fields.Many2one(
        string="Fixed Asset Category",
        comodel_name="fixed.asset.category",
    )
