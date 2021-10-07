# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class AccountAssetFromInventoryType(models.Model):
    _name = "account.asset_from_inventory_type"
    _description = "Type of Fixed Asset From Inventory"

    name = fields.Char(
        string="Type",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    note = fields.Text(
        string="Note",
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        readonly=False,
    )
    allowed_product_categ_ids = fields.Many2many(
        string="Allowed Product Categories",
        comodel_name="product.category",
        relation="rel_asset_inventory_type_2_product_categ",
        column1="type_id",
        column2="category_id",
    )
    allowed_product_ids = fields.Many2many(
        string="Allowed Products",
        comodel_name="product.product",
        relation="rel_asset_inventory_type_2_product",
        column1="type_id",
        column2="product_id",
    )
    sequence_id = fields.Many2one(
        string="Sequence",
        comodel_name="ir.sequence",
        company_dependent=True,
    )
    asset_inventory_confirm_grp_ids = fields.Many2many(
        string="Allow To Confirm Inventory-Fixed Asset Conversion",
        comodel_name="res.groups",
        relation="rel_asset_inventory_type_confirm_exp_acc",
        column1="type_id",
        column2="group_id",
    )
    asset_inventory_restart_approval_grp_ids = fields.Many2many(
        string="Allow To Restart Inventory-Fixed Asset Conversion",
        comodel_name="res.groups",
        relation="rel_asset_inventory_type_restart_approval_exp_acc",
        column1="type_id",
        column2="group_id",
    )
    asset_inventory_cancel_grp_ids = fields.Many2many(
        string="Allow To Cancel Inventory-Fixed Asset Conversion",
        comodel_name="res.groups",
        relation="rel_asset_inventory_type_cancel_exp_acc",
        column1="type_id",
        column2="group_id",
    )
    asset_inventory_restart_grp_ids = fields.Many2many(
        string="Allow To Restart Inventory-Fixed Asset Conversion",
        comodel_name="res.groups",
        relation="rel_asset_inventory_type_restart_exp_acc",
        column1="type_id",
        column2="group_id",
    )
