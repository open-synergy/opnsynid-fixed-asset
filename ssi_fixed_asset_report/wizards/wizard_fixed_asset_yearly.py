# -*- coding: utf-8 -*-
# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import Warning as UserError


class WizardFixedAssetYearly(models.TransientModel):
    _name = "account.wizard_fixed_asset_yearly"
    _description = "Print Yearly Asset Report"

    year = fields.Integer(
        string="Year",
        required=True,
        default=0,
    )
    asset_category_ids = fields.Many2many(
        string="Asset Category",
        comodel_name="fixed.asset.category",
        relation="rel_report_fixed_asset_yearly_2_category",
        column1="wizard_id",
        column2="asset_category_id",
    )

    def button_export_html(self):
        self.ensure_one()
        report_type = "qweb-html"
        return self._export(report_type)

    def button_export_pdf(self):
        self.ensure_one()
        report_type = "qweb-pdf"
        return self._export(report_type)

    def button_export_xlsx(self):
        self.ensure_one()
        report_type = "xlsx"
        return self._export(report_type)

    def _export(self, report_type):
        """Default export is PDF."""
        return self._print_report(report_type)

    def _print_report(self, report_type):
        self.ensure_one()
        data = self._prepare_report_fixed_asset()
        if report_type == "xlsx":
            report_name = "a_f_r.report_aged_partner_balance_xlsx"
        else:
            report_name = "account_financial_report.aged_partner_balance"
        return (
            self.env["ir.actions.report"]
            .search(
                [("report_name", "=", report_name), ("report_type", "=", report_type)],
                limit=1,
            )
            .report_action(self, data=data)
        )

    def _prepare_report_fixed_asset(self):
        self.ensure_one()
        return {
            "wizard_id": self.id,
            "year": self.year,
            "company_id": self.env.user.company_id.id,
            "asset_category_ids": self.asset_category_ids.ids,
            "fixed_asset_report_lang": self.env.lang,
        }
