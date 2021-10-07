# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class ComplexAssetMovementCommon(models.AbstractModel):
    _name = "account.complex_asset_movement_common"
    _description = "Common Object For Complex Fixed Asset Movement"
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
    def _default_date(self):
        return fields.Datetime.now()

    @api.model
    def _default_movement_type(self):
        return "add"

    @api.multi
    @api.depends(
        "company_id",
    )
    def _compute_policy(self):
        _super = super(ComplexAssetMovementCommon, self)
        _super._compute_policy()

    name = fields.Char(
        string="# Document",
        required=True,
        default="/",
        copy=False,
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
    date = fields.Date(
        string="Date",
        default=lambda self: self._default_date(),
        required=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    asset_id = fields.Many2one(
        string="Asset",
        comodel_name="account.asset.asset",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    parent_asset_id = fields.Many2one(
        string="Parent Asset",
        comodel_name="account.asset.asset",
        domain=[
            ("type", "=", "view"),
        ],
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    movement_type = fields.Selection(
        string="Movement Type",
        selection=[
            ("add", "Add Asset to Parent Asset"),
            ("remove", "Remove Asset From Parent Asset"),
        ],
        default=lambda self: self._default_movement_type(),
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
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
        _super = super(ComplexAssetMovementCommon, self)
        _super.validate_tier()
        for document in self:
            if document.validated:
                document.action_open()

    @api.multi
    def restart_validation(self):
        _super = super(ComplexAssetMovementCommon, self)
        _super.restart_validation()
        for document in self:
            document.request_validation()

    @api.multi
    def action_confirm(self):
        for rec in self:
            rec.write(self._prepare_confirm_data())
            rec.request_validation()

    @api.multi
    def action_open(self):
        for rec in self:
            rec.write(self._prepare_open_data())

    @api.multi
    def action_valid(self):
        for rec in self:
            rec.write(self._prepare_valid_data())

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.write(self._prepare_cancel_data())
            rec.restart_validation()

    @api.multi
    def action_restart(self):
        for rec in self:
            rec.write(self._prepare_restart_data())

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
        result = {
            "state": "valid",
            "validated_user_id": self.env.user.id,
            "validated_date": fields.Datetime.now(),
        }
        return result

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        result = {
            "state": "cancel",
            "cancelled_user_id": self.env.user.id,
            "cancelled_date": fields.Datetime.now(),
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
        _super = super(ComplexAssetMovementCommon, self)
        result = _super.create(values)
        sequence = result._create_sequence()
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
        _super = super(ComplexAssetMovementCommon, self)
        _super.unlink()
