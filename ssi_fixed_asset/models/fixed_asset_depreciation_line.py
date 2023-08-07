# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import time

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FixedAssetDepreciationLine(models.Model):
    _name = "fixed.asset.depreciation.line"
    _description = "Asset Depreciation Line"
    _order = "line_date, type"

    name = fields.Char(
        string="Depreciation Name",
        size=64,
        readonly=True,
    )
    asset_id = fields.Many2one(
        string="Asset",
        comodel_name="fixed.asset.asset",
        required=True,
        ondelete="cascade",
    )
    previous_id = fields.Many2one(
        string="Previous Depreciation Line",
        comodel_name="fixed.asset.depreciation.line",
        readonly=True,
    )
    subtype_id = fields.Many2one(
        string="Subtype",
        comodel_name="fixed.asset_depreciation_line_subtype",
        ondelete="restrict",
    )
    parent_state = fields.Selection(
        string="State of Asset",
        related="asset_id.state",
    )
    asset_value = fields.Float(
        string="Asset Value",
        related="asset_id.asset_value",
    )
    amount = fields.Float(
        string="Amount",
        required=True,
    )

    @api.depends(
        "amount",
        "previous_id",
    )
    def _compute(self):
        for line in self:
            depreciated_value = remaining_value = 0.0

            previous_remaining_value = line.amount * 2.0
            previous_depreciated_value = -1.0 * line.amount
            previous_amount = line.amount

            if line.previous_id:
                previous_depreciated_value = line.previous_id.depreciated_value
                previous_amount = line.previous_id.amount
                if line.previous_id.type == "create":
                    # previous_depreciated_value -= line.amount
                    previous_amount = 0.0
                previous_remaining_value = line.previous_id.remaining_value

            depreciated_value = previous_depreciated_value + previous_amount
            remaining_value = previous_remaining_value - line.amount

            line.depreciated_value = depreciated_value
            line.remaining_value = remaining_value

    remaining_value = fields.Float(
        string="Next Period Depreciation",
        compute=_compute,
        store=True,
    )
    depreciated_value = fields.Float(
        string="Amount Already Depreciated",
        compute=_compute,
        store=True,
    )
    line_date = fields.Date(
        string="Date",
        required=True,
    )
    move_id = fields.Many2one(
        string="Depreciation Entry",
        comodel_name="account.move",
        readonly=True,
    )

    @api.depends(
        "move_id",
    )
    def _move_check(self):
        for document in self:
            document.move_check = False
            if document.move_id:
                document.move_check = True

    move_check = fields.Boolean(
        string="Posted",
        compute=_move_check,
        store=True,
    )
    type = fields.Selection(
        string="Type",
        selection=[
            ("create", "Asset Value"),
            ("depreciate", "Depreciation"),
            ("remove", "Asset Removal"),
        ],
        readonly=True,
        default="depreciate",
    )
    init_entry = fields.Boolean(
        string="Initial Balance Entry",
        help="Set this flag for entries of previous fiscal years "
        "for which OpenERP has not generated accounting entries.",
    )

    def unlink(self):
        obj_depreciation_line = self.env["fixed.asset.depreciation.line"]

        for document in self:
            if document.type == "create":
                raise UserError(
                    _("You cannot remove an asset line " "of type 'Asset Value'."),
                )
            elif document.move_id:
                raise UserError(
                    _(
                        "You cannot delete a depreciation line with "
                        "an associated accounting entry."
                    )
                )

            previous_id = document.previous_id and document.previous_id.id or False

            criteria = [("previous_id", "=", document.id)]
            depreciation_line_id = obj_depreciation_line.search(criteria)
            if depreciation_line_id:
                depreciation_line_id.write({"previous_id": previous_id})
        _super = super(FixedAssetDepreciationLine, self)
        _super.unlink()

    @api.onchange(
        "amount",
    )
    def onchange_amount(self):
        if self.type == "depreciate":
            asset_value = self.asset_value
            depreciated_value = self.depreciated_value
            amount = self.amount
            self.remaining_value = asset_value - depreciated_value - amount

    def write(self, vals):
        for dl in self:
            if vals.keys() == ["move_id"] and not vals["move_id"]:
                # allow to remove an accounting entry via the
                # 'Delete Move' button on the depreciation lines.
                if not self.env.context.get("unlink_from_asset"):
                    raise UserError(
                        _(
                            "You are not allowed to remove an accounting entry "
                            "linked to an asset."
                            "\nYou should remove such entries from the asset."
                        )
                    )
            elif vals.keys() == ["asset_id"]:
                continue
            elif dl.move_id and not self.env.context.get("allow_asset_line_update"):
                raise UserError(
                    _(
                        "You cannot change a depreciation line "
                        "with an associated accounting entry."
                    )
                )
            elif vals.get("init_entry"):
                self.env.cr.execute(
                    "SELECT id "
                    "FROM fixed_asset_depreciation_line "
                    "WHERE asset_id = %s AND move_check = TRUE "
                    "AND type = 'depreciate' AND line_date <= %s LIMIT 1",
                    (dl.asset_id.id, dl.line_date),
                )
                res = self.env.cr.fetchone()
                if res:
                    raise UserError(
                        _(
                            "You cannot set the 'Initial Balance Entry' flag "
                            "on a depreciation line "
                            "with prior posted entries."
                        )
                    )
        return super(FixedAssetDepreciationLine, self).write(vals)

    def _setup_move_data(self, depreciation_date):
        asset = self.asset_id
        move_data = {
            "name": "/",
            "date": depreciation_date,
            "ref": self.name,
            "journal_id": asset.category_id.journal_id.id,
        }
        return move_data

    def _setup_move_line_data(
        self,
        depreciation_date,
        account_id,
        type,  # pylint: disable=W0622
        move_id,
    ):
        self.ensure_one()
        asset = self.asset_id
        amount = self.amount
        analytic_id = False
        if type == "depreciation":
            debit = amount < 0 and -amount or 0.0
            credit = amount > 0 and amount or 0.0
        elif type == "expense":
            debit = amount > 0 and amount or 0.0
            credit = amount < 0 and -amount or 0.0
            analytic_id = asset.account_analytic_id.id
        move_line_data = {
            "name": asset.name,
            "ref": self.name,
            "move_id": move_id,
            "account_id": account_id,
            "credit": credit,
            "debit": debit,
            "journal_id": asset.category_id.journal_id.id,
            "partner_id": asset.partner_id.id,
            "analytic_account_id": analytic_id,
            "date": depreciation_date,
            "fixed_asset_id": asset.id,
        }
        return move_line_data

    def create_move(self):
        self.ensure_one()
        context = self.env.context

        obj_fixed_asset = self.env["fixed.asset.asset"]
        obj_account_move = self.env["account.move"]
        obj_account_move_line = self.env["account.move.line"]

        created_move_ids = []
        asset_ids = []

        asset = self.asset_id
        if asset.method_time == "year" or asset.method_time == "month":
            depreciation_date = context.get("depreciation_date") or self.line_date
        else:
            depreciation_date = context.get("depreciation_date") or time.strftime(
                "%Y-%m-%d"
            )
        ctx = dict(self.env.context, allow_asset=True, check_move_validity=False)
        move_id = obj_account_move.create(self._setup_move_data(depreciation_date))
        depr_acc_id = asset.category_id.account_depreciation_id.id
        exp_acc_id = asset.category_id.account_expense_depreciation_id.id
        obj_account_move_line.with_context(ctx).create(
            self._setup_move_line_data(
                depreciation_date, depr_acc_id, "depreciation", move_id.id
            )
        )
        obj_account_move_line.with_context(ctx).create(
            self._setup_move_line_data(
                depreciation_date, exp_acc_id, "expense", move_id.id
            )
        )
        move_id.post()
        ctx = {"allow_asset_line_update": True}
        self.with_context(ctx).write({"move_id": move_id.id})
        created_move_ids.append(move_id.id)
        asset_ids.append(asset.id)
        # we re-evaluate the assets to determine whether we can close them
        for asset in obj_fixed_asset.browse(list(set(asset_ids))):
            currency = asset.company_id.currency_id
            if currency.is_zero(asset.value_residual):
                asset.write({"state": "close"})
        return created_move_ids

    def _get_action_account_move(self):
        action = self.env.ref("account." "action_move_journal_line").read()[0]
        return action

    def open_move(self):
        self.ensure_one()
        move = self.move_id
        action = self._get_action_account_move()

        if len(move) > 0:
            action["domain"] = [("id", "=", move.id)]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def unlink_move(self):
        ctx = {"unlink_from_asset": True, "force_delete": True}
        move = self.move_id
        if move.state == "posted":
            move.button_cancel()
        move.with_context(ctx).unlink()

        self.with_context(ctx).write({"move_id": False})
        if self.parent_state == "close":
            self.asset_id.write({"state": "open"})
        elif self.parent_state == "removed" and self.type == "remove":
            self.asset_id.write({"state": "close"})
            self.unlink()
        return True

    def _mark_as_init(self):
        self.ensure_one()
        self.write({"init_entry": True})
        asset = self.asset_id
        currency = asset.company_id.currency_id
        if currency.is_zero(asset.value_residual):
            asset.write({"state": "close"})

    def action_mark_as_init(self):
        for document in self.sudo():
            document._mark_as_init()

    def _unmark_as_init(self):
        self.ensure_one()
        self.write({"init_entry": False})
        asset = self.asset_id
        currency = asset.company_id.currency_id
        if not currency.is_zero(asset.value_residual):
            asset.write({"state": "open"})

    def action_unmark_as_init(self):
        for document in self.sudo():
            document._unmark_as_init()

    def action_compute(self):
        for document in self.sudo():
            document._compute()
