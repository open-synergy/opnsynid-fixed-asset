# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class FixedAssetImprovementType(models.Model):
    _name = "fixed_asset_improvement_type"
    _description = "Fixed Asset Improvement Type"
    _inherit = [
        "mixin.master_data",
    ]

    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        required=True,
    )
    exchange_account_id = fields.Many2one(
        "account.account",
        string="Exchange Account",
        required=True,
    )
    # Fixed Asset Selection
    asset_selection_method = fields.Selection(
        string="Asset Selection Method",
        default="domain",
        required=True,
        selection=[
            ("manual", "Manual"),
            ("domain", "Domain"),
            ("code", "Python Code"),
        ]
    )
    asset_ids = fields.Many2many(
        "fixed.asset.asset",
        string="Assets",
        relation="rel_fixed_asset_improvement_type_2_asset",
        column1="type_id",
        column2="asset_id",
    )
    asset_domain = fields.Text(
        string="Asset Domain",
        default="[]"
    )
    asset_python_code = fields.Text(
        string="Asset Python Code",
        default="result = []"
    )
    # Account Selection
    account_selection_method = fields.Selection(
        string="Account Selection Method",
        default="domain",
        required=True,
        selection=[
            ("manual", "Manual"),
            ("domain", "Domain"),
            ("code", "Python Code"),
        ]
    )
    account_ids = fields.Many2many(
        "account.account",
        string="Accounts",
        relation="rel_fixed_asset_improvement_type_2_account",
        column1="type_id",
        column2="account_id",
    )
    account_domain = fields.Text(
        string="Account Domain",
        default="[]"
    )
    account_python_code = fields.Text(
        string="Account Python Code",
        default="result = []"
    )
