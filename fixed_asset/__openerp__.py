# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Fixed Asset",
    "version": "8.0.2.1.0",
    "category": "Accounting & Finance",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account_accountant",
        "base_sequence_configurator",
        "base_workflow_policy",
        "base_print_policy",
        "base_multiple_approval",
        "base_cancel_reason",
    ],
    "data": [
        "security/account_asset_security.xml",
        "security/ir.model.access.csv",
        "menu.xml",
        "data/ir_sequence_data.xml",
        "data/base_sequence_configurator_data.xml",
        "data/base_cancel_reason_configurator_data.xml",
        "data/base_workflow_policy_data.xml",
        "wizards/account_asset_remove_view.xml",
        "wizards/account_asset_change_duration_view.xml",
        "wizards/wizard_asset_compute_view.xml",
        "views/account_asset_config_setting_views.xml",
        "views/account_asset_category.xml",
        "views/account_account_view.xml",
        "views/account_move_line_view.xml",
        "views/account_move_view.xml",
        "views/account_asset_asset.xml",
        "views/account_asset_history.xml",
        "views/account_invoice_view.xml",
    ],
}
