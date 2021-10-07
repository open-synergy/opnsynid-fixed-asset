# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Fixed Asset Change of Estimation",
    "version": "8.0.1.0.2",
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
        "security/res_groups_data.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/base_sequence_configurator_data.xml",
        "data/base_workflow_policy_data.xml",
        "data/account_asset_depreciation_line_subtype_data.xml",
        "menu.xml",
        "views/account_asset_asset_views.xml",
        "views/account_asset_config_setting_views.xml",
        "views/account_asset_change_estimation_useful_life_views.xml",
        "views/account_asset_change_estimation_salvage_views.xml",
    ],
    "demo": [
        "demo/tier_definition_demo.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
}
