# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FixedAssetDisposalType(models.Model):
    _name = "fixed_asset.disposal_type"
    _inherit = [
        "mixin.master_data",
    ]
    _description = "Fixed Asset Disposal Type"

    name = fields.Char(
        string="Disposal Type",
    )
    set_disposition_price = fields.Boolean(
        string="Allow To Set Disposition Price",
        default=False,
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
        company_dependent=True,
    )
    gain_account_id = fields.Many2one(
        string="Gain Account",
        comodel_name="account.account",
        ondelete="restrict",
        company_dependent=True,
    )
    loss_account_id = fields.Many2one(
        string="Loss Account",
        comodel_name="account.account",
        ondelete="restrict",
        company_dependent=True,
    )
