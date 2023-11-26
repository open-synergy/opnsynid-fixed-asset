# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FixedAssetFromInventory(models.Model):
    _name = "fixed_asset_from_inventory_type"
    _inherit = [
        "mixin.master_data",
    ]
    _description = "Fixed Asset From Inventory Type"

    fixed_asset_usage_id = fields.Many2one(
        string="Fixed Asset Usage",
        comodel_name="product.usage_type",
        required=True,
        ondelete="restrict",
    )
    inventory_usage_id = fields.Many2one(
        string="Inventory Usage",
        comodel_name="product.usage_type",
        required=True,
        ondelete="restrict",
    )
    journal_id = fields.Many2one(
        string="journal",
        comodel_name="account.journal",
        required=True,
        ondelete="restrict",
    )
