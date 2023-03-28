# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


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
