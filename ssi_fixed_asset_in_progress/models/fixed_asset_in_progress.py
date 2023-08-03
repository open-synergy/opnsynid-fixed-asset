# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class FixedAssetInProgress(models.Model):
    _name = "fixed_asset.in_progress"
    _inherit = [
        "mixin.transaction_confirm",
        "mixin.transaction_open",
        "mixin.transaction_done",
        "mixin.transaction_cancel",
        "mixin.transaction_terminate",
        "mixin.print_document",
        "mixin.company_currency",
        "mixin.date_duration",
    ]
    _description = "Fixed Asset In Progress"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"
    _after_approved_method = "action_open"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True

    # Attributes related to add element on form view automatically
    _automatically_insert_multiple_approval_page = True
    _automatically_insert_open_policy_fields = False
    _automatically_insert_open_button = False

    _statusbar_visible_label = "draft,confirm,open,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "terminate_ok",
        "restart_ok",
        "open_ok",
        "done_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "action_done",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "%(ssi_transaction_terminate_mixin.base_select_terminate_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_open",
        "dom_done",
        "dom_cancel",
        "dom_terminate",
    ]

    # Sequence attribute
    _create_sequence_state = "open"

    # Attributes related to add element on duration_view automatically
    _date_start_readonly = True
    _date_end_readonly = True
    _date_end_required = False
    _date_start_states_list = ["draft"]
    _date_start_states_readonly = ["draft"]
    _date_end_states_list = ["open"]
    _date_end_states_readonly = ["open"]

    title = fields.Char(
        string="Fixed Asset Name",
        required=True,
        copy=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    category_id = fields.Many2one(
        string="Category",
        comodel_name="fixed.asset.category",
        required=True,
        copy=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    fixed_asset_in_progress_move_line_ids = fields.One2many(
        string="Fixed Asset in Progress Move Lines",
        comodel_name="account.move.line",
        inverse_name="fixed_asset_in_progress_id",
        readonly=True,
        copy=False,
        states={"open": [("readonly", False)]},
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        copy=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    fixed_asset_account_id = fields.Many2one(
        string="Fixed Asset Account",
        comodel_name="account.account",
        required=True,
        copy=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    fixed_asset_in_progress_account_id = fields.Many2one(
        string="Fixed Asset in Progress Account",
        comodel_name="account.account",
        required=True,
        copy=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    move_line_id = fields.Many2one(
        string="Accounting Entry Item",
        comodel_name="account.move.line",
        copy=False,
        readonly=True,
        ondelete="restrict",
    )

    @api.depends("move_line_id", "move_line_id.fixed_asset_id")
    def _compute_accounting(self):
        for record in self:
            move = fixed_asset = False
            if record.move_line_id:
                move = record.move_line_id.move_id
                fixed_asset = record.move_line_id.fixed_asset_id
            record.move_id = move
            record.fixed_asset_id = fixed_asset

    move_id = fields.Many2one(
        string="Accounting Entry",
        comodel_name="account.move",
        related=False,
        compute="_compute_accounting",
        store=True,
        ondelete="restrict",
    )
    fixed_asset_id = fields.Many2one(
        string="Fixed Asset",
        comodel_name="fixed.asset.asset",
        related=False,
        compute="_compute_accounting",
        store=True,
        ondelete="restrict",
    )

    @api.depends(
        "fixed_asset_in_progress_move_line_ids",
        "fixed_asset_in_progress_move_line_ids.debit",
        "fixed_asset_in_progress_move_line_ids.account_id",
    )
    def _compute_amount(self):
        for record in self:
            amount_in_progress = 0.0
            for line in record.fixed_asset_in_progress_move_line_ids:
                amount_in_progress += line.debit
            record.amount_in_progress = amount_in_progress

    amount_in_progress = fields.Monetary(
        string="Amount in Progress",
        compute="_compute_amount",
        store=True,
        currency_field="company_currency_id",
    )

    state = fields.Selection(
        string="State",
        default="draft",
        required=True,
        readonly=True,
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("open", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancel"),
            ("terminate", "Terminate"),
        ],
    )

    @api.model
    def _get_policy_field(self):
        res = super(FixedAssetInProgress, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "done_ok",
            "open_ok",
            "cancel_ok",
            "terminate_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    def _prepare_done_data(self):
        _super = super(FixedAssetInProgress, self)
        ml = self._create_accounting_entry()
        result = _super._prepare_done_data()
        result.update(
            {
                "move_line_id": ml.id,
                "fixed_asset_id": ml.fixed_asset_id.id,
            }
        )
        return result

    def _prepare_cancel_data(self, cancel_reason=False):
        _super = super(FixedAssetInProgress, self)
        result = _super._prepare_cancel_data(cancel_reason=cancel_reason)
        result.update(
            {
                "date_end": False,
            }
        )
        return result

    def action_cancel(self, cancel_reason=False):
        _super = super(FixedAssetInProgress, self)
        _super.action_cancel(cancel_reason=cancel_reason)
        for record in self.sudo():
            record._unlink_fixed_asset()
            record._unlink_aml()

    def action_open(self):
        _super = super(FixedAssetInProgress, self)
        _super.action_open()
        for record in self.sudo():
            record._unlink_fixed_asset()
            record._unlink_aml()

    def _unlink_fixed_asset(self):
        self.ensure_one()
        if self.fixed_asset_id:
            fixed_asset = self.fixed_asset_id
            self.write(
                {
                    "fixed_asset_id": False,
                }
            )
            fixed_asset.unlink()

    def _unlink_aml(self):
        self.ensure_one()
        if self.move_line_id:
            ml = self.move_line_id
            self.write(
                {
                    "move_line_id": False,
                }
            )
            move = ml.move_id
            move.button_cancel()
            move.with_context(force_delete=True).unlink()

    def _prepare_open_data(self):
        _super = super(FixedAssetInProgress, self)
        result = _super._prepare_open_data()
        result.update(
            {
                "date_end": False,
            }
        )
        return result

    def _create_accounting_entry(self):
        self.ensure_one()
        AccountMove = self.env["account.move"]
        data = self._prepare_accounting_entry()
        move = AccountMove.with_context(check_move_validity=False).create(data)
        ml = self._create_fixed_asset_move_line(move)
        for line in self.fixed_asset_in_progress_move_line_ids:
            line._create_asset_in_progress_reverse_ml(move)
        ml.action_create_fixed_asset()
        return ml

    def _prepare_accounting_entry(self):
        self.ensure_one()
        return {
            "name": self.name,
            "journal_id": self.journal_id.id,
            "date": self.date_end,
        }

    def _create_fixed_asset_move_line(self, move):
        self.ensure_one()
        AML = self.env["account.move.line"]
        data = self._prepare_fixed_asset_move_line(move)
        return AML.with_context(check_move_validity=False).create(data)

    def _prepare_fixed_asset_move_line(self, move):
        self.ensure_one()
        return {
            "move_id": move.id,
            "name": self.title,
            "account_id": self.fixed_asset_account_id.id,
            "debit": self.amount_in_progress,
            "credit": 0.0,
        }

    @api.onchange(
        "category_id",
    )
    def onchange_fixed_asset_in_progress_account_id(self):
        self.fixed_asset_in_progress_account_id = False
        if self.category_id:
            categ = self.category_id
            self.fixed_asset_in_progress_account_id = (
                categ.account_fixed_asset_in_progress_id
            )

    @api.onchange(
        "category_id",
    )
    def onchange_fixed_asset_account_id(self):
        self.fixed_asset_account_id = False
        if self.category_id:
            categ = self.category_id
            self.fixed_asset_account_id = categ.account_asset_id

    @api.onchange(
        "category_id",
    )
    def onchange_journal_id(self):
        self.journal_id = False
        if self.category_id:
            categ = self.category_id
            self.journal_id = categ.fixed_asset_in_progress_journal_id
