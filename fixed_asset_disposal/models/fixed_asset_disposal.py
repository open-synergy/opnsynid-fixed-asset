# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class FixedAssetDisposal(models.Model):
    _name = "fixed.asset.disposal"
    _description = "Fixed Asset Disposal"
    _inherit = [
        "mail.thread",
        "mixin.sequence",
        "mixin.policy",
        "mixin.multiple_approval",
        "mixin.state_change_history",
    ]
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    @api.model
    def _default_currency_id(self):
        return self.env.user.company_id.currency_id.id

    @api.model
    def _default_date_disposition(self):
        return fields.Datetime.now()

    @api.model
    def _default_type_id(self):
        return False

    @api.multi
    @api.depends(
        "company_id",
    )
    def _compute_policy(self):
        _super = super(FixedAssetDisposal, self)
        _super._compute_policy()

    @api.multi
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

    name = fields.Char(
        string="# Document",
        required=True,
        readonly=True,
        default="/",
        states={
            "draft": [
                ("readonly", False),
            ],
        },
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
        string="Disposition Date",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        default=lambda self: self._default_date_disposition(),
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        default=lambda self: self._default_company_id(),
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
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
        comodel_name="fixed.asset.disposal_type",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        default=lambda self: self._default_type_id(),
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True,
        default=lambda self: self._default_currency_id(),
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    disposition_price = fields.Float(
        string="Disposition Price",
        required=True,
        default=0.0,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    acquisition_price = fields.Float(
        string="Acquisition Price",
        required=True,
        readonly=True,
    )
    depreciated_amount = fields.Float(
        string="Depreciated Value",
        required=False,
        readonly=True,
    )
    gain_loss_amount = fields.Float(
        string="Gain/Loss Amount",
        compute="_compute_gain_loss",
        store=True,
    )
    exchange_acc_move_id = fields.Many2one(
        string="Exchange Account Move",
        comodel_name="account.move",
        readonly=True,
    )
    disposal_acc_move_id = fields.Many2one(
        string="Disposal Account Move",
        comodel_name="account.move",
        readonly=True,
    )
    gain_acc_move_id = fields.Many2one(
        string="Gain/Loss Account Move",
        comodel_name="account.move",
        readonly=True,
    )
    exchange_acc_move_creation = fields.Selection(
        string="Exchange Acc. Move Creation",
        selection=[
            ("automatic", "Automatic"),
            ("manual", "Manual Selection"),
            ("workflow", "Workflow"),
        ],
        default="automatic",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    disposal_acc_move_creation = fields.Selection(
        string="Disposal Acc. Move Creation",
        selection=[
            ("automatic", "Automatic"),
            ("manual", "Manual Selection"),
            ("workflow", "Workflow"),
        ],
        default="automatic",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    gain_acc_move_creation = fields.Selection(
        string="Gain/Loss Acc. Move Creation",
        selection=[
            ("automatic", "Automatic"),
            ("manual", "Manual Selection"),
            ("workflow", "Workflow"),
        ],
        default="automatic",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
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
    note = fields.Text(
        string="Note",
    )
    state = fields.Selection(
        string="State",
        required=True,
        readonly=True,
        track_visibility="onchange",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("open", "On Progress"),
            ("valid", "Valid"),
            ("cancel", "Cancel"),
            ("reject", "Rejected"),
        ],
        default="draft",
        copy=False,
    )
    confirm_ok = fields.Boolean(
        string="Can Confirm",
        compute="_compute_policy",
        store=False,
        readonly=True,
    )
    approve_ok = fields.Boolean(
        string="Can Approve",
        compute="_compute_policy",
        store=False,
    )
    reject_ok = fields.Boolean(
        string="Can Reject",
        compute="_compute_policy",
        store=False,
    )
    valid_ok = fields.Boolean(
        string="Can Validate",
        compute="_compute_policy",
        store=False,
        readonly=True,
    )
    cancel_ok = fields.Boolean(
        string="Can Cancel",
        compute="_compute_policy",
        store=False,
        readonly=True,
    )
    restart_ok = fields.Boolean(
        string="Can Restart",
        compute="_compute_policy",
        store=False,
        readonly=True,
    )
    restart_validation_ok = fields.Boolean(
        string="Can Restart Validation",
        compute="_compute_policy",
    )

    @api.multi
    def action_approve_approval(self):
        _super = super(FixedAssetDisposal, self)
        _super.action_approve_approval()
        for document in self:
            if document.approved:
                document.action_open()

    @api.multi
    def restart_validation(self):
        _super = super(FixedAssetDisposal, self)
        _super.restart_validation()
        for document in self:
            document.action_request_approval()

    @api.multi
    def action_confirm(self):
        for document in self:
            document.write(self._prepare_confirm_data())
            document.action_request_approval()

    @api.multi
    def action_open(self):
        for document in self:
            document.write(self._prepare_open_data())

    @api.multi
    def action_valid(self):
        for document in self:
            document.write(self._prepare_valid_data())
            document._unlink_residual_depreciation()
            document.asset_id.write(
                {
                    "state": "removed",
                }
            )

    @api.multi
    def action_cancel(self):
        for document in self:
            disposal_acc_move = self.disposal_acc_move_id
            if document.depreciation_line_id:
                document.depreciation_line_id.unlink_move()
                document.depreciation_line_id.unlink()
            document.write(self._prepare_cancel_data())
            document.asset_id.compute_depreciation_board()
            if disposal_acc_move:
                disposal_acc_move.unlink()
            document.asset_id.write(
                {
                    "state": "open",
                }
            )

            document.restart_validation()

    @api.multi
    def action_restart(self):
        for document in self:
            document.write(self._prepare_restart_data())

    @api.multi
    def _prepare_confirm_data(self):
        self.ensure_one()
        result = {
            "state": "confirm",
        }
        return result

    @api.multi
    def _prepare_open_data(self):
        self.ensure_one()
        result = {
            "state": "open",
        }
        return result

    @api.multi
    def _prepare_valid_data(self):
        self.ensure_one()
        disposal_acc_move = False
        if self.generate_accounting_entry:
            disposal_acc_move = self._create_disposal_acc_move()
        depreciation_line = self._create_depreciation_line()
        result = {
            "state": "valid",
            "disposal_acc_move_id": disposal_acc_move and disposal_acc_move.id or False,
            "depreciation_line_id": depreciation_line.id,
        }
        return result

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        result = {
            "state": "cancel",
            "disposal_acc_move_id": False,
            "depreciation_line_id": False,
        }
        return result

    @api.multi
    def _prepare_restart_data(self):
        self.ensure_one()
        result = {
            "state": "draft",
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

    @api.model
    def create(self, values):
        _super = super(FixedAssetDisposal, self)
        result = _super.create(values)
        sequence = result._create_sequence()
        result.write(
            {
                "name": sequence,
            }
        )
        if not result.policy_template_id:
            result.onchange_policy_template_id()
        return result

    @api.multi
    def _prepare_acc_move(self, journal, move_lines):
        self.ensure_one()
        return {
            "name": self.name,
            "date": self.date_disposition,
            "journal_id": journal.id,
            "line_id": move_lines,
        }

    @api.multi
    def _prepare_disposal_acc_move(self):
        self.ensure_one()
        journal = self.disposal_journal_id
        move_lines = (
            self._prepare_disposal_accum_depr_move_line()
            + self._prepare_disposal_asset_move_line()
            + self._prepare_disposal_exchange_move_line()
            + self._prepare_disposal_gain_loss_move_line()
        )
        return self._prepare_acc_move(journal, move_lines)

    @api.multi
    def _prepare_disposal_accum_depr_move_line(self):
        self.ensure_one()
        description = "%s fixed asset disposal" % (self.asset_id.code)
        return self._prepare_exchange_move_line(
            description=_(description),
            account=self.accumulated_depreciation_account_id.id,
            debit=self.depreciated_amount,
            credit=0.0,
        )

    @api.multi
    def _prepare_disposal_asset_move_line(self):
        self.ensure_one()
        description = "%s asset disposal" % (self.asset_id.code)
        return self._prepare_exchange_move_line(
            description=_(description),
            account=self.asset_account_id.id,
            credit=self.acquisition_price,
            debit=0.0,
        )

    @api.multi
    def _prepare_disposal_exchange_move_line(self):
        self.ensure_one()
        description = "%s asset disposal" % (self.asset_id.code)
        return self._prepare_exchange_move_line(
            description=_(description),
            account=self.exchange_account_id.id,
            credit=0.0,
            debit=self.disposition_price,
        )

    @api.multi
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

    @api.multi
    def _create_disposal_acc_move(self):
        self.ensure_one()
        return self.env["account.move"].create(self._prepare_disposal_acc_move())

    @api.multi
    def _prepare_depreciation_line(self):
        self.ensure_one()
        subtype_id = self.env.ref("fixed_asset_disposal." "depr_line_subtype_disposal")
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

    @api.multi
    def _create_depreciation_line(self):
        self.ensure_one()
        obj_line = self.env["fixed.asset.depreciation.line"]
        asset_value = obj_line.create(self._prepare_depreciation_line())
        return asset_value

    @api.multi
    def _unlink_residual_depreciation(self):
        self.ensure_one()
        obj_line = self.env["fixed.asset.depreciation.line"]
        criteria = [
            ("asset_id", "=", self.asset_id.id),
            ("line_date", ">", self.date_disposition),
        ]
        obj_line.search(criteria).unlink()
