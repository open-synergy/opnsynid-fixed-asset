# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fixed Asset",
    "version": "14.0.1.8.0",
    "category": "Accounting & Finance",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "account_fiscal_year",
        "ssi_financial_accounting",
        "ssi_master_data_mixin",
        "ssi_transaction_confirm_mixin",
        "ssi_transaction_done_mixin",
        "ssi_transaction_cancel_mixin",
        "ssi_transaction_open_mixin",
    ],
    "external_dependencies": {
        "python": [
            "ddt",
            "numpy",
        ],
    },
    "data": [
        "security/ir_module_category_data.xml",
        "security/res_group_data.xml",
        "security/account_asset_security.xml",
        "security/ir.model.access.csv",
        "data/approval_template_data.xml",
        "data/policy_template_data.xml",
        "data/ir_sequence_data.xml",
        "data/sequence_template_data.xml",
        "data/ir_server_action_data.xml",
        "data/account_journal_data.xml",
        "wizards/mass_depreciation_views.xml",
        "views/fixed_asset_category.xml",
        "views/account_account_view.xml",
        "views/fixed_asset_asset.xml",
        "views/account_move_line_views.xml",
    ],
    "demo": [
        "demo/account_journal_demo.xml",
        "demo/account_account_demo.xml",
        "demo/fixed_asset_category_demo.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
}
