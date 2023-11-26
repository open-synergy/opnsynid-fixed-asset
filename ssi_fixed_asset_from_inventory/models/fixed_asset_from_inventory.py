# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class FixedAssetFromInventory(models.Model):
    _name = "fixed_asset_from_inventory"
    _inherit = [
        "mixin.transaction_confirm",
        "mixin.transaction_done",
        "mixin.transaction_cancel",
        "mixin.company_currency",
        "mixin.account_move",
        "mixin.account_move_double_line",
    ]
    _description = "Fixed Asset From Inventory"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True

    # Attributes related to add element on form view automatically
    _automatically_insert_multiple_approval_page = True
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False

    _statusbar_visible_label = "draft,confirm,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "terminate_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
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
        "dom_terminate",
    ]

    # Sequence attribute
    _create_sequence_state = "done"

    _journal_id_field_name = "journal_id"
    _move_id_field_name = "move_id"
    _accounting_date_field_name = "date"
    _currency_id_field_name = "company_currency_id"
    _company_currency_id_field_name = "company_currency_id"
    _number_field_name = "name"

    # Debit ML Attribute
    _debit_account_id_field_name = "fixed_asset_account_id"
    _debit_partner_id_field_name = False
    _debit_analytic_account_id_field_name = False
    _debit_label_field_name = "name"
    _debit_product_id_field_name = "product_id"
    _debit_uom_id_field_name = "uom_id"
    _debit_quantity_field_name = "quantity"
    _debit_price_unit_field_name = "amount"
    _debit_currency_id_field_name = "company_currency_id"
    _debit_company_currency_id_field_name = "company_currency_id"
    _debit_amount_currency_field_name = "amount"
    _debit_company_id_field_name = "company_id"
    _debit_date_field_name = "date"
    _debit_need_date_due = False
    _debit_date_due_field_name = False

    # Credit ML Attribute
    _credit_account_id_field_name = "inventory_account_id"
    _credit_partner_id_field_name = False
    _credit_analytic_account_id_field_name = False
    _credit_label_field_name = "name"
    _credit_product_id_field_name = "product_id"
    _credit_uom_id_field_name = "uom_id"
    _credit_quantity_field_name = "quantity"
    _credit_price_unit_field_name = "amount"
    _credit_currency_id_field_name = "company_currency_id"
    _credit_company_currency_id_field_name = "company_currency_id"
    _credit_amount_currency_field_name = "amount"
    _credit_company_id_field_name = "company_id"
    _credit_date_field_name = "date"
    _credit_need_date_due = False
    _credit_date_due_field_name = False

    date = fields.Date(
        string="Date",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        default=lambda self: self._default_date(),
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="fixed_asset_from_inventory_type",
        required=True,
        copy=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        required=True,
        copy=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    uom_id = fields.Many2one(
        related="product_id.uom_id",
    )
    quantity = fields.Float(
        string="Quantity",
        required=True,
        default=1.0,
    )
    allowed_lot_ids = fields.Many2many(
        string="Allowed Serisl Numbers",
        comodel_name="stock.production.lot",
        compute="_compute_allowed_lot_ids",
        store=False,
    )
    lot_id = fields.Many2one(
        string="# Serial Number",
        comodel_name="stock.production.lot",
        required=True,
        copy=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    amount = fields.Monetary(
        string="Amount",
        currency_field="company_currency_id",
        readonly=True,
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        copy=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    inventory_account_id = fields.Many2one(
        string="Inventory Account",
        comodel_name="account.account",
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
    debit_move_line_id = fields.Many2one(
        string="Debit Journal Item",
        comodel_name="account.move.line",
        copy=False,
        readonly=True,
        ondelete="restrict",
    )
    credit_move_line_id = fields.Many2one(
        string="Credit Journal Item",
        comodel_name="account.move.line",
        copy=False,
        readonly=True,
        ondelete="restrict",
    )
    move_id = fields.Many2one(
        string="Accounting Entry",
        comodel_name="account.move",
        copy=False,
        readonly=True,
        ondelete="restrict",
    )
    fixed_asset_id = fields.Many2one(
        string="# Fixed Asset",
        comodel_name="fixed.asset.asset",
        compute="_compute_fixed_asset_id",
        store=True,
    )

    @api.model
    def _default_date(self):
        return fields.Date.today()

    @api.depends(
        "debit_move_line_id",
    )
    def _compute_fixed_asset_id(self):
        for record in self:
            result = False
            if record.debit_move_line_id and record.debit_move_line_id.fixed_asset_ids:
                result = record.debit_move_line_id.fixed_asset_ids[0]
            record.fixed_asset_id = result

    @api.depends(
        "product_id",
        "company_id",
    )
    def _compute_allowed_lot_ids(self):
        Quant = self.env["stock.quant"]
        for record in self:
            record.allowed_lot_ids = []
            if record.company_id and record.product_id:
                criteria = [
                    ("company_id", "=", record.company_id.id),
                    ("product_id", "=", record.product_id.id),
                    ("location_id.usage", "=", "internal"),
                    ("lot_id.fixed_asset_id", "=", False),
                ]
                record.allowed_lot_ids = Quant.search(criteria).mapped("lot_id")

    @api.onchange(
        "company_id",
        "product_id",
    )
    def onchange_lot_id(self):
        self.lot_id = False

    @api.onchange("lot_id")
    def onchange_amount(self):
        self.amount = 0.0
        Quant = self.env["stock.quant"]
        if self.lot_id:
            criteria = [
                ("company_id", "=", self.company_id.id),
                ("product_id", "=", self.product_id.id),
                ("lot_id", "=", self.lot_id.id),
                ("location_id.usage", "=", "internal"),
            ]
            quants = Quant.search(criteria)
            if len(quants) > 0:
                self.amount = quants[0].value

    @api.onchange(
        "type_id",
    )
    def onchange_journal_id(self):
        self.journal_id = False
        if self.type_id:
            self.journal_id = self.type_id.journal_id

    @api.onchange(
        "product_id",
        "type_id",
    )
    def onchange_fixed_asset_account_id(self):
        self.fixed_asset_account_id = False
        if self.product_id and self.type_id:
            self.fixed_asset_account_id = self.product_id._get_product_account(
                usage_code=self.type_id.fixed_asset_usage_id.code
            )

    @api.onchange(
        "product_id",
        "type_id",
    )
    def onchange_inventory_account_id(self):
        self.inventory_account_id = False
        if self.product_id and self.type_id:
            self.inventory_account_id = self.product_id._get_product_account(
                usage_code=self.type_id.inventory_usage_id.code
            )

    @api.model
    def _get_policy_field(self):
        res = super(FixedAssetFromInventory, self)._get_policy_field()
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
    def _create_accounting_entry(self):
        if self.move_id:
            return True

        self._create_standard_move()  # Mixin
        debit_ml, credit_ml = self._create_standard_ml()  # Mixin
        self.write(
            {
                "debit_move_line_id": debit_ml.id,
                "credit_move_line_id": credit_ml.id,
            }
        )
        self._post_standard_move()  # Mixin
        debit_ml.action_create_fixed_asset()
        self.lot_id.write(
            {
                "fixed_asset_id": debit_ml.fixed_asset_ids[0].id,
            }
        )

    @ssi_decorator.post_cancel_action()
    def _delete_accounting_entry(self):
        self.ensure_one()
        self.fixed_asset_id.unlink()
        self.write(
            {
                "debit_move_line_id": False,
                "credit_move_line_id": False,
            }
        )
        self._delete_standard_move()  # Mixin

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
