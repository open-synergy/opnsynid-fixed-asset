# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FixedAssetDisposal(models.Model):
    _name = "fixed_asset.disposal"
    _description = "Fixed Asset Disposal"
    _inherit = [
        "mixin.transaction_confirm",
        "mixin.transaction_open",
        "mixin.transaction_done",
        "mixin.transaction_cancel",
        "mixin.print_document",
        "mixin.company_currency",
    ]
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
    ]

    # Sequence attribute
    _create_sequence_state = "open"

    @api.model
    def _default_date_disposition(self):
        return fields.Datetime.now()

    @api.depends(
        "acquisition_price",
        "disposition_price",
        "depreciated_amount",
    )
    def _compute_gain_loss(self):
        for document in self:
            document.gain_loss_amount = (
                document.disposition_price
                - document.acquisition_price
                + document.depreciated_amount
            )

    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_disposition = fields.Date(
        string="Disposal Date",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        default=lambda self: self._default_date_disposition(),
    )
    asset_id = fields.Many2one(
        string="Asset",
        comodel_name="fixed.asset.asset",
        required=True,
        domain=[("type", "=", "normal"), ("state", "=", "open")],
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="fixed_asset.disposal_type",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    disposition_price = fields.Monetary(
        string="Disposal Price",
        required=True,
        default=0.0,
        readonly=True,
        currency_field="company_currency_id",
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    acquisition_price = fields.Monetary(
        string="Acquisition Price",
        currency_field="company_currency_id",
        required=True,
        readonly=True,
    )
    depreciated_amount = fields.Monetary(
        string="Depreciated Value",
        currency_field="company_currency_id",
        required=False,
        readonly=True,
    )
    gain_loss_amount = fields.Monetary(
        string="Gain/Loss Amount",
        currency_field="company_currency_id",
        compute="_compute_gain_loss",
        store=True,
    )
    disposal_acc_move_id = fields.Many2one(
        string="Disposal Account Move",
        comodel_name="account.move",
        readonly=True,
    )
    disposal_journal_id = fields.Many2one(
        string="Disposal Journal",
        comodel_name="account.journal",
        readonly=True,
        required=True,
        states={
            "draft": [("readonly", False)],
        },
    )
    asset_account_id = fields.Many2one(
        string="Asset Account",
        comodel_name="account.account",
        ondelete="restrict",
        readonly=True,
        required=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    exchange_account_id = fields.Many2one(
        string="Exchange Account",
        comodel_name="account.account",
        ondelete="restrict",
        readonly=True,
        required=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    gain_account_id = fields.Many2one(
        string="Gain Account",
        comodel_name="account.account",
        ondelete="restrict",
        readonly=True,
        required=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    loss_account_id = fields.Many2one(
        string="Loss Account",
        comodel_name="account.account",
        ondelete="restrict",
        readonly=True,
        required=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    accumulated_depreciation_account_id = fields.Many2one(
        string="Accumulated Depreciation Account",
        comodel_name="account.account",
        ondelete="restrict",
        readonly=True,
        required=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    depreciation_line_id = fields.Many2one(
        string="Depreciation Line",
        comodel_name="fixed.asset.depreciation.line",
        readonly=True,
    )
    generate_accounting_entry = fields.Boolean(
        string="Generate Accounting Entry",
        default=True,
    )
    state = fields.Selection(
        string="State",
        required=True,
        readonly=True,
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("open", "On Progress"),
            ("done", "Done"),
            ("cancel", "Cancel"),
            ("reject", "Rejected"),
        ],
        default="draft",
        copy=False,
    )

    def action_done(self):
        _super = super(FixedAssetDisposal, self)
        _super.action_done()
        for document in self.sudo():
            document._unlink_residual_depreciation()
            document.asset_id.write(
                {
                    "state": "removed",
                }
            )

    def action_cancel(self, cancel_reason=False):
        _super = super(FixedAssetDisposal, self)
        _super.action_cancel(cancel_reason=cancel_reason)
        for document in self.sudo():
            disposal_acc_move = document.disposal_acc_move_id
            if document.depreciation_line_id:
                document.depreciation_line_id.unlink_move()
                document.depreciation_line_id.unlink()
            document.write(self._prepare_cancel_additional_data())
            document.asset_id.compute_depreciation_board()
            if disposal_acc_move:
                disposal_acc_move.with_context(force_delete=True).unlink()
            document.asset_id.write(
                {
                    "state": "open",
                }
            )

    def _prepare_done_data(self):
        self.ensure_one()
        _super = super(FixedAssetDisposal, self)
        result = _super._prepare_done_data()
        disposal_acc_move = False
        if self.generate_accounting_entry:
            disposal_acc_move = self._create_disposal_acc_move()
        depreciation_line = self._create_depreciation_line()
        result.update(
            {
                "disposal_acc_move_id": disposal_acc_move
                and disposal_acc_move.id
                or False,
                "depreciation_line_id": depreciation_line.id,
            }
        )
        return result

    def _prepare_cancel_additional_data(self):
        self.ensure_one()
        result = {
            "disposal_acc_move_id": False,
            "depreciation_line_id": False,
        }
        return result

    @api.onchange("asset_id")
    def onchange_acquisition_price(self):
        self.acquisition_price = 0.0
        if self.asset_id:
            self.acquisition_price = self.asset_id.purchase_value

    @api.onchange("asset_id")
    def onchange_depreciated_amount(self):
        self.depreciated_amount = 0.0
        if self.asset_id:
            self.depreciated_amount = self.asset_id.value_depreciated

    @api.onchange("asset_id", "type_id")
    def onchange_asset_account(self):
        self.asset_account_id = False
        if self.asset_id:
            self.asset_account_id = self.asset_id.category_id.account_asset_id

    @api.onchange("asset_id", "type_id")
    def onchange_exchange_account(self):
        self.exchange_account_id = False
        if self.type_id:
            self.exchange_account_id = self.type_id.exchange_account_id

    @api.onchange("asset_id", "type_id")
    def onchange_accumulated_depreciation_account(self):
        self.accumulated_depreciation_account_id = False
        if self.asset_id:
            self.accumulated_depreciation_account_id = (
                self.asset_id.category_id.account_depreciation_id
            )

    @api.onchange("asset_id", "type_id")
    def onchange_gain_account(self):
        self.gain_account_id = False
        if self.type_id and self.type_id.gain_account_id:
            self.gain_account_id = self.type_id.gain_account_id

    @api.onchange("asset_id", "type_id")
    def onchange_loss_account(self):
        self.loss_account_id = False
        if self.type_id and self.type_id.loss_account_id:
            self.loss_account_id = self.type_id.loss_account_id

    @api.onchange("asset_id", "type_id")
    def onchange_disposal_journal_id(self):
        self.disposal_journal_id = False
        if self.type_id:
            self.disposal_journal_id = self.type_id.disposal_journal_id

    @api.onchange(
        "type_id",
    )
    def onchange_policy_template_id(self):
        template_id = self._get_template_policy()
        self.policy_template_id = template_id

    def _prepare_acc_move(self, journal, move_lines):
        self.ensure_one()
        return {
            "name": self.name,
            "date": self.date_disposition,
            "journal_id": journal.id,
            "line_ids": move_lines,
        }

    def _prepare_disposal_acc_move(self):
        self.ensure_one()
        journal = self.disposal_journal_id
        move_lines = (
            self._prepare_disposal_accum_depr_move_line()
            + self._prepare_disposal_asset_move_line()
            + self._prepare_disposal_gain_loss_move_line()
        )
        if self.disposition_price > 0.0:
            move_lines += self._prepare_disposal_exchange_move_line()
        return self._prepare_acc_move(journal, move_lines)

    def _prepare_disposal_accum_depr_move_line(self):
        self.ensure_one()
        description = "%s fixed asset disposal" % (self.asset_id.code)
        return self._prepare_exchange_move_line(
            description=_(description),
            account=self.accumulated_depreciation_account_id.id,
            debit=self.depreciated_amount,
            credit=0.0,
        )

    def _prepare_disposal_asset_move_line(self):
        self.ensure_one()
        description = "%s asset disposal" % (self.asset_id.code)
        return self._prepare_exchange_move_line(
            description=_(description),
            account=self.asset_account_id.id,
            credit=self.acquisition_price,
            debit=0.0,
        )

    def _prepare_disposal_exchange_move_line(self):
        self.ensure_one()
        description = "%s asset disposal" % (self.asset_id.code)
        return self._prepare_exchange_move_line(
            description=_(description),
            account=self.exchange_account_id.id,
            credit=0.0,
            debit=self.disposition_price,
        )

    def _prepare_exchange_move_line(self, description, account, debit, credit):
        self.ensure_one()
        return [
            (
                0,
                0,
                {
                    "name": description,
                    "account_id": account,
                    "debit": debit,
                    "credit": credit,
                    "analytic_account_id": False,
                },
            )
        ]

    def _prepare_disposal_gain_loss_move_line(self):
        self.ensure_one()
        gain = self.gain_loss_amount >= 0.0 and abs(self.gain_loss_amount) or 0.0
        loss = self.gain_loss_amount < 0.0 and abs(self.gain_loss_amount) or 0.0
        description = "%s asset disposal" % (self.asset_id.code)
        return self._prepare_exchange_move_line(
            description=_(description),
            account=self._get_gain_account().id,
            credit=gain,
            debit=loss,
        )

    def _get_gain_account(self):
        self.ensure_one()
        if self.gain_loss_amount < 0.0:
            return self.loss_account_id
        else:
            return self.gain_account_id

    def _create_disposal_acc_move(self):
        self.ensure_one()
        move = self.env["account.move"].create(self._prepare_disposal_acc_move())
        move.action_post()
        return move

    def _prepare_depreciation_line(self):
        self.ensure_one()
        subtype_id = self.env.ref(
            "ssi_fixed_asset_disposal." "depr_line_subtype_disposal"
        )
        amount = self.acquisition_price - self.depreciated_amount
        return {
            "name": "Disposal",
            "previous_id": self.asset_id.last_posted_depreciation_line_id.id,
            "subtype_id": subtype_id.id,
            "type": "remove",
            "line_date": self.date_disposition,
            "amount": amount,
            "init_entry": True,
            "asset_id": self.asset_id.id,
        }

    def _create_depreciation_line(self):
        self.ensure_one()
        obj_line = self.env["fixed.asset.depreciation.line"]
        asset_value = obj_line.create(self._prepare_depreciation_line())
        return asset_value

    def _unlink_residual_depreciation(self):
        self.ensure_one()
        obj_line = self.env["fixed.asset.depreciation.line"]
        criteria = [
            ("asset_id", "=", self.asset_id.id),
            ("line_date", ">", self.date_disposition),
        ]
        obj_line.search(criteria).unlink()

    @api.constrains('disposition_price')
    def _disposition_price_validity(self):
        for rec in self.sudo():
            if rec.disposition_price < 0:
                raise ValidationError(_('Disposal price can not negative.'))

