# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Fixed Asset Impairment",
    "version": "8.0.1.0.1",
    "category": "Accounting & Finance",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "fixed_asset",
        "base_sequence_configurator",
        "base_workflow_policy",
        "base_print_policy",
        "base_multiple_approval",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/res_groups_data.xml",
        "data/ir_sequence_data.xml",
        "data/base_sequence_configurator_data.xml",
        "data/base_workflow_policy_data.xml",
        "menu.xml",
        "views/account_asset_config_setting_views.xml",
        "views/account_asset_category_views.xml",
        "views/account_asset_views.xml",
        "views/account_asset_impairment_common_views.xml",
        "views/account_asset_impairment_views.xml",
        "views/account_asset_impairment_reversal_views.xml",
    ],
    "demo": [
        "demo/account_journal_demo.xml",
        "demo/account_account_type_demo.xml",
        "demo/account_account_demo.xml",
        "demo/account_asset_category_demo.xml",
        "demo/tier_definition_demo.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
}
