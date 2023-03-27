# -*- coding: utf-8 -*-
# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import Warning as UserError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class WizardFixedAssetYearly(models.TransientModel):
    _name = "account.wizard_fixed_asset_yearly"
    _description = "Print Yearly Asset Report"

    @api.constrains("year")
    def _check_year(self):
        if not 2000 < self.year < 2100:
            raise UserError(
                _(f"Invalid year {self.year}.")
            )

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
            report_name = "a_f_r.report_fixed_asset_yearly_xlsx"
        else:
            report_name = "ssi_fixed_asset_report.report_fixed_asset_yearly"
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
        fixed_asset_yearly = []
        if self.asset_category_ids:
            category_ids = self.asset_category_ids
        else:
            category_ids = self.env['fixed.asset.category'].search([])
        date_end = f'{self.year}-12-31'
        criteria = [
            ("date_start", "<=", date_end),
            ("state", "in", ["open", "close", "removed"]),
        ]
        for category_id in category_ids:
            assets = []
            asset_ids = self.env['fixed.asset.asset'].search(criteria + [('category_id', '=', category_id.id)])
            no = 1
            for asset in asset_ids:
                assets.append({
                    "no": no,
                    "res_id": asset.id,
                    "code": asset.code,
                    "name": asset.name,
                    "acquisition_value": asset.purchase_value,
                    "vendor": asset.partner_id and asset.partner_id.commercial_partner_id.name or "-",
                    "vendor_id": asset.partner_id and asset.partner_id.commercial_partner_id.id or 0,
                    "start_date": asset.date_start.strftime("%d %B %Y"),
                    "age": str(asset.method_number) + " " + asset.method_time,
                    "salvage_value": asset.salvage_value,
                    "nbv_previous_year": self._get_nbv_previous_year(asset),
                    "dpr_previous_year": self._get_dpr_previous_year(asset),
                    "depr1": self._get_depreciation_amount(asset, 1),
                    "depr2": self._get_depreciation_amount(asset, 2),
                    "depr3": self._get_depreciation_amount(asset, 3),
                    "depr4": self._get_depreciation_amount(asset, 4),
                    "depr5": self._get_depreciation_amount(asset, 5),
                    "depr6": self._get_depreciation_amount(asset, 6),
                    "depr7": self._get_depreciation_amount(asset, 7),
                    "depr8": self._get_depreciation_amount(asset, 8),
                    "depr9": self._get_depreciation_amount(asset, 9),
                    "depr10": self._get_depreciation_amount(asset, 10),
                    "depr11": self._get_depreciation_amount(asset, 11),
                    "depr12": self._get_depreciation_amount(asset, 12),
                    "dpr_current_year": self._get_dpr_current_year(asset),
                    "nbv_current_year": self._get_nbv_current_year(asset),
                })
                no += 1
            if not assets:
                continue
            fixed_asset_yearly.append({
                'category_name': category_id.display_name,
                'assets': assets,
            })
        return {
            "wizard_id": self.id,
            "year": str(self.year),
            "asset_categories": ', '.join(self.asset_category_ids.mapped('display_name')),
            "fixed_asset_report_lang": self.env.lang,
            'company_name': self.env.user.company_id.name,
            'currency_name': self.env.user.company_id.currency_id.name,
            'fixed_asset_yearly': fixed_asset_yearly,
        }

    def _get_nbv_previous_year(self, asset):
        date_end = date(self.year, 12, 31)
        filtered = asset.depreciation_line_ids.filtered(
            lambda x: x.line_date <= date_end and (x.init_entry or x.move_check)
        )
        result = 0.0
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.type, r.line_date), reverse=True)
            sorted = sorteds[0]
            result = sorted.remaining_value
        return result

    def _get_dpr_previous_year(self, asset):
        date_end = date(self.year, 12, 31)
        filtered = asset.depreciation_line_ids.filtered(
            lambda x: x.line_date <= date_end and (x.init_entry or x.move_check)
        )
        result = 0.0
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.type, r.line_date), reverse=True)
            sorted = sorteds[0]
            result = sorted.depreciated_value + sorted.amount
        return result

    def _get_depreciation_amount(self, asset, month):
        dt_date_start = datetime(self.year, month, 1)
        date_start = dt_date_start.date()
        date_end = (dt_date_start + relativedelta(months=1, days=-1)).date()
        filtered = asset.depreciation_line_ids.filtered(
            lambda x: (
                date_start <= x.line_date <= date_end
                and x.init_entry
                and x.type in ("depreciate", "remove")
            )
            or (
                x.move_id
                and date_start <= x.move_id.date <= date_end
                and x.move_check
                and x.type in ("depreciate", "remove")
            )
        )
        result = 0.0
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.type, r.line_date), reverse=True)
            for sorted in sorteds:
                result += sorted.amount
        return result

    def _get_dpr_current_year(self, asset):
        date_end = date(self.year, 12, 31)
        filtered = asset.depreciation_line_ids.filtered(
            lambda x: x.line_date <= date_end and (x.init_entry or x.move_check)
        )
        result = 0.0
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.type, r.line_date), reverse=True)
            sorted = sorteds[0]
            result = sorted.depreciated_value + sorted.amount
        return result

    def _get_nbv_current_year(self, asset):
        date_end = date(self.year, 12, 31)
        filtered = asset.depreciation_line_ids.filtered(
            lambda x: x.line_date <= date_end and (x.init_entry or x.move_check)
        )
        result = 0.0
        if filtered:
            sorteds = filtered.sorted(key=lambda r: (r.type, r.line_date), reverse=True)
            sorted = sorteds[0]
            result = sorted.remaining_value
        return result
