# -*- coding: utf-8 -*-
# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Fixed Asset from Inventory",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "base_sequence_configurator",
        "base_workflow_policy",
        "base_cancel_reason",
        "base_terminate_reason",
        "base_print_policy",
        "base_multiple_approval",
        "account_accountant",
        "web_readonly_bypass",
        "base_ir_filters_active",
        "base_action_rule",
        "fixed_asset_stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_module_category_data.xml",
        "security/res_groups_data.xml",
        "data/ir_sequence_data.xml",
        "data/base_sequence_configurator_data.xml",
        "data/base_cancel_reason_configurator_data.xml",
        "data/base_workflow_policy_data.xml",
        "views/account_asset_from_inventory_type_views.xml",
        "views/account_asset_from_inventory_views.xml",
    ],
    "demo": [
        "demo/account_asset_from_inventory_type_demo.xml",
    ],
}
