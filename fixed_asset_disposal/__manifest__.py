# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Fixed Asset Disposal",
    "version": "11.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "fixed_asset",
        "ssi_policy_mixin",
        "ssi_multiple_approval_mixin",
        "ssi_state_change_history_mixin",
    ],
    "data": [
        "security/res_groups_data.xml",
        "security/ir.model.access.csv",
        "data/fixed_asset_depreciation_line_subtype_data.xml",
        "data/policy_template_data.xml",
        "data/approval_template_data.xml",
        "data/ir_sequence_data.xml",
        "data/sequence_template_data.xml",
        "menu.xml",
        "views/fixed_asset_disposal_type_views.xml",
        "views/fixed_asset_disposal_views.xml",
    ],
    "demo": [],
    "images": [
        "static/description/banner.png",
    ],
}
