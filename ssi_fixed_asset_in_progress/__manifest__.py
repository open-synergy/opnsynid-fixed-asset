# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fixed Asset In Progress",
    "version": "14.0.1.3.0",
    "category": "Accounting & Finance",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "ssi_fixed_asset",
        "ssi_master_data_mixin",
        "ssi_transaction_confirm_mixin",
        "ssi_transaction_done_mixin",
        "ssi_transaction_cancel_mixin",
        "ssi_transaction_open_mixin",
        "ssi_transaction_terminate_mixin",
        "ssi_print_mixin",
        "ssi_company_currency_mixin",
        "ssi_duration_mixin",
    ],
    "data": [
        "security/ir_module_category_data.xml",
        "security/res_group_data.xml",
        "security/ir.model.access.csv",
        "security/ir_rule_data.xml",
        "data/approval_template_data.xml",
        "data/policy_template_data.xml",
        "data/ir_sequence_data.xml",
        "data/sequence_template_data.xml",
        "data/account_type_demo.xml",
        "data/account_journal_data.xml",
        "views/fixed_asset_category_views.xml",
        "views/fixed_asset_in_progress_views.xml",
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
