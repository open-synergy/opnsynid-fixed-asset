# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class FixedAssetUsefulLifeEstimationChange(models.Model):
    _name = "fixed_asset_useful_life_estimation_change"
    _description = "Fixed Asset Useful Life Estimation Change"
    _inherit = [
        "mixin.transaction_confirm",
        "mixin.transaction_done",
        "mixin.transaction_cancel",
    ]

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_multiple_approval_page = True
    _automatically_insert_done_button = False
    _automatically_insert_done_policy_fields = False

    _statusbar_visible_label = "draft,confirm,done"

    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]

    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "action_done",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "done"

    asset_id = fields.Many2one(
        comodel_name="fixed.asset.asset",
        string="Fixed Asset",
        required=True,
        ondelete="restrict",
    )
    date = fields.Date(string="Date", required=True)
    asset_value_history_id = fields.Many2one(
        comodel_name="fixed.asset.depreciation.line",
        string="Asset Value History",
        readonly=True,
    )
    depreciation_history_id = fields.Many2one(
        comodel_name="fixed.asset.depreciation.line",
        string="Depreciation History History",
        readonly=True,
    )
    previous_method_number = fields.Integer(
        string="Previous Method Number",
        required=True,
        readonly=True,
    )
    previous_method_period = fields.Selection(
        selection=[
            ("month", "Month"),
            ("quarter", "Quarter"),
            ("year", "Year"),
        ],
        string="Previous Method Period",
        readonly=True,
    )
    method_number = fields.Integer(string="Method Number", required=True)
    method_period = fields.Selection(
        selection=[
            ("month", "Month"),
            ("quarter", "Quarter"),
            ("year", "Year"),
        ],
        string="Method Period",
        required=True,
    )
    state = fields.Selection(
        string="State",
        default="draft",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
            ("reject", "Rejected"),
        ],
    )

    @api.model
    def _get_policy_field(self):
        res = super(FixedAssetUsefulLifeEstimationChange, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
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

    @ssi_decorator.post_done_action()
    def _10_create_adjustment_depreciation(self):
        self.ensure_one()
        if not self._check_create_adjustment():
            return False

        Line = self.env["fixed.asset.depreciation.line"]
        adj = Line.create(self._prepare_depreciation())
        adj.create_move()

        self.write(
            {
                "depreciation_history_id": adj.id,
            }
        )

    @ssi_decorator.post_done_action()
    def _20_create_asset_value(self):
        self.ensure_one()
        Line = self.env["fixed.asset.depreciation.line"]
        asset_value = Line.create(self._prepare_asset_value())
        self.write(
            {
                "asset_value_history_id": asset_value.id,
            }
        )

    @ssi_decorator.post_done_action()
    def _30_update_asset_useful_file(self):
        self.ensure_one()
        self.asset_id.write(
            {
                "method_number": self.method_number,
                "method_period": self.method_period,
            }
        )

    @ssi_decorator.post_done_action()
    def _40_compute_asset_depreciation_board(self):
        self.ensure_one()
        self.asset_id.compute_depreciation_board()

    def _prepare_asset_value(self):
        self.ensure_one()
        subtype = self.env.ref(
            "ssi_fixed_asset_useful_life_estimation_change."
            "depr_line_subtype_useful_life"
        )
        return {
            "name": self._get_asset_value_name(),
            "subtype_id": subtype.id,
            "previous_id": self.asset_id.last_posted_depreciation_line_id.id,
            "type": "create",
            "line_date": self.date,
            "amount": 0.0,
            "init_entry": True,
            "asset_id": self.asset_id.id,
        }

    def _get_asset_value_name(self):
        self.ensure_one()
        name = "Asset value of %s" % (self.name)
        return name

    def _check_create_adjustment(self):
        self.ensure_one()
        if not self.asset_id.last_depreciation_id:
            return False

        if (
            self.asset_id.last_depreciation_id.line_date
            == self._get_depreciation_date()
        ):
            return False

        return True

    def _get_depreciation_date(self):
        self.ensure_one()
        dt_depreciation = self.date + relativedelta(day=1, days=-1)
        return dt_depreciation

    def _prepare_depreciation(self):
        self.ensure_one()
        subtype = self.env.ref(
            "ssi_fixed_asset_useful_life_estimation_change."
            "depr_line_subtype_useful_life"
        )
        return {
            "name": self._get_depreciation_name(),
            "subtype_id": subtype.id,
            "previous_id": self.asset_id.last_posted_depreciation_line_id.id,
            "type": "depreciate",
            "line_date": self._get_depreciation_date().strftime("%Y-%m-%d"),
            "amount": self._get_depreciation_amount(),
            "asset_id": self.asset_id.id,
        }

    def _get_depreciation_name(self):
        self.ensure_one()
        name = "Depreciation adjustment of %s" % (self.name)
        return name

    def _get_depreciation_amount(self):
        self.ensure_one()

        table = self.asset_id._compute_depreciation_table()
        depreciation_date = self._get_depreciation_date()
        year_amount = 0.0

        for year in table:
            if (
                year["date_start"] <= depreciation_date
                and year["date_stop"] >= depreciation_date
            ):
                year_amount = year["fy_amount"]
                break

        coef = self._get_depreciation_date().month
        period_amount = year_amount / 12.0
        return coef * period_amount

    @api.onchange("asset_id")
    def onchange_method_number(self):
        self.method_number = False
        if self.asset_id:
            self.method_number = self.asset_id.method_number

    @api.onchange("asset_id")
    def onchange_method_period(self):
        self.method_period = False
        if self.asset_id:
            self.method_period = self.asset_id.method_period

    @api.onchange("asset_id")
    def onchange_previous_method_number(self):
        self.previous_method_number = False
        if self.asset_id:
            self.previous_method_number = self.asset_id.method_number

    @api.onchange("asset_id")
    def onchange_previous_method_period(self):
        self.previous_method_period = False
        if self.asset_id:
            self.previous_method_period = self.asset_id.method_period
