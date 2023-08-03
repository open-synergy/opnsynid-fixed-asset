# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FixedAssetCategory(models.Model):
    _name = "fixed.asset.category"
    _inherit = [
        "mixin.master_data",
    ]
    _description = "Fixed Asset Category"
    _order = "name"

    @api.model
    def _get_method(self):
        result = [
            ("linear", _("Linear")),
            ("degressive", _("Degressive")),
            ("degr-linear", _("Degressive-Linear")),
        ]
        return result

    @api.model
    def _get_method_time(self):
        result = [
            ("year", _("Number of Years")),
            ("month", _("Number of Months")),
        ]
        return result

    name = fields.Char(
        string="Category",
    )

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self._default_company_id(),
    )
    account_analytic_id = fields.Many2one(
        string="Analytic account",
        comodel_name="account.analytic.account",
    )
    account_asset_id = fields.Many2one(
        string="Asset Account",
        comodel_name="account.account",
        required=True,
        domain=[("internal_type", "=", "other")],
    )
    account_depreciation_id = fields.Many2one(
        string="Depreciation Account",
        comodel_name="account.account",
        required=True,
        domain=[("internal_type", "=", "other")],
    )
    account_expense_depreciation_id = fields.Many2one(
        string="Depr. Expense Account",
        comodel_name="account.account",
        required=True,
        domain=[("internal_type", "=", "other")],
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        domain=[
            ("type", "=", "general"),
        ],
    )
    method = fields.Selection(
        string="Computation Method",
        selection=lambda self: self._get_method(),
        required=True,
        help="Choose the method to use to compute "
        "the amount of depreciation lines.\n"
        "  * Linear: Calculated on basis of: "
        "Gross Value / Number of Depreciations\n"
        "  * Degressive: Calculated on basis of: "
        "Residual Value * Degressive Factor"
        "  * Degressive-Linear (only for Time Method = Year): "
        "Degressive becomes linear when the annual linear "
        "depreciation exceeds the annual degressive depreciation",
        default="linear",
    )
    method_number = fields.Integer(
        string="Number of Years",
        help="The number of years needed to depreciate your asset",
        default=5,
    )
    method_period = fields.Selection(
        string="Period Length",
        selection=[
            ("month", "Month"),
            ("quarter", "Quarter"),
            ("year", "Year"),
        ],
        required=True,
        help="Period length for the depreciation accounting entries",
        default="year",
    )
    method_progress_factor = fields.Float(
        string="Degressive Factor",
        default=0.3,
    )
    method_time = fields.Selection(
        string="Time Method",
        selection=lambda self: self._get_method_time(),
        required=True,
        help="Choose the method to use to compute the dates and "
        "number of depreciation lines.\n"
        "  * Number of Years: Specify the number of years "
        "for the depreciation.\n",
        default="year",
    )
    prorata = fields.Boolean(
        string="Prorata Temporis",
        help="Indicates that the first depreciation entry for this asset "
        "has to be done from the depreciation start date instead of "
        "the first day of the fiscal year.",
    )
    open_asset = fields.Boolean(
        string="Skip Draft State",
        help="Check this if you want to automatically confirm the assets "
        "of this category when created by invoices.",
    )
    date_min_prorate = fields.Integer(
        string="Date Min. to Prorate",
        default=15,
    )

    @api.constrains(
        "method",
        "method_time",
    )
    def _check_method(self):
        str_error = _("Degressive-Linear is only supported for Time Method = Year.")
        if self.method == "degr-linear" and self.method_time != "year":
            raise UserError(str_error)

    @api.onchange(
        "method_time",
    )
    def onchange_prorata(self):
        self.prorata = False
        if self.method_time != "year":
            self.prorata = True

    @api.model
    def create(self, values):
        _super = super(FixedAssetCategory, self)

        if values.get("method_time") != "year" and not values.get("prorata"):
            values["prorata"] = True
        result = _super.create(values)

        obj_account_account = self.env["account.account"]
        account_asset_id = values.get("account_asset_id")

        if account_asset_id:
            account = obj_account_account.browse(account_asset_id)
            if not account.fixed_asset_category_id:
                account.write({"fixed_asset_category_id": result.id})
        return result

    def write(self, values):
        _super = super(FixedAssetCategory, self)

        if values.get("method_time"):
            if values["method_time"] != "year" and not values.get("prorata"):
                values["prorata"] = True
        result = _super.write(values)

        obj_account_account = self.env["account.account"]

        for rec in self:
            account_asset_id = values.get("account_asset_id")
            if account_asset_id:
                account = obj_account_account.browse(account_asset_id)
                if not account.fixed_asset_category_id:
                    account.write({"fixed_asset_category_id": rec.id})
        return result
