# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, fields


class AccountAssetRecomputeTrigger(models.Model):
    _name = "account.asset.recompute.trigger"
    _description = "Asset table recompute triggers"

    reason = fields.Char(
        string="Reason",
        size=64,
        required=True,
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
    )
    date_trigger = fields.Datetime(
        string="Trigger Date",
        readonly=True,
        help="Date of the event triggering the need to "
             "recompute the Asset Tables.",
    )
    date_completed = fields.Datetime(
        string="Completion Date",
        readonly=True,
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("open", "Open"),
            ("done", "Done")
        ],
        readonly=True,
    )
