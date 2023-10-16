# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from odoo.addons.ssi_decorator import ssi_decorator


class FixedAssetImprovement(models.Model):
    _name = "fixed_asset_improvement"
    _description = "Fixed Asset Improvement"
    _inherit = [
        "mixin.transaction_confirm",
        "mixin.transaction_done",
        "mixin.transaction_cancel",
        "mixin.account_move",
        "mixin.account_move_double_line",
        "mixin.company_currency",
        "mixin.many2one_configurator",
    ]

    # Approval Mixin Stuff
    _approval_from_state = "draft"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Sequence Mixin Stuff
    _create_sequence_state = "done"

    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "cancel_ok",
        "restart_ok",
    ]

    _statusbar_visible_label = "draft,confirm,done"

    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # Accounting Entry Mixin Stuff
    _journal_id_field_name = "journal_id"
    _accounting_date_field_name = "date"
    _currency_id_field_name = "company_currency_id"
    _company_currency_id_field_name = "company_currency_id"
    _debit_account_field_name = "exchange_account_id"
    _credit_account_field_name = "accumulated_depreciation_account_id"
    _amount_currency_field_name = "improvement_amount"

    type_id = fields.Many2one(
        "fixed_asset_improvement_type",
        string="Type",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    allowed_asset_ids = fields.Many2many(
        "fixed.asset.asset",
        string="Allowed Assets",
        compute="_compute_allowed_asset_ids",
        store=False,
    )
    asset_id = fields.Many2one(
        "fixed.asset.asset",
        string="Asset",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    move_line_ids = fields.One2many(
        "account.move.line",
        "fixed_asset_improvement_id",
        string="Move Lines",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date = fields.Date(
        string="Date",
        compute="_compute_date",
        store=True,
    )
    improvement_amount = fields.Monetary(
        string="Improvement Amount",
        compute="_compute_amount",
        currency_field="company_currency_id",
        store=True,
    )
    # Accounting Stuff
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    exchange_account_id = fields.Many2one(
        "account.account",
        string="Exchange Account",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    accumulated_depreciation_account_id = fields.Many2one(
        "account.account",
        string="Accumulated Depreciation Account",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    move_id = fields.Many2one(
        "account.move",
        string="Move",
        readonly=True,
    )
    # Technical fields
    asset_value_history_id = fields.Many2one(
        "fixed.asset.depreciation.line",
        string="Asset Value History",
        readonly=True,
    )
    depreciation_history_id = fields.Many2one(
        "fixed.asset.depreciation.line",
        string="Depreciation History",
        readonly=True,
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
        res = super(FixedAssetImprovement, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "reject_ok",
            "cancel_ok",
            "restart_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @api.depends("type_id")
    def _compute_allowed_asset_ids(self):
        for record in self:
            result = []
            if record.type_id:
                ttype = record.type_id
                if ttype.asset_selection_method == "manual":
                    result = ttype.asset_ids.ids
                elif ttype.asset_selection_method == "domain":
                    criteria = safe_eval(ttype.asset_domain, {})
                    result = self.env["fixed.asset.asset"].search(criteria).ids
                elif ttype.asset_selection_method == "code":
                    localdict = self._get_localdict()
                    try:
                        safe_eval(ttype.asset_python_code, localdict, mode="exec", nocopy=True)
                        result = localdict["result"]
                    except Exception as error:
                        raise UserError(_("Error evaluating conditions.\n %s") % error)

            record.allowed_asset_ids = result

    def _compute_date(self):
        pass

    @api.depends("move_line_ids", "move_line_ids.debit")
    def _compute_amount(self):
        for record in self:
            amount = 0.0
            for move in record.move_line_ids:
                amount = amount + move.debit
            record.improvement_amount = amount

    @api.onchange("type_id")
    def onchange_asset_id(self):
        self.asset_id = False

    @api.onchange("type_id")
    def onchange_journal_id(self):
        self.journal_id = False
        if self.type_id:
            self.journal_id = self.type_id.journal_id

    @api.onchange("type_id")
    def onchange_exchange_account_id(self):
        self.exchange_account_id = False
        if self.type_id:
            self.exchange_account_id = self.type_id.exchange_account_id

    @api.onchange("type_id")
    def onchange_accumulated_depreciation_account_id(self):
        self.accumulated_depreciation_account_id = False
        # if self.type_id:
        #     self.accumulated_depreciation_account_id = self.type_id.accumulated_depreciation_account_id

    @ssi_decorator.post_done_action()
    def _name_accounting_entry(self):
        self.ensure_one()
        self._create_standard_move() #Mixin
        self._create_standard_debit_ml() #Mixin
        self._create_standard_credit_ml() #Mixin
        self._post_standard_move() #Mixin

    @ssi_decorator.post_cancel_action()
    def _delete_accounting_entry(self):
        self.ensure_one()
        self._delete_standard_move()
