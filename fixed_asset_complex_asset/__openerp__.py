# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Complex Fixed Assets Management",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "fixed_asset",
        "base_sequence_configurator",
        "base_workflow_policy",
        "web_readonly_bypass",
        "base_print_policy",
        "base_multiple_approval",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/base_sequence_configurator_data.xml",
        "data/base_workflow_policy_data.xml",
        "menu.xml",
        "views/account_asset_config_setting_views.xml",
        "views/account_asset_views.xml",
        # "views/account_asset_category_views.xml",
        "views/account_complex_asset_movement_common_views.xml",
        "views/account_complex_asset_installation_views.xml",
        "views/account_complex_asset_removal_views.xml",
    ],
}
