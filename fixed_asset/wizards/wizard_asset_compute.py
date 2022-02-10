# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class AssetDepreciationConfirmationWizard(models.TransientModel):
    _name = "asset.depreciation.confirmation.wizard"
    _description = "asset.depreciation.confirmation.wizard"

    date_end = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.today,
        help="All depreciation lines prior to this date will be automatically"
        " posted",
    )

    @api.multi
    def asset_compute(self):
        assets = self.env["fixed.asset.asset"].search(
            [("state", "=", "open"), ("type", "=", "normal")]
        )
        created_move_ids, error_log = assets._compute_entries(
            self.date_end, check_triggers=True
        )

        if error_log:
            module = __name__.split("addons.")[1].split(".")[0]
            result_view = self.env.ref(
                "{}.{}_view_form_result".format(module, self._table)
            )
            self.note = _("Compute Assets errors") + ":\n" + error_log
            return {
                "name": _("Compute Assets result"),
                "res_id": self.id,
                "view_type": "form",
                "view_mode": "form",
                "res_model": "asset.depreciation.confirmation.wizard",
                "view_id": result_view.id,
                "target": "new",
                "type": "ir.actions.act_window",
                "context": {"asset_move_ids": created_move_ids},
            }

        return {
            "name": _("Created Asset Moves"),
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "account.move",
            "view_id": False,
            "domain": [("id", "in", created_move_ids)],
            "type": "ir.actions.act_window",
        }

    @api.multi
    def view_asset_moves(self):
        self.ensure_one()
        domain = [("id", "in", self.env.context.get("asset_move_ids", []))]
        return {
            "name": _("Created Asset Moves"),
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "account.move",
            "view_id": False,
            "domain": domain,
            "type": "ir.actions.act_window",
        }
