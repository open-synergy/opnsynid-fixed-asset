# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FixedAssetDisposalType(models.Model):
    _name = "fixed.asset.disposal_type"
    _inherit = ["mail.thread"]
    _description = "Fixed Asset Disposal Type"

    name = fields.Char(
        string="Type",
        required=True,
    )
    code = fields.Char(
        string="Code",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    note = fields.Text(
        string="Note",
    )
    set_disposition_price = fields.Boolean(
        string="Allow To Set Disposition Price",
        default=False,
    )
    sequence_id = fields.Many2one(
        string="Sequence",
        comodel_name="ir.sequence",
        company_dependent=True,
    )
    disposal_journal_id = fields.Many2one(
        string="Disposal Journal",
        comodel_name="account.journal",
        company_dependent=True,
    )
    exchange_account_id = fields.Many2one(
        string="Exchange Account",
        comodel_name="account.account",
        ondelete="restrict",
    )
    gain_account_id = fields.Many2one(
        string="Gain Account",
        comodel_name="account.account",
        ondelete="restrict",
    )
    loss_account_id = fields.Many2one(
        string="Loss Account",
        comodel_name="account.account",
        ondelete="restrict",
    )
