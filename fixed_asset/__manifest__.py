# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Fixed Asset",
    "version": "11.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "account_fiscal_year",
        "ssi_sequence_mixin",
        "ssi_policy_mixin",
        "ssi_multiple_approval_mixin",
    ],
    "external_dependencies": {
        "python": [
            "ddt",
        ],
    },
    "data": [
        "security/account_asset_security.xml",
        "security/ir.model.access.csv",
        "menu.xml",
        "data/ir_sequence_data.xml",
        "data/sequence_template_data.xml",
        "views/fixed_asset_config_setting_views.xml",
        "views/fixed_asset_category.xml",
        "views/account_account_view.xml",
        "views/account_move_line_view.xml",
        "views/account_move_view.xml",
        "views/fixed_asset_asset.xml",
        "views/fixed_asset_history.xml",
        "views/account_invoice_view.xml",
    ],
    "demo": [],
    "images": [
        "static/description/banner.png",
    ],
}