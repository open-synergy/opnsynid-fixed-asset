# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Complex Fixed Asset",
    "version": "14.0.1.1.0",
    "category": "Accounting & Finance",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "ssi_financial_accounting",
        "ssi_master_data_mixin",
        "ssi_transaction_confirm_mixin",
        "ssi_transaction_done_mixin",
        "ssi_transaction_cancel_mixin",
        "ssi_fixed_asset",
        "ssi_company_currency_mixin",
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
        "views/complex_fixed_asset_installation_views.xml",
        "views/complex_fixed_asset_removal_views.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
}
