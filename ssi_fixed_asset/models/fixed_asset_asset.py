# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import calendar
import logging
from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import numpy as np
except (ImportError, IOError) as err:
    _logger.debug(err)


class DummyFy(object):
    def __init__(self, *args, **argv):
        for key, arg in argv.items():
            setattr(self, key, arg)


class FixedAssetAsset(models.Model):
    _name = "fixed.asset.asset"
    _description = "Fixed Asset"
    _inherit = [
        "mixin.transaction_confirm",
        "mixin.transaction_cancel",
        "mixin.transaction_open",
        "mixin.transaction_done",
    ]
    _order = "date_start desc, name"
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"
    _after_approved_method = "action_open"
    _create_sequence_state = "open"
    _done_state = "close"
    _document_number_field = "code"

    @api.model
    def _get_policy_field(self):
        res = super(FixedAssetAsset, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "open_ok",
            "approve_ok",
            "done_ok",
            "cancel_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    account_move_line_ids = fields.One2many(
        string="Entries",
        comodel_name="account.move.line",
        inverse_name="fixed_asset_id",
        readonly=True,
        copy=False,
    )
    asset_acquisition_move_line_id = fields.Many2one(
        string="Acquisiton Journal Item",
        comodel_name="account.move.line",
        readonly=True,
        ondelete="restrict",
    )
    asset_acquisition_move_id = fields.Many2one(
        string="Acquisiton Journal Entry",
        comodel_name="account.move",
        related="asset_acquisition_move_line_id.move_id",
        readonly=True,
    )

    @api.depends(
        "depreciation_line_ids",
    )
    def _compute_move_line_check(self):
        for document in self:
            document.move_line_check = bool(
                document.depreciation_line_ids.filtered("move_id")
            )

    move_line_check = fields.Boolean(
        string="Has accounting entries",
        compute="_compute_move_line_check",
    )

    def name_get(self):
        result = []
        for rec in self:
            if rec.code:
                name = "[{}] {}".format(rec.code, rec.name)
            else:
                name = "%s" % (rec.name)
            result.append((rec.id, name))
        return result

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        res = super(FixedAssetAsset, self).name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        args = list(args or [])
        if name:
            criteria = ["|", ("code", operator, name), ("name", operator, name)]
            criteria = criteria + args
            asset_ids = self.search(criteria, limit=limit)
            if asset_ids:
                return asset_ids.name_get()
        return res

    name = fields.Char(
        string="Asset Name",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=False,
    )
    code = fields.Char(
        string="Reference",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default="/",
        copy=False,
        required=True,
    )
    purchase_value = fields.Float(
        string="Purchase Value",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="\nThe Asset Value is calculated as follows:"
        "\nPurchase Value - Salvage Value.",
    )

    def _asset_value_compute(self):
        self.ensure_one()
        if self.type == "view":
            asset_value = 0.0
        else:
            asset_value = self.purchase_value - self.salvage_value
        return asset_value

    def _value_get(self):
        self.ensure_one()
        asset_value = self._asset_value_compute()
        for child in self.child_ids:
            asset_value += (
                child.type == "normal"
                and child._asset_value_compute()
                or child._value_get()
            )
        return asset_value

    @api.model
    def _get_asset_value_field(self):
        return [
            ("+", "purchase_value"),
        ]

    def _get_asset_value(self):
        """
        Dynamically add/subsstract asset value from list.
        List of fields and their sign will be provided by
        _get_asset_value_field method.
        This will allow modification for other fixed asset event
        (e.g improvement or impairment)
        """
        self.ensure_one()
        result = 0.0
        for field_dict in self._get_asset_value_field():
            if field_dict[0] == "+":
                result += getattr(self, field_dict[1])
            else:
                result -= getattr(self, field_dict[1])
        return result

    @api.depends(
        "purchase_value",
        "salvage_value",
        "type",
        "method",
        "child_ids",
        "child_ids.asset_value",
        "child_ids.parent_id",
    )
    def _compute_asset_value(self):
        for asset in self:
            if asset.type == "view":
                asset_value = 0.0
                for child in asset.child_ids:
                    if child.state == "open" and child.type == "normal":
                        asset_value += child.asset_value
                asset.asset_value = asset_value
            elif asset.method in ["linear-limit", "degr-limit"]:
                asset.asset_value = asset._get_asset_value()
            else:
                asset.asset_value = asset._get_asset_value()

    asset_value = fields.Float(
        string="Asset Value",
        compute=_compute_asset_value,
        store=True,
        help="This amount represent the initial value of the asset.",
    )

    def _get_additional_depreciated_value(self):
        self.ensure_one()
        result = 0.0
        for field_dict in self._get_additional_depreciated_value_field():
            if field_dict[0] == "+":
                result += getattr(self, field_dict[1])
            else:
                result -= getattr(self, field_dict[1])
        return result

    @api.model
    def _get_additional_depreciated_value_field(self):
        return []

    @api.depends(
        "asset_value",
        "depreciation_line_ids",
        "depreciation_line_ids.amount",
        "depreciation_line_ids.previous_id",
        "depreciation_line_ids.init_entry",
        "depreciation_line_ids.move_id",
        "child_ids",
        "child_ids.value_residual",
        "child_ids.value_depreciated",
        "child_ids.parent_id",
    )
    def _compute_depreciation(self):
        for asset in self:
            if asset.type == "normal":
                lines = asset.depreciation_line_ids.filtered(
                    lambda l: l.type in ("depreciate", "remove")
                    and (l.init_entry or l.move_check)
                )
                value_depreciated = (
                    sum(totl.amount for totl in lines)
                    + asset._get_additional_depreciated_value()
                )
                asset.value_residual = asset._get_asset_value() - value_depreciated
                asset.value_depreciated = value_depreciated
            else:
                value_residual = value_depreciated = 0.0
                for child in asset.child_ids:
                    if child.state == "open" and child.type == "normal":
                        value_residual += child.value_residual
                        value_depreciated += child.value_depreciated
                asset.value_residual = value_residual
                asset.value_depreciated = value_depreciated

    value_residual = fields.Float(
        string="Residual Value",
        compute=_compute_depreciation,
        store=True,
    )
    value_depreciated = fields.Float(
        string="Depreciated Value",
        compute=_compute_depreciation,
        store=True,
    )
    salvage_value = fields.Float(
        string="Salvage Value",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="The estimated value that an asset will realize upon "
        "its sale at the end of its useful life.\n"
        "This value is used to determine the depreciation amounts.",
    )
    note = fields.Text(
        string="Note",
    )
    category_id = fields.Many2one(
        string="Asset Category",
        comodel_name="fixed.asset.category",
        change_default=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    parent_id = fields.Many2one(
        string="Parent Asset",
        comodel_name="fixed.asset.asset",
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain=[("type", "=", "view")],
        ondelete="restrict",
    )
    parent_left = fields.Integer(
        string="Parent Left",
        index=True,
    )
    parent_right = fields.Integer(
        string="Parent Right",
        index=True,
    )
    child_ids = fields.One2many(
        string="Child Assets",
        comodel_name="fixed.asset.asset",
        inverse_name="parent_id",
    )
    date_start = fields.Date(
        string="Purchase Date",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=datetime.now().strftime("%Y-%m-%d"),
        help="You should manually add depreciation lines "
        "with the depreciations of previous fiscal years "
        "if the Depreciation Start Date is different from the date "
        "for which accounting entries need to be generated.",
    )
    date_remove = fields.Date(
        string="Asset Removal Date",
        readonly=True,
        copy=False,
    )
    state = fields.Selection(
        string="Status",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("reject", "Rejected"),
            ("open", "Running"),
            ("close", "Close"),
            ("removed", "Removed"),
            ("cancel", "Cancelled"),
        ],
        required=True,
        readonly=True,
        copy=False,
        default="draft",
        help="When an asset is created, the status is 'Draft'.\n"
        "If the asset is confirmed, the status goes in 'Running' "
        "and the depreciation lines can be posted "
        "to the accounting.\n"
        "If the last depreciation line is posted, "
        "the asset goes into the 'Close' status.\n"
        "When the removal entries are generated, "
        "the asset goes into the 'Removed' status.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    def _get_method(self):
        return self.env["fixed.asset.category"]._get_method()

    method = fields.Selection(
        string="Computation Method",
        selection=lambda self: self._get_method(),
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default="linear",
        help="Choose the method to use to compute "
        "the amount of depreciation lines.\n"
        "  * Linear: Calculated on basis of: "
        "Gross Value / Number of Depreciations\n"
        "  * Degressive: Calculated on basis of: "
        "Residual Value * Degressive Factor"
        "  * Degressive-Linear (only for Time Method = Year): "
        "Degressive becomes linear when the annual linear "
        "depreciation exceeds the annual degressive depreciation",
    )
    method_number = fields.Integer(
        string="Number of Periods",
        readonly=True,
        default=5,
        states={"draft": [("readonly", False)]},
        help="The number of years needed to depreciate your asset",
    )
    method_period = fields.Selection(
        string="Period Length",
        selection=[
            ("month", "Month"),
            ("quarter", "Quarter"),
            ("year", "Year"),
        ],
        required=True,
        readonly=True,
        default="year",
        states={"draft": [("readonly", False)]},
        help="Period length for the depreciation accounting entries",
    )
    method_end = fields.Date(
        string="Ending Date",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    method_progress_factor = fields.Float(
        string="Degressive Factor",
        readonly=True,
        default=0.3,
        states={"draft": [("readonly", False)]},
    )

    def _get_method_time(self):
        return self.env["fixed.asset.category"]._get_method_time()

    method_time = fields.Selection(
        string="Time Method",
        selection=lambda self: self._get_method_time(),
        required=True,
        readonly=True,
        default="year",
        states={"draft": [("readonly", False)]},
        help="Choose the method to use to compute the dates and "
        "number of depreciation lines.\n"
        "  * Number of Years: Specify the number of years "
        "for the depreciation.\n",
    )
    prorata = fields.Boolean(
        string="Prorata Temporis",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Indicates that the first depreciation entry for this asset "
        "have to be done from the depreciation start date instead "
        "of the first day of the fiscal year.",
    )
    depreciation_line_ids = fields.One2many(
        string="Depreciation Lines",
        comodel_name="fixed.asset.depreciation.line",
        inverse_name="asset_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
    )
    type = fields.Selection(
        string="Type",
        selection=[
            ("view", "View"),
            ("normal", "Normal"),
        ],
        required=True,
        readonly=True,
        default="normal",
        states={"draft": [("readonly", False)]},
    )
    company_currency_id = fields.Many2one(
        string="Company Currency",
        related="company_id.currency_id",
        readonly=True,
    )
    account_analytic_id = fields.Many2one(
        string="Analytic account",
        comodel_name="account.analytic.account",
    )

    def _get_method_time_coefficient(self):
        self.ensure_one()
        result = 0
        if self.method_time == "year":
            result = 12
        elif self.method_time == "month":
            result = 1
        return result

    def _get_method_period_coefficient(self):
        self.ensure_one()
        return 1

    def _get_numpy_date_unit(self):
        self.ensure_one()
        return "M"

    @api.depends(
        "method_time",
        "method_number",
        "method_period",
        "depreciation_line_ids",
        "depreciation_line_ids.line_date",
    )
    def _compute_method_period_number(self):
        for asset in self:
            method_period_start_number = (
                method_period_depreciated_number
            ) = method_period_remaining_number = method_period_number = 0.0
            if asset.last_posted_asset_value_id:
                asset_value = asset.last_posted_asset_value_id
                depreciation = asset.last_depreciation_id

                coef_method_time = asset._get_method_time_coefficient()
                coef_method_period = asset._get_method_period_coefficient()
                method_period_number = (
                    coef_method_time / coef_method_period
                ) * asset.method_number
                np_date_unit = asset._get_numpy_date_unit()

                dt_asset_start_date = np.datetime64(
                    asset._get_date_start(), np_date_unit
                )

                if asset_value:
                    dt_posted_asset_value_date = np.datetime64(
                        asset_value.line_date, np_date_unit
                    )
                    dt_diff = dt_posted_asset_value_date - dt_asset_start_date
                    method_period_start_number = int(dt_diff / coef_method_period)

                if depreciation and asset_value:
                    # TODO: Pretty sure numpy has method to change string into dt
                    dt_temp = asset_value.line_date
                    dt_temp = dt_temp + relativedelta(day=1, days=-1)
                    dt_temp = np.datetime64(dt_temp, np_date_unit)
                    dt_depreciation = np.datetime64(
                        depreciation.line_date, np_date_unit
                    )
                    method_period_depreciated_number = dt_depreciation - dt_temp
                method_period_remaining_number = (
                    method_period_number
                    - method_period_start_number
                    - int(method_period_depreciated_number)
                )

            asset.method_period_number = method_period_number
            asset.method_period_start_number = method_period_start_number
            asset.method_period_depreciated_number = method_period_depreciated_number
            asset.method_period_remaining_number = method_period_remaining_number

    method_period_number = fields.Integer(
        string="Age Based On Period Lenght",
        compute="_compute_method_period_number",
    )
    method_period_start_number = fields.Integer(
        string="Age On Asset Value Date",
        compute="_compute_method_period_number",
    )
    method_period_depreciated_number = fields.Integer(
        string="Depreciated Age",
        compute="_compute_method_period_number",
    )
    method_period_remaining_number = fields.Integer(
        string="Remaining Age",
        compute="_compute_method_period_number",
    )

    def _prepare_valid_lines_domain(self):
        self.ensure_one()
        return [
            "&",
            "|",
            ("move_check", "=", True),
            ("init_entry", "=", True),
            ("asset_id", "=", self.id),
        ]

    def _get_asset_value_line_domain(self):
        self.ensure_one()
        return [
            ("asset_id", "=", self.id),
            ("type", "=", "create"),
        ]

    @api.depends(
        "depreciation_line_ids",
        "depreciation_line_ids.line_date",
        "depreciation_line_ids.init_entry",
        "depreciation_line_ids.move_check",
        "depreciation_line_ids.type",
    )
    def _compute_last_posted_depreciation_line(self):
        obj_line = self.env["fixed.asset.depreciation.line"]
        for asset in self:
            criteria = asset._prepare_valid_lines_domain()
            lines = obj_line.search(criteria, order="type desc, line_date desc")
            line_id = False
            if len(lines) > 0:
                line_id = lines[0].id
            asset.last_posted_depreciation_line_id = line_id

            criteria = asset._get_asset_value_line_domain()
            lines = obj_line.search(criteria, order="line_date desc, type desc")
            line_id = False
            if len(lines) > 0:
                line_id = lines[0].id
            asset.last_posted_asset_line_id = line_id

    last_posted_depreciation_line_id = fields.Many2one(
        string="Last Posted Depreciation Line",
        comodel_name="fixed.asset.depreciation.line",
        compute="_compute_last_posted_depreciation_line",
    )
    last_posted_asset_line_id = fields.Many2one(
        string="Last Asset Value Depreciation Line",
        comodel_name="fixed.asset.depreciation.line",
        compute="_compute_last_posted_depreciation_line",
    )

    def _prepare_posted_lines_domain(self):
        self.ensure_one()
        date = self.last_posted_asset_line_id.line_date
        return [
            "&",
            "&",
            "&",
            "|",
            ("move_check", "=", True),
            ("init_entry", "=", True),
            ("asset_id", "=", self.id),
            ("type", "=", "depreciate"),
            ("line_date", ">=", date),
            ("subtype_id", "=", False),
        ]

    @api.depends(
        "depreciation_line_ids",
        "depreciation_line_ids.init_entry",
        "depreciation_line_ids.move_check",
        "depreciation_line_ids.type",
    )
    def _compute_posted_depreciation_line_ids(self):
        obj_line = self.env["fixed.asset.depreciation.line"]
        for asset in self:
            domain = asset._prepare_posted_lines_domain()
            posted_lines = obj_line.search(domain, order="line_date desc")
            asset.posted_depreciation_line_ids = posted_lines.ids

    posted_depreciation_line_ids = fields.Many2many(
        string="Posted Depreciation Lines",
        comodel_name="fixed.asset.depreciation.line",
        compute="_compute_posted_depreciation_line_ids",
    )

    def _prepare_posted_asset_value_domain(self):
        self.ensure_one()
        return [
            ("type", "=", "create"),
            ("init_entry", "=", True),
            ("asset_id", "=", self.id),
        ]

    def _prepare_posted_depreciation_domain(self):
        self.ensure_one()
        return [
            "&",
            "&",
            "|",
            ("move_check", "=", True),
            ("init_entry", "=", True),
            ("type", "=", "depreciate"),
            ("asset_id", "=", self.id),
        ]

    def _prepare_posted_history_domain(self):
        self.ensure_one()
        return [
            "&",
            "|",
            ("move_check", "=", True),
            ("init_entry", "=", True),
            ("asset_id", "=", self.id),
        ]

    def _prepare_unposted_history_domain(self):
        self.ensure_one()
        return [
            ("move_check", "=", False),
            ("init_entry", "=", False),
            ("asset_id", "=", self.id),
        ]

    @api.depends(
        "depreciation_line_ids",
        "depreciation_line_ids.init_entry",
        "depreciation_line_ids.move_check",
        "depreciation_line_ids.type",
    )
    def _compute_asset_histories(self):
        obj_line = self.env["fixed.asset.depreciation.line"]
        for asset in self:
            last_posted_asset_value = (
                last_posted_depreciation
            ) = last_posted_history = False

            posted_asset_value_domain = asset._prepare_posted_asset_value_domain()
            posted_asset_values = obj_line.search(
                posted_asset_value_domain, order="line_date, type"
            )

            if len(posted_asset_values) > 0:
                last_posted_asset_value = posted_asset_values[-1]

            posted_depreciation_domain = asset._prepare_posted_depreciation_domain()
            posted_depreciations = obj_line.search(
                posted_depreciation_domain, order="line_date, type"
            )

            if len(posted_depreciations) > 0:
                last_posted_depreciation = posted_depreciations[-1]

            posted_history_domain = asset._prepare_posted_history_domain()
            posted_histories = obj_line.search(
                posted_history_domain, order="line_date, type"
            )

            if len(posted_histories) > 0:
                last_posted_history = posted_histories[-1]

            unposted_history_domain = asset._prepare_unposted_history_domain()
            unposted_histories = obj_line.search(
                unposted_history_domain, order="line_date, type"
            )

            asset.posted_asset_value_ids = posted_asset_values.ids
            asset.last_posted_asset_value_id = (
                last_posted_asset_value and last_posted_asset_value.id or False
            )
            asset.posted_depreciation_ids = posted_depreciations.ids
            asset.last_depreciation_id = (
                last_posted_depreciation and last_posted_depreciation.id or False
            )
            asset.unposted_history_ids = unposted_histories.ids
            asset.posted_history_ids = posted_histories.ids
            asset.last_posted_history_id = (
                last_posted_history and last_posted_history.id or False
            )

    posted_asset_value_ids = fields.Many2many(
        string="Posted Asset Value Histories",
        comodel_name="fixed.asset.depreciation.line",
        compute="_compute_asset_histories",
    )
    last_posted_asset_value_id = fields.Many2one(
        string="Last Posted Asset Value History",
        comodel_name="fixed.asset.depreciation.line",
        compute="_compute_asset_histories",
    )
    posted_depreciation_ids = fields.Many2many(
        string="Posted Depreciation Histories",
        comodel_name="fixed.asset.depreciation.line",
        compute="_compute_asset_histories",
    )
    last_depreciation_id = fields.Many2one(
        string="Last Depreciation History",
        comodel_name="fixed.asset.depreciation.line",
        compute="_compute_asset_histories",
    )
    unposted_history_ids = fields.Many2many(
        string="Unposted Asset Histories",
        comodel_name="fixed.asset.depreciation.line",
        compute="_compute_asset_histories",
    )
    posted_history_ids = fields.Many2many(
        string="Posted Asset Histories",
        comodel_name="fixed.asset.depreciation.line",
        compute="_compute_asset_histories",
    )
    last_posted_history_id = fields.Many2one(
        string="Last Posted History",
        comodel_name="fixed.asset.depreciation.line",
        compute="_compute_asset_histories",
    )
    prorate_by_month = fields.Boolean(
        string="Prorate by Month",
        default=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date_min_prorate = fields.Integer(
        string="Date Min. to Prorate",
        default=15,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    # Policy Field
    done_ok = fields.Boolean(
        string="Can Close",
    )

    @api.model
    def create(self, vals):
        if vals.get("method_time") != "year" and not vals.get("prorata"):
            vals["prorata"] = True
        asset = super(FixedAssetAsset, self).create(vals)
        if self._context.get("create_asset_from_move_line"):
            asset.salvage_value = 0.0
        if asset.type == "normal":
            asset_line_obj = self.env["fixed.asset.depreciation.line"]
            line_name = asset._get_depreciation_entry_name(0)
            asset_date_start = asset._get_date_start()
            asset_line_vals = {
                "amount": asset.asset_value,
                "asset_id": asset.id,
                "name": line_name,
                "line_date": asset_date_start,
                "init_entry": True,
                "type": "create",
            }
            asset_line_obj.create(asset_line_vals)
            if not asset.policy_template_id:
                asset.onchange_policy_template_id()
        return asset

    def write(self, vals):
        _super = super(FixedAssetAsset, self)
        res = _super.write(vals)
        context = self.env.context

        if vals.get("method_time"):
            if vals["method_time"] != "year" and not vals.get("prorata"):
                vals["prorata"] = True
        for asset in self:
            asset_type = vals.get("type") or asset.type

            if asset_type == "view" or context.get("asset_validate_from_write"):
                continue
            if asset.category_id.open_asset and context.get(
                "create_asset_from_move_line"
            ):
                asset.compute_depreciation_board()
                ctx = dict(context, asset_validate_from_write=True)
                asset.with_context(ctx).validate()
        return res

    def copy(self, default=None):
        _super = super(FixedAssetAsset, self)
        if default is None:
            default = {}
        update_vals = {
            "depreciation_line_ids": [],
            "account_move_line_ids": [],
            "state": "draft",
        }
        default.update(update_vals)

        return _super.copy(default)

    # -- Other Methods --
    def _get_date_start(self):
        self.ensure_one()
        dt_date_start = self.date_start
        if self.prorate_by_month:
            if dt_date_start.day > self.date_min_prorate:
                dt_date_start = dt_date_start + relativedelta(day=1, months=1)

        return dt_date_start

    def _get_assets(self):
        asset_ids = []
        for asset in self:

            def _parent_get(record):
                asset_ids.append(record.id)
                if record.parent_id:
                    _parent_get(record.parent_id)

            _parent_get(asset)
        return asset_ids

    def _get_assets_from_dl(self):
        self.ensure_one()
        asset_ids = []
        filter_dl_ids = self.depreciation_line_ids.filtered(
            lambda x: x.type in ["depreciate", "remove"] and (x.init_entry or x.move_id)
        )
        for dl in filter_dl_ids:
            res = []

            def _parent_get(record):
                res.append(record.id)
                if record.parent_id:
                    res.append(_parent_get(record.parent_id))

            _parent_get(dl.asset_id)
            for asset_id in res:
                if asset_id not in asset_ids:
                    asset_ids.append(asset_id)
        return asset_ids

    @api.model
    def _get_period(self):
        context = self.env.context
        ctx = dict(context or {}, account_period_prefer_normal=True)
        periods = self.env["account.period"].with_context(ctx).find()
        if periods:
            return periods[0]
        else:
            return False

    def _get_first_period_amount(
        self, table, entry, depreciation_start_date, line_dates
    ):
        """
        Return prorata amount for Time Method "Year" in case of
        "Prorata Temporis"
        """
        amount = entry.get("period_amount")
        if self.prorata:
            dates = filter(lambda x: x <= entry["date_stop"], line_dates)
            full_periods = len(dates) - 1
            amount = entry["fy_amount"] - amount * full_periods
        return amount

    def _get_depreciation_entry_name(self, seq):
        """use this method to customise the name of the accounting entry"""
        return (self.code or str(self.id)) + "/" + str(seq)

    def _prepare_old_lines_domain(self):
        self.ensure_one()
        return [
            ("asset_id", "=", self.id),
            ("type", "=", "depreciate"),
            ("move_id", "=", False),
            ("init_entry", "=", False),
        ]

    def _delete_unposted_history(self):
        self.ensure_one()
        line_obj = self.env["fixed.asset.depreciation.line"]
        domain = self._prepare_old_lines_domain()
        old_lines = line_obj.search(domain)
        if old_lines:
            old_lines.unlink()

    def _compute_starting_depreciation_entry(self, table):
        self.ensure_one()
        # TODO: Use new helper field
        line_obj = self.env["fixed.asset.depreciation.line"]
        domain = self._prepare_posted_lines_domain()
        posted_lines = line_obj.search(domain, order="line_date desc")

        # TODO: Use new helper field
        last_line = self.last_posted_depreciation_line_id

        if len(posted_lines) > 0:
            last_depreciation_date = last_line.line_date
            last_date_in_table = table[-1]["lines"][-1]["date"]
            if last_date_in_table <= last_depreciation_date:
                raise UserError(
                    _(
                        "The duration of the asset conflicts with the "
                        "posted depreciation table entry dates."
                    )
                )

            for _table_i, entry in enumerate(table):
                # residual_amount_table = \
                #     entry["lines"][-1]["remaining_value"]
                if entry["date_start"] <= last_depreciation_date <= entry["date_stop"]:
                    break
            if entry["date_stop"] == last_depreciation_date:
                _table_i += 1
                _line_i = 0
            else:
                entry = table[_table_i]
                date_min = entry["date_start"]
                for _line_i, line in enumerate(entry["lines"]):
                    # residual_amount_table = line["remaining_value"]
                    if date_min <= last_depreciation_date <= line["date"]:
                        break
                    date_min = line["date"]
                if line["date"] == last_depreciation_date:
                    _line_i += 1
            table_i_start = _table_i
            line_i_start = _line_i
        else:  # no posted lines
            table_i_start = 0
            line_i_start = 0

        return table_i_start, line_i_start

    def _create_depreciation_lines(self, table, table_index_start, line_index_start):
        self.ensure_one()
        line_i_start = line_index_start
        table_i_start = table_index_start
        posted_lines = self.posted_depreciation_line_ids
        obj_line = self.env["fixed.asset.depreciation.line"]
        seq = len(posted_lines)
        depr_line = self.last_posted_history_id
        # depr_line = self.last_posted_depreciation_line_id

        # last_date = table[-1]["lines"][-1]["date"]
        depreciated_value = sum(vari_l.amount for vari_l in posted_lines)
        for entry in table[table_i_start:]:
            for line in entry["lines"][line_i_start:]:
                seq += 1
                name = self._get_depreciation_entry_name(seq)
                amount = line["amount"]

                if amount:
                    vals = {
                        "previous_id": depr_line.id,
                        "amount": amount,
                        "asset_id": self.id,
                        "name": name,
                        "line_date": line["date"].strftime("%Y-%m-%d"),
                        "init_entry": entry["init"],
                    }
                    depreciated_value += amount
                    depr_line = obj_line.create(vals)
                else:
                    seq -= 1
            line_i_start = 0

    def _compute_depreciation_amount_per_fiscal_year(self, table, line_dates):
        digits = self.env["decimal.precision"].precision_get("Account")
        fy_residual_amount = amount_to_depr = self._get_amount_to_depreciate()
        i_max = len(table) - 1
        asset_sign = self._get_asset_value() >= 0 and 1 or -1

        for i, entry in enumerate(table):

            year_amount = self._compute_year_amount(amount_to_depr, fy_residual_amount)

            if i == i_max:
                if self.method == "degressive":
                    year_amount = fy_residual_amount - self.salvage_value

            if self.method_period == "year":
                period_amount = year_amount
            elif self.method_period == "quarter":
                period_amount = year_amount / 4
            elif self.method_period == "month":
                period_amount = year_amount / 12

            if i == i_max:
                if self.method == "linear":
                    fy_amount = fy_residual_amount
                else:
                    fy_amount = fy_residual_amount - self.salvage_value
            else:
                firstyear = i == 0 and True or False
                fy_factor = self._get_fy_duration_factor(entry, self, firstyear)

                fy_amount = year_amount * fy_factor

            if asset_sign * (fy_amount - fy_residual_amount) > 0:
                fy_amount = fy_residual_amount

            period_amount = round(period_amount, digits)
            fy_amount = round(fy_amount, digits)

            entry.update(
                {
                    "period_amount": period_amount,
                    "fy_amount": fy_amount,
                }
            )

            fy_residual_amount -= fy_amount
            if round(fy_residual_amount, digits) == 0:
                break

        i_max = i
        table = table[: i_max + 1]
        return table

    def compute_depreciation_board(self):
        for asset in self.sudo():
            if asset.value_residual == 0.0:
                continue
            asset._delete_unposted_history()
            table = asset._compute_depreciation_table()

            if not table:
                continue

            table_i_start, line_i_start = asset._compute_starting_depreciation_entry(
                table
            )
            asset._create_depreciation_lines(table, table_i_start, line_i_start)
            asset._recompute_lines()

    def _recompute_lines(self):
        self.ensure_one()
        domain = [
            ("asset_id", "=", self.id),
            ("type", "=", "depreciate"),
            ("move_id", "=", False),
            ("init_entry", "=", False),
        ]
        Line = self.env["fixed.asset.depreciation.line"]
        lines = Line.search(domain)
        lines.action_compute()

    def _get_depreciation_start_date(self, fy):
        """
        In case of 'Linear': the first month is counted as a full month
        if the fiscal year starts in the middle of a month.
        """
        if self.prorata:
            depreciation_start_date = self.last_posted_asset_line_id.line_date
        else:
            depreciation_start_date = fy.date_from
        return depreciation_start_date

    def _get_depreciation_stop_date(self, depreciation_start_date):
        if self.method_time == "year" and not self.method_end:
            depreciation_stop_date = depreciation_start_date + relativedelta(
                years=self.method_number, months=-1, day=31
            )
        if self.method_time == "month" and not self.method_end:
            depreciation_stop_date = depreciation_start_date + relativedelta(
                months=self.method_number - 1, day=31
            )
        elif self.method_time == "number":
            if self.method_period == "month":
                depreciation_stop_date = depreciation_start_date + relativedelta(
                    months=self.method_number, days=-1
                )
            elif self.method_period == "quarter":
                m = [x for x in [3, 6, 9, 12] if x >= depreciation_start_date.month][0]
                first_line_date = depreciation_start_date + relativedelta(
                    month=m, day=31
                )
                months = self.method_number * 3
                depreciation_stop_date = first_line_date + relativedelta(
                    months=months - 1, days=-1
                )
            elif self.method_period == "year":
                depreciation_stop_date = depreciation_start_date + relativedelta(
                    years=self.method_number, days=-1
                )
        elif self.method_time == "year" and self.method_end:
            depreciation_stop_date = self.method_end
        return depreciation_stop_date

    def _get_amount_to_depreciate(self):
        self.ensure_one()
        asset_value = self.last_posted_asset_line_id.remaining_value
        if self.method == "linear":
            return asset_value - self.salvage_value
        else:
            return asset_value

    def _compute_line_dates(self, table, start_date, stop_date):
        """
        The posting dates of the accounting entries depend on the
        chosen 'Period Length' as follows:
        - month: last day of the month
        - quarter: last of the quarter
        - year: last day of the fiscal year

        Override this method if another posting date logic is required.
        """
        line_dates = []

        if self.method_period == "month":
            line_date = start_date + relativedelta(day=31)
        if self.method_period == "quarter":
            m = [x for x in [3, 6, 9, 12] if x >= start_date.month][0]
            line_date = start_date + relativedelta(month=m, day=31)
        elif self.method_period == "year":
            line_date = table[0]["date_stop"]

        i = 1
        while line_date < stop_date:
            line_dates.append(line_date)
            if self.method_period == "month":
                line_date = line_date + relativedelta(months=1, day=31)
            elif self.method_period == "quarter":
                line_date = line_date + relativedelta(months=3, day=31)
            elif self.method_period == "year":
                line_date = table[i]["date_stop"]
                i += 1

        # last entry
        if not (self.method_time == "number" and len(line_dates) == self.method_number):
            line_dates.append(line_date)

        return line_dates

    def _get_amount_linear(
        self, depreciation_start_date, depreciation_stop_date, entry
    ):
        """
        Override this method if you want to compute differently the
        yearly amount.
        """
        year = entry["date_stop"].year
        cy_days = calendar.isleap(year) and 366 or 365
        days = (depreciation_stop_date - depreciation_start_date).days + 1
        return (self._get_amount_to_depreciate() / days) * cy_days

    def _compute_year_amount(self, amount_to_depr, residual_amount):
        """
        Localization: override this method to change the degressive-linear
        calculation logic according to local legislation.
        """
        if self.method_time not in ["year", "month"]:
            raise UserError(
                _(
                    "Programming Error!\n"
                    "The '_compute_year_amount' method is only intended for "
                    "Time Method 'Number of Years.''"
                ),
            )

        year_amount_liner_divider = (
            self.method_period_number - self.method_period_start_number
        )
        year_amount_linear = (amount_to_depr / year_amount_liner_divider) * 12

        if self.method == "linear":
            return year_amount_linear

        year_amount_degressive = residual_amount * self.method_progress_factor

        if self.method == "degressive":
            return year_amount_degressive

        if self.method == "degr-linear":
            if year_amount_linear > year_amount_degressive:
                return min(year_amount_linear, residual_amount)
            else:
                return min(year_amount_degressive, residual_amount)

        raise UserError(_("Illegal value %s in asset.method.") % self.method)

    def _get_fy_info(self, date):
        """Return an homogeneus data structure for fiscal years."""
        fy_info = self.company_id.compute_fiscalyear_dates(date)
        if "record" not in fy_info:
            fy_info["record"] = DummyFy(
                date_from=fy_info["date_from"], date_to=fy_info["date_to"]
            )
        return fy_info

    @api.model
    def _get_fy_duration_factor(self, entry, asset, firstyear):
        """
        localization: override this method to change the logic used to
        calculate the impact of extended/shortened fiscal years
        """
        duration_factor = 1.0
        fy_id = entry["fy_id"]
        if asset.prorata:
            if firstyear:
                depreciation_date_start = asset.last_posted_asset_line_id.line_date
                first_fy_asset_days = depreciation_date_start + relativedelta(day=1)

                duration_factor = float(13 - first_fy_asset_days.month) / 12.0

            elif fy_id:
                duration_factor = asset._get_fy_duration(fy_id, option="years")
        elif fy_id:
            fy_months = asset._get_fy_duration(fy_id, option="months")
            duration_factor = float(fy_months) / 12
        return duration_factor

    def _get_fy_duration(self, fy, option="days"):
        """Returns fiscal year duration.

        @param option:
        - days: duration in days
        - months: duration in months,
                  a started month is counted as a full month
        - years: duration in calendar years, considering also leap years
        """
        fy_date_start = fy.date_from
        fy_date_stop = fy.date_to
        days = (fy_date_stop - fy_date_start).days + 1
        months = (
            (fy_date_stop.year - fy_date_start.year) * 12
            + (fy_date_stop.month - fy_date_start.month)
            + 1
        )
        if option == "days":
            return days
        elif option == "months":
            return months
        elif option == "years":
            year = fy_date_start.year
            cnt = fy_date_stop.year - fy_date_start.year + 1
            for i in range(cnt):
                cy_days = calendar.isleap(year) and 366 or 365
                if i == 0:  # first year
                    if fy_date_stop.year == year:
                        duration = (fy_date_stop - fy_date_start).days + 1
                    else:
                        duration = (date(year, 12, 31) - fy_date_start).days + 1
                    factor = float(duration) / cy_days
                elif i == cnt - 1:  # last year
                    duration = (fy_date_stop - date(year, 1, 1)).days + 1
                    factor += float(duration) / cy_days
                else:
                    factor += 1.0
                year += 1
            return factor

    def _compute_depreciation_table_lines(
        self, table, depreciation_start_date, depreciation_stop_date, line_dates
    ):
        digits = self.env["decimal.precision"].precision_get("Asset Depreciation")
        asset_sign = self._get_asset_value() >= 0 and 1 or -1
        i_max = len(table) - 1
        remaining_value = self._get_amount_to_depreciate()
        depreciated_value = 0.0
        for i, entry in enumerate(table):

            lines = []
            fy_amount_check = 0.0
            fy_amount = entry["fy_amount"]
            li_max = len(line_dates) - 1
            for li, line_date in enumerate(line_dates):

                if round(remaining_value, digits) == 0.0:
                    break

                if line_date > min(entry["date_stop"], depreciation_stop_date) and not (
                    i == i_max and li == li_max
                ):
                    break

                if (
                    self.method == "degr-linear"
                    and asset_sign * (fy_amount - fy_amount_check) < 0
                ):
                    break

                amount = entry.get("period_amount")

                # last year, last entry
                # Handle rounding deviations.
                if i == i_max and li == li_max:
                    amount = remaining_value
                    remaining_value = 0.0
                else:
                    remaining_value -= amount

                fy_amount_check += amount
                line = {
                    "date": line_date,
                    "amount": amount,
                    "depreciated_value": depreciated_value,
                    "remaining_value": remaining_value,
                }
                lines.append(line)
                depreciated_value += amount

            # Handle rounding and extended/shortened FY deviations.
            #
            # Remark:
            # In account_asset_management version < 8.0.2.8.0
            # the FY deviation for the first FY
            # was compensated in the first FY depreciation line.
            # The code has now been simplified with compensation
            # always in last FT depreciation line.

            if round(fy_amount_check - fy_amount, digits) != 0:
                diff = fy_amount_check - fy_amount
                amount = amount - diff
                remaining_value += diff
                lines[-1].update(
                    {
                        "amount": amount,
                        "remaining_value": remaining_value,
                    }
                )
                depreciated_value -= diff

            if not lines:
                table.pop(i)
            else:
                entry["lines"] = lines
            line_dates = line_dates[li:]

        for _i, entry in enumerate(table):
            if not entry["fy_amount"]:
                entry["fy_amount"] = sum(var_l["amount"] for var_l in entry["lines"])

    def _compute_depreciation_table(self):  # noqa: C901

        table = []
        if self.method_time in ["year", "number"] and not self.method_number:
            return table

        company = self.company_id
        init_flag = False
        asset_date_start = self.last_posted_asset_line_id.line_date
        fy = self._get_fy_info(asset_date_start)
        fiscalyear_lock_date = company.fiscalyear_lock_date

        if fiscalyear_lock_date and fiscalyear_lock_date >= asset_date_start:
            init_flag = True

        depreciation_start_date = self._get_depreciation_start_date(fy["record"])

        # SPONGE
        # raise UserError(str(depreciation_start_date))

        # depreciation_stop_date = self._get_depreciation_stop_date(
        #     depreciation_start_date
        # )
        depreciation_stop_date = self._get_depreciation_stop_date(
            self._get_date_start()
        )

        # SPONGE
        # raise UserError(str(depreciation_stop_date))

        fy_date_start = asset_date_start

        while fy_date_start <= depreciation_stop_date:
            fy_info = self._get_fy_info(fy_date_start)
            table.append(
                {
                    "fy_id": fy_info["record"],
                    "date_start": fy_info["date_from"],
                    "date_stop": fy_info["date_to"],
                    "init": init_flag,
                }
            )
            fy_date_start = fy_info["date_to"] + relativedelta(days=1)

        # SPONGE
        # raise UserError(str(table))

        # Step 1:
        # Calculate depreciation amount per fiscal year.
        # This is calculation is skipped for method_time != 'year'.
        line_dates = self._compute_line_dates(
            table, depreciation_start_date, depreciation_stop_date
        )

        # SPONGE
        # raise UserError(str(line_dates))

        table = self._compute_depreciation_amount_per_fiscal_year(table, line_dates)

        # SPONGE
        # raise UserError(str(table))

        # Step 2:
        # Spread depreciation amount per fiscal year
        # over the depreciation periods.
        self._compute_depreciation_table_lines(
            table, depreciation_start_date, depreciation_stop_date, line_dates
        )

        # SPONGE
        # raise UserError(str(table))

        return table

    # -- Constrains Methods --
    @api.constrains(
        "method",
        "method_time",
    )
    def _check_method(self):
        str_error = _("Degressive-Linear is only supported for Time Method = Year.")
        if self.method == "degr-linear" and self.method_time != "year":
            raise UserError(str_error)

    # -- Onchange Methods --

    @api.onchange(
        "category_id",
    )
    def onchange_policy_template_id(self):
        template_id = self._get_template_policy()
        self.policy_template_id = template_id

    @api.onchange(
        "category_id",
    )
    def onchange_category_id(self):
        if not self._context.get("create_asset_from_move_line"):
            if self.depreciation_line_ids:
                for line in self.depreciation_line_ids:
                    if line.move_id:
                        raise UserError(
                            _("Error!"),
                            _(
                                "You cannot change the category of an asset "
                                "with accounting entries."
                            ),
                        )
        obj_asset_category = self.env["fixed.asset.category"]
        if self.category_id:
            category = obj_asset_category.browse(self.category_id.id)
            self.method = category.method
            self.method_number = category.method_number
            self.method_time = category.method_time
            self.method_period = category.method_period
            self.method_progress_factor = category.method_progress_factor
            self.prorata = category.prorata
            self.account_analytic_id = category.account_analytic_id.id
            self.date_min_prorate = category.date_min_prorate
            self.prorate_by_month = True

    @api.onchange(
        "category_id",
    )
    def onchange_date_min_prorate(self):
        self.date_min_prorate = False
        if self.category_id:
            self.date_min_prorate = self.category_id.date_min_prorate

    @api.onchange(
        "asset_value",
    )
    def onchange_amount_depreciation_line(self):
        dl_ids = self.depreciation_line_ids.filtered(lambda x: x.type == "create")
        if dl_ids:
            for document in dl_ids:
                document.amount = self.asset_value

    @api.onchange(
        "date_start",
        "prorate_by_month",
        "date_min_prorate",
    )
    def onchange_line_date_depreciation_line(self):
        if self.date_start:
            dl_ids = self.depreciation_line_ids.filtered(lambda x: x.type == "create")
            if dl_ids:
                for document in dl_ids:
                    document.line_date = self._get_date_start()

    @api.onchange(
        "method_time",
    )
    def onchange_method_time(self):
        if self.method_time != "year":
            self.prorata = True

    @api.onchange(
        "type",
    )
    def onchange_type_date_start(self):
        if self.type == "view":
            self.date_start = False

    @api.onchange(
        "type",
    )
    def onchange_type_category_id(self):
        if self.type == "view":
            self.category_id = False

    @api.onchange(
        "type",
    )
    def onchange_type_purchase_value(self):
        if self.type == "view":
            self.purchase_value = 0.0

    @api.onchange(
        "type",
    )
    def onchange_type_salvage_value(self):
        if self.type == "view":
            self.salvage_value = 0.0

    @api.onchange(
        "type",
    )
    def onchange_type_code(self):
        if self.type == "view":
            self.code = False

    @api.onchange(
        "type",
    )
    def onchange_type_depreciation_line_ids(self):
        if self.depreciation_line_ids:
            self.depreciation_line_ids.unlink()

    # -- Workflow Methods --
    def action_approve_approval(self):
        _super = super(FixedAssetAsset, self)
        _super.action_approve_approval()
        for document in self.sudo():
            if document.approved:
                document.validate()

    def validate(self):
        for document in self.sudo():
            currency = document.company_id.currency_id
            if document.type == "normal" and currency.is_zero(document.value_residual):
                document.write(document._prepare_done_data())
            else:
                document.write(document._prepare_open_data())

    def action_cancel(self, cancel_reason=False):
        _super = super(FixedAssetAsset, self)
        res = _super.action_cancel(cancel_reason)
        for record in self.sudo():
            record._unlink_creation_depreciation_line()
        return res

    def _get_account_move_ids(self):
        return self.mapped("account_move_line_ids.move_id")

    def _get_action_account_move(self):
        action = self.env.ref("account." "action_move_journal_line").read()[0]
        return action

    def open_entries(self):
        self.ensure_one()
        account_move_ids = self._get_account_move_ids()
        action = self._get_action_account_move()

        if len(account_move_ids) > 0:
            action["domain"] = [("id", "in", account_move_ids.ids)]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def _unlink_creation_depreciation_line(self):
        self.ensure_one()
        lines = self.depreciation_line_ids.filtered(lambda x: x.type != "create")
        if lines:
            lines.unlink()
