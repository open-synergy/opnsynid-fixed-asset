# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Fixed Asset Retirement",
    "version": "8.0.1.0.1",
    "category": "Accounting & Finance",
    "website": "https://opensynergy-indonesia.com",
    "author": "OpenSynergy Indonesia",
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
        "security/res_groups_data.xml",
        "security/ir.model.access.csv",
        "menu.xml",
        "views/account_asset_retirement_type_views.xml",
        "views/account_asset_retirement_common_views.xml",
    ]
}
