# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class FixedAssetImpairmentCommon(models.AbstractModel):
    _name = "account.asset.impairment_common"
    _description = "Fixed Asset Impairment Common"
    _inherit = [
        "mail.thread",
        "base.sequence_document",
        "base.workflow_policy_object",
        "tier.validation",
    ]
    _state_from = ["draft", "confirm"]
    _state_to = ["open"]

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    @api.model
    def _default_type(self):
        return self._context.get("type", "impairment")

    @api.model
    def _default_date(self):
        return fields.Datetime.now()

    def _compute_depreciation(self, cr, uid, ids, name, args, context=None):
        res = {}
        for asset in self.browse(cr, uid, ids, context=context):
            res[asset.id] = {}
            child_ids = self.search(
                cr,
                uid,
                [("parent_id", "child_of", [asset.id]), ("type", "=", "normal")],
                context=context,
            )
            if child_ids:
                cr.execute(
                    "SELECT COALESCE(SUM(amount),0.0) AS amount "
                    "FROM account_asset_depreciation_line "
                    "WHERE asset_id in %s "
                    "AND type in ('depreciate','remove') "
                    "AND (init_entry=TRUE OR move_check=TRUE)",
                    (tuple(child_ids),),
                )
                value_depreciated = cr.fetchone()[0]
            else:
                value_depreciated = 0.0
            res[asset.id]["value_residual"] = asset.asset_value - value_depreciated
            res[asset.id]["value_depreciated"] = value_depreciated
        return res

    @api.multi
    @api.depends(
        "company_id",
    )
    def _compute_policy(self):
        _super = super(FixedAssetImpairmentCommon, self)
        _super._compute_policy()

    name = fields.Char(
        string="# Document",
        required=True,
        default="/",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
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
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
    )
    asset_id = fields.Many2one(
        string="Asset",
        comodel_name="account.asset.asset",
        required=True,
        domain=[
            ("type", "=", "normal"),
        ],
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date = fields.Date(
        string="Date",
        required=True,
        readonly=True,
        default=lambda self: self._default_date(),
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    period_id = fields.Many2one(
        string="Period",
        comodel_name="account.period",
        require=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    type = fields.Selection(
        string="Type",
        selection=[
            ("impairment", "Impairment"),
            ("reversal", "Reversal"),
        ],
        required=True,
        default=lambda self: self._default_type(),
    )
    impairment_amount = fields.Float(
        string="Impairment Amount",
        required=True,
        default=0.0,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    account_impairment_id = fields.Many2one(
        string="Impairment Account",
        comodel_name="account.account",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    account_contra_id = fields.Many2one(
        string="Contra-Impairment Account",
        comodel_name="account.account",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    account_move_id = fields.Many2one(
        string="# Accounting Entry",
        comodel_name="account.move",
        readonly=True,
        ondelete="restrict",
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
    confirmed_date = fields.Datetime(
        string="Confirmation Date",
        readonly=True,
        copy=False,
    )
    confirmed_user_id = fields.Many2one(
        string="Confirmation By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    opened_date = fields.Datetime(
        string="Opened Date",
        readonly=True,
        copy=False,
    )
    opened_user_id = fields.Many2one(
        string="Open By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    validated_date = fields.Datetime(
        string="Validation Date",
        readonly=True,
        copy=False,
    )
    validated_user_id = fields.Many2one(
        string="Validation By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    cancelled_date = fields.Datetime(
        string="Cancellation Date",
        readonly=True,
        copy=False,
    )
    cancelled_user_id = fields.Many2one(
        string="Cancellation By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )

    @api.multi
    def validate_tier(self):
        _super = super(FixedAssetImpairmentCommon, self)
        _super.validate_tier()
        for document in self:
            if document.validated:
                document.action_open()

    @api.multi
    def restart_validation(self):
        _super = super(FixedAssetImpairmentCommon, self)
        _super.restart_validation()
        for document in self:
            document.request_validation()

    @api.multi
    def action_confirm(self):
        for imp in self:
            imp.write(self._prepare_confirm_data())
            imp.request_validation()

    @api.multi
    def action_open(self):
        for imp in self:
            imp.write(self._prepare_open_data())

    @api.multi
    def action_valid(self):
        for imp in self:
            imp.write(self._prepare_valid_data())
            imp._create_depreciation_line()

    @api.multi
    def action_cancel(self):
        for imp in self:
            move = imp.account_move_id
            imp.write(self._prepare_cancel_data())
            move.unlink()
            imp.restart_validation()

    @api.multi
    def action_restart(self):
        for imp in self:
            imp.write(self._prepare_restart_data())

    @api.multi
    def _prepare_confirm_data(self):
        self.ensure_one()
        result = {
            "state": "confirm",
            "confirmed_user_id": self.env.user.id,
            "confirmed_date": fields.Datetime.now(),
        }
        return result

    @api.multi
    def _prepare_open_data(self):
        self.ensure_one()
        result = {
            "state": "open",
            "opened_user_id": self.env.user.id,
            "opened_date": fields.Datetime.now(),
        }
        return result

    @api.multi
    def _prepare_valid_data(self):
        self.ensure_one()
        move = self._create_account_move()
        result = {
            "state": "valid",
            "validated_user_id": self.env.user.id,
            "validated_date": fields.Datetime.now(),
            "account_move_id": move.id,
        }
        return result

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        result = {
            "state": "cancel",
            "cancelled_user_id": self.env.user.id,
            "cancelled_date": fields.Datetime.now(),
            "account_move_id": False,
        }
        return result

    @api.multi
    def _prepare_restart_data(self):
        self.ensure_one()
        result = {
            "state": "draft",
            "confirmed_user_id": False,
            "confirmed_date": False,
            "opened_user_id": False,
            "opened_date": False,
            "validated_user_id": False,
            "validated_date": False,
            "cancelled_user_id": False,
            "cancelled_date": False,
        }
        return result

    @api.model
    def create(self, values):
        _super = super(FixedAssetImpairmentCommon, self)
        result = _super.create(values)
        ctx = self.env.context.copy()
        ctx.update(
            {
                "ir_sequence_date": result.date,
            }
        )
        sequence = result.with_context(ctx)._create_sequence()
        result.write(
            {
                "name": sequence,
            }
        )
        return result

    @api.multi
    def unlink(self):
        strWarning = _("You can only delete data on draft state")
        for imp in self:
            if imp.state != "draft":
                if not self._context.get("force_unlink", False):
                    raise UserError(strWarning)
        _super = super(FixedAssetImpairmentCommon, self)
        _super.unlink()

    @api.onchange("company_id")
    def onchange_asset_id(self):
        self.asset_id = False

    @api.onchange("date")
    def onchange_period_id(self):
        self.period_id = self.env["account.period"].find(self.date).id

    @api.onchange("asset_id")
    def onchange_account_impairment_id(self):
        self.account_impairment_id = False
        if self.asset_id and self.asset_id.category_id.impairment_account_id:
            self.account_impairment_id = self.asset_id.category_id.impairment_account_id

    @api.onchange("asset_id")
    def onchange_account_contra_id(self):
        self.account_contra_id = False
        if not self.asset_id:
            return {}

        if (
            self.type == "impairment"
            and self.asset_id.category_id.impairment_expense_account_id
        ):
            self.account_contra_id = (
                self.asset_id.category_id.impairment_expense_account_id
            )
        elif (
            self.type == "reversal"
            and self.asset_id.category_id.impairment_reversal_account_id
        ):
            self.account_contra_id = (
                self.asset_id.category_id.impairment_reversal_account_id
            )

    @api.onchange("asset_id")
    def onchange_journal_id(self):
        self.journal_id = False
        if self.asset_id and self.asset_id.category_id.impairment_journal_id:
            self.journal_id = self.asset_id.category_id.impairment_journal_id

    @api.multi
    def _prepare_account_move(self):
        self.ensure_one()
        data = {
            "name": self.name,
            "ref": self.name,
            "date": self.date,
            "period_id": self.period_id.id,
            "journal_id": self.journal_id.id,
            "line_id": [
                (0, 0, self._prepare_move_impairment()),
                (0, 0, self._prepare_move_contra_impairment()),
            ],
        }
        return data

    @api.multi
    def _prepare_move_impairment(self):
        self.ensure_one()
        debit, credit = self._get_debit_credit_impairment()
        data = {
            "name": self.name,
            "debit": debit,
            "credit": credit,
            "account_id": self.account_impairment_id.id,
        }
        return data

    @api.multi
    def _prepare_move_contra_impairment(self):
        self.ensure_one()
        debit, credit = self._get_debit_credit_contra_impairment()
        data = {
            "name": self.name,
            "debit": debit,
            "credit": credit,
            "account_id": self.account_contra_id.id,
        }
        return data

    @api.multi
    def _get_debit_credit_impairment(self):
        self.ensure_one()
        debit = credit = 0.0
        if self.type == "impairment":
            debit = 0.0
            credit = self.impairment_amount
        elif self.type == "reversal":
            credit = 0.0
            debit = self.impairment_amount
        return debit, credit

    @api.multi
    def _get_debit_credit_contra_impairment(self):
        self.ensure_one()
        debit = credit = 0.0
        if self.type == "impairment":
            credit = 0.0
            debit = self.impairment_amount
        elif self.type == "reversal":
            debit = 0.0
            credit = self.impairment_amount
        return debit, credit

    @api.multi
    def _create_account_move(self):
        self.ensure_one()
        return self.env["account.move"].create(self._prepare_account_move())

    @api.multi
    def _prepare_depreciation_line(self):
        self.ensure_one()
        obj_dl = self.env["account.asset.depreciation.line"]
        criteria = [
            ("asset_id", "=", self.asset_id.id),
        ]
        dls = obj_dl.search(criteria, limit=1, order="line_date desc")
        if len(dls) == 1:
            dl = dls[0]
        return {
            "name": self.name,
            "asset_id": self.asset_id.id,
            "previous_id": dl and dl.id or False,
            "amount": self.impairment_amount,
            "line_date": self.date,
            "type": "depreciate",
            "init_entry": True,
        }

    @api.multi
    def _create_depreciation_line(self):
        self.ensure_one()
        self.asset_id.compute_depreciation_board()

    @api.constrains("impairment_amount")
    def _check_impairment_amount(self):
        if self.impairment_amount <= 0.0:
            raise UserError(_("No zero or negative value"))

    @api.constrains("date")
    def _check_asset_purchase_value(self):
        if self.date <= self.asset_id.date_start:
            raise UserError(_("Can not impair asset before purchase date"))

    @api.constrains("state")
    def _check_depreciation_board(self):
        warning_msg = _("No impairment before last depreciation date")
        if self.state == "confirm":
            obj_dl = self.env["account.asset.depreciation.line"]
            criteria = [
                ("asset_id", "=", self.asset_id.id),
                ("move_check", "=", True),
            ]
            dls = obj_dl.search(criteria, limit=1, order="line_date desc")
            if len(dls) == 1:
                if dls.line_date >= self.date:
                    raise UserError(warning_msg)
