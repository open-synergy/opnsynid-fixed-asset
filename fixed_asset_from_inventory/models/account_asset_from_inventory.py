# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class AccountAssetFromInventory(models.Model):
    _name = "account.asset_from_inventory"
    _description = "Fixed Asset From Inventory"
    _inherit = [
        "mail.thread",
        "tier.validation",
        "base.sequence_document",
        "base.workflow_policy_object",
        "base.cancel.reason_common",
        "base.terminate.reason_common",
    ]
    _state_from = ["draft", "confirm"]
    _state_to = ["done"]

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    @api.depends(
        "type_id",
    )
    def _compute_policy(self):
        _super = super(AccountAssetFromInventory, self)
        _super._compute_policy()

    name = fields.Char(
        string="# Document",
        default="/",
        required=True,
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
        required=True,
        default=lambda self: self._default_company_id(),
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="account.asset_from_inventory_type",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_conversion = fields.Date(
        string="Date Conversion",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    allowed_product_categ_ids = fields.Many2many(
        string="Allowed Product Categories",
        comodel_name="product.category",
        related="type_id.allowed_product_categ_ids",
    )
    allowed_product_ids = fields.Many2many(
        string="Allowed Products",
        comodel_name="product.product",
        related="type_id.allowed_product_ids",
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    lot_id = fields.Many2one(
        string="Lot",
        comodel_name="stock.production.lot",
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
    asset_account_id = fields.Many2one(
        string="Fixed Asset Account",
        comodel_name="account.account",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    inventory_account_id = fields.Many2one(
        string="Inventory Asset Account",
        comodel_name="account.account",
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
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        copy=False,
        default="draft",
        required=True,
        readonly=True,
    )
    # Log Fields
    confirm_date = fields.Datetime(
        string="Confirm Date",
        readonly=True,
        copy=False,
    )
    confirm_user_id = fields.Many2one(
        string="Confirmed By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    done_date = fields.Datetime(
        string="Finish Date",
        readonly=True,
        copy=False,
    )
    done_user_id = fields.Many2one(
        string="Finished By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    cancel_date = fields.Datetime(
        string="Cancel Date",
        readonly=True,
        copy=False,
    )
    cancel_user_id = fields.Many2one(
        string="Cancelled By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )

    # Policy Field
    confirm_ok = fields.Boolean(
        string="Can Confirm",
        compute="_compute_policy",
    )
    restart_approval_ok = fields.Boolean(
        string="Can Restart Approval",
        compute="_compute_policy",
    )
    cancel_ok = fields.Boolean(
        string="Can Cancel",
        compute="_compute_policy",
    )
    restart_ok = fields.Boolean(
        string="Can Restart",
        compute="_compute_policy",
    )
    terminate_ok = fields.Boolean(
        string="Can Terminate",
        compute="_compute_policy",
    )

    @api.multi
    def action_confirm(self):
        for document in self:
            document.write(document._prepare_confirm_data())
            document.request_validation()

    @api.multi
    def action_done(self):
        for document in self:
            document.write(document._prepare_done_data())
            document._create_fixed_asset()

    @api.multi
    def action_cancel(self):
        for document in self:
            document.write(document._prepare_cancel_data())
            document.restart_validation()

    @api.multi
    def action_restart(self):
        for document in self:
            document.write(document._prepare_restart_data())

    @api.multi
    def _prepare_confirm_data(self):
        self.ensure_one()
        return {
            "state": "confirm",
            "confirm_date": fields.Datetime.now(),
            "confirm_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_done_data(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        ctx.update(
            {
                "ir_sequence_date": self.date_conversion,
            }
        )
        sequence = self.with_context(ctx)._create_sequence()
        return {
            "state": "done",
            "name": sequence,
        }

    @api.multi
    def _prepare_terminate_data(self):
        self.ensure_one()
        return {
            "state": "terminate",
            "terminate_date": fields.Datetime.now(),
            "terminate_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        return {
            "state": "cancel",
            "cancel_date": fields.Datetime.now(),
            "cancel_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_restart_data(self):
        self.ensure_one()
        return {
            "state": "draft",
            "confirm_date": False,
            "confirm_user_id": False,
            "approve_date": False,
            "approve_user_id": False,
            "done_date": False,
            "done_user_id": False,
            "cancel_date": False,
            "cancel_user_id": False,
            "terminate_date": False,
            "terminate_user_id": False,
            "cancel_reason_id": False,
            "terminate_reason_id": False,
        }

    @api.multi
    def _create_fixed_asset(self):
        self.ensure_one()
        quant = self.lot_id.quant_ids[0]
        quant._create_fixed_asset()

    @api.onchange(
        "type_id",
    )
    def onchange_product_id(self):
        self.product_id = False

    @api.onchange(
        "type_id",
    )
    def onchange_lot_id(self):
        self.lot_id = False

    @api.onchange(
        "type_id",
    )
    def onchange_journal_id(self):
        self.journal_id = False
        if self.type_id:
            self.journal_id = self.type_id.journal_id

    @api.onchange(
        "product_id",
    )
    def onchange_asset_account_id(self):
        self.asset_account_id = False
        if self.product_id and self.product_id.asset_category_id:
            self.asset_account_id = self.product_id.asset_category_id.account_asset_id

    @api.onchange(
        "product_id",
    )
    def onchange_inventory_account_id(self):
        self.inventory_account_id = False
        if self.product_id:
            self.inventory_account_id = self.product_id.categ_id.property_stock_valuation_account_id



    @api.multi
    def unlink(self):
        strWarning1 = _("You can only delete data on draft state")
        strWarning2 = _("You can not delete data with document number")
        for document in self:
            if document.state != "draft":
                if not self.env.context.get("force_unlink", False):
                    raise UserError(strWarning1)
            if document.name != "/":
                if not self.env.context.get("force_unlink", False):
                    raise UserError(strWarning2)
        _super = super(AccountAssetFromInventory, self)
        _super.unlink()

    @api.multi
    def validate_tier(self):
        _super = super(AccountAssetFromInventory, self)
        _super.validate_tier()
        for document in self:
            if document.validated:
                document.action_done()

    @api.multi
    def restart_validation(self):
        _super = super(AccountAssetFromInventory, self)
        _super.restart_validation()
        for document in self:
            document.request_validation()

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.name == "/":
                name = "*" + str(record.id)
            else:
                name = record.name
            result.append((record.id, name))
        return result
