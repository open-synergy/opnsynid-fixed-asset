# Author: Damien Crier
# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# Copyright 2021 Tecnativa - João Marques
# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class FixedAssetYearlyXslx(models.AbstractModel):
    _name = "report.a_f_r.report_fixed_asset_yearly_xlsx"
    _description = "Fixed Asset Yearly XLSX Report"
    _inherit = "report.report_xlsx.abstract"

    def get_column_names(self):
        return [
            "NO",
            "CODE",
            "NAME",
            "VENDOR",
            "ACQUISITION VALUE",
            "START DATE",
            "AGE (YEAR)",
            "SALVAGE VALUE",
            "NBV PREVIOUS YEAR",
            "ACCUMULATED DEPR",
            "I",
            "II",
            "III",
            "IV",
            "V",
            "VI",
            "VII",
            "VIII",
            "IX",
            "X",
            "XI",
            "XII",
            "ACCUMULATED DEPR",
            "NBV",
        ]

    def generate_xlsx_report(self, workbook, data, objects):
        wbf, workbook = self.add_workbook_format(workbook)
        worksheet = workbook.add_worksheet("Yearly Asset Report")
        worksheet.set_column("A:A", 5)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 40)
        worksheet.set_column("D:Z", 20)
        row = 1
        worksheet.merge_range(
            f"A{row}:X{row}",
            f'Fixed Asset Yearly - {data["company_name"]} - {data["currency_name"]}',
            wbf["title_doc"],
        )
        worksheet.set_row(row - 1, 25)
        row += 2
        worksheet.write(row, 1, "Year filter", wbf["header"])
        worksheet.write(row, 2, "Asset category filter", wbf["header"])
        row += 1
        worksheet.write(row, 1, data["year"], wbf["content_center"])
        worksheet.write(row, 2, data["asset_categories"], wbf["content_center"])
        row += 3
        for category in data["fixed_asset_yearly"]:
            worksheet.merge_range(
                f"A{row}:B{row}", category["category_name"], wbf["content_bold"]
            )
            worksheet.write(row, 2, data["asset_categories"], wbf["content"])
            column_names = self.get_column_names()
            col = 0
            for column_name in column_names:
                worksheet.write(row, col, column_name, wbf["header"])
                col += 1
            row += 1
            for asset in category["assets"]:
                worksheet.write(row, 0, asset["no"], wbf["content_no"])
                worksheet.write(row, 1, asset["code"], wbf["content"])
                worksheet.write(row, 2, asset["name"], wbf["content"])
                worksheet.write(row, 3, asset["vendor"], wbf["content"])
                worksheet.write(
                    row, 4, asset["acquisition_value"], wbf["content_float"]
                )
                worksheet.write(row, 5, asset["start_date"], wbf["content"])
                worksheet.write(row, 6, asset["age"], wbf["content"])
                worksheet.write(row, 7, asset["salvage_value"], wbf["content_float"])
                worksheet.write(
                    row, 8, asset["nbv_previous_year"], wbf["content_float"]
                )
                worksheet.write(
                    row, 9, asset["dpr_previous_year"], wbf["content_float"]
                )
                worksheet.write(row, 10, asset["depr1"], wbf["content_float"])
                worksheet.write(row, 11, asset["depr2"], wbf["content_float"])
                worksheet.write(row, 12, asset["depr3"], wbf["content_float"])
                worksheet.write(row, 13, asset["depr4"], wbf["content_float"])
                worksheet.write(row, 14, asset["depr5"], wbf["content_float"])
                worksheet.write(row, 15, asset["depr6"], wbf["content_float"])
                worksheet.write(row, 16, asset["depr7"], wbf["content_float"])
                worksheet.write(row, 17, asset["depr8"], wbf["content_float"])
                worksheet.write(row, 18, asset["depr9"], wbf["content_float"])
                worksheet.write(row, 19, asset["depr10"], wbf["content_float"])
                worksheet.write(row, 20, asset["depr11"], wbf["content_float"])
                worksheet.write(row, 21, asset["depr12"], wbf["content_float"])
                worksheet.write(
                    row, 22, asset["dpr_current_year"], wbf["content_float"]
                )
                worksheet.write(
                    row, 23, asset["nbv_current_year"], wbf["content_float"]
                )
                row += 1
            row += 2

    def add_workbook_format(self, workbook):
        colors = {
            "white_orange": "#FFFFDB",
            "orange": "#FFC300",
            "red": "#FF0000",
            "yellow": "#F6FA03",
        }

        wbf = {}
        wbf["header"] = workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "bg_color": "#FFFFDB",
                "font_color": "#000000",
                "font_name": "Arial",
            }
        )
        wbf["header"].set_border()

        wbf["header_orange"] = workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "bg_color": colors["orange"],
                "font_color": "#000000",
                "font_name": "Arial",
            }
        )
        wbf["header_orange"].set_border()

        wbf["header_yellow"] = workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "bg_color": colors["yellow"],
                "font_color": "#000000",
                "font_name": "Arial",
            }
        )
        wbf["header_yellow"].set_border()

        wbf["header_no"] = workbook.add_format(
            {
                "bold": 1,
                "align": "center",
                "bg_color": "#FFFFDB",
                "font_color": "#000000",
                "font_name": "Arial",
            }
        )
        wbf["header_no"].set_border()
        wbf["header_no"].set_align("vcenter")

        wbf["footer"] = workbook.add_format({"align": "left", "font_name": "Arial"})

        wbf["content_datetime"] = workbook.add_format(
            {"num_format": "yyyy-mm-dd hh:mm:ss", "font_name": "Arial"}
        )
        wbf["content_datetime"].set_left()
        wbf["content_datetime"].set_right()

        wbf["content_date"] = workbook.add_format(
            {"num_format": "yyyy-mm-dd", "font_name": "Arial"}
        )
        wbf["content_date"].set_border()

        wbf["title_doc"] = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_size": 20,
                "font_name": "Arial",
                "text_wrap": True,
            }
        )

        wbf["company"] = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_size": 15,
                "font_name": "Arial",
                "text_wrap": True,
            }
        )

        wbf["content"] = workbook.add_format()
        wbf["content"].set_border()

        wbf["content_center"] = workbook.add_format(
            {
                "align": "center",
                "valign": "vcenter",
                "bold": False,
            }
        )
        wbf["content_center"].set_border()

        wbf["content_bold"] = workbook.add_format(
            {
                "bold": True,
            }
        )

        wbf["content_no"] = workbook.add_format({"align": "center"})
        wbf["content_no"].set_border()

        wbf["content_float"] = workbook.add_format(
            {"align": "right", "num_format": "#,##0.00", "font_name": "Arial"}
        )
        wbf["content_float"].set_border()

        wbf["content_float_bold"] = workbook.add_format(
            {
                "align": "right",
                "num_format": "#,##0.00",
                "font_name": "Arial",
                "bold": True,
            }
        )

        wbf["content_number"] = workbook.add_format(
            {"align": "right", "num_format": "#,##0", "font_name": "Arial"}
        )
        wbf["content_number"].set_right()
        wbf["content_number"].set_left()

        wbf["content_percent"] = workbook.add_format(
            {"align": "right", "num_format": "0.00%", "font_name": "Arial"}
        )
        wbf["content_percent"].set_right()
        wbf["content_percent"].set_left()

        wbf["total_float"] = workbook.add_format(
            {
                "bold": 1,
                "bg_color": colors["white_orange"],
                "align": "right",
                "num_format": "#,##0.00",
                "font_name": "Arial",
            }
        )
        wbf["total_float"].set_top()
        wbf["total_float"].set_bottom()
        wbf["total_float"].set_left()
        wbf["total_float"].set_right()

        wbf["total_number"] = workbook.add_format(
            {
                "align": "right",
                "bg_color": colors["white_orange"],
                "bold": 1,
                "num_format": "#,##0",
                "font_name": "Arial",
            }
        )
        wbf["total_number"].set_top()
        wbf["total_number"].set_bottom()
        wbf["total_number"].set_left()
        wbf["total_number"].set_right()

        wbf["total"] = workbook.add_format(
            {
                "bold": 1,
                "bg_color": colors["white_orange"],
                "align": "center",
                "font_name": "Arial",
            }
        )
        wbf["total"].set_left()
        wbf["total"].set_right()
        wbf["total"].set_top()
        wbf["total"].set_bottom()

        wbf["total_float_yellow"] = workbook.add_format(
            {
                "bold": 1,
                "bg_color": colors["yellow"],
                "align": "right",
                "num_format": "#,##0.00",
                "font_name": "Arial",
            }
        )
        wbf["total_float_yellow"].set_top()
        wbf["total_float_yellow"].set_bottom()
        wbf["total_float_yellow"].set_left()
        wbf["total_float_yellow"].set_right()

        wbf["total_number_yellow"] = workbook.add_format(
            {
                "align": "right",
                "bg_color": colors["yellow"],
                "bold": 1,
                "num_format": "#,##0",
                "font_name": "Arial",
            }
        )
        wbf["total_number_yellow"].set_top()
        wbf["total_number_yellow"].set_bottom()
        wbf["total_number_yellow"].set_left()
        wbf["total_number_yellow"].set_right()

        wbf["total_yellow"] = workbook.add_format(
            {
                "bold": 1,
                "bg_color": colors["yellow"],
                "align": "center",
                "font_name": "Arial",
            }
        )
        wbf["total_yellow"].set_left()
        wbf["total_yellow"].set_right()
        wbf["total_yellow"].set_top()
        wbf["total_yellow"].set_bottom()

        wbf["total_float_orange"] = workbook.add_format(
            {
                "bold": 1,
                "bg_color": colors["orange"],
                "align": "right",
                "num_format": "#,##0.00",
                "font_name": "Arial",
            }
        )
        wbf["total_float_orange"].set_top()
        wbf["total_float_orange"].set_bottom()
        wbf["total_float_orange"].set_left()
        wbf["total_float_orange"].set_right()

        wbf["total_number_orange"] = workbook.add_format(
            {
                "align": "right",
                "bg_color": colors["orange"],
                "bold": 1,
                "num_format": "#,##0",
                "font_name": "Arial",
            }
        )
        wbf["total_number_orange"].set_top()
        wbf["total_number_orange"].set_bottom()
        wbf["total_number_orange"].set_left()
        wbf["total_number_orange"].set_right()

        wbf["total_orange"] = workbook.add_format(
            {
                "bold": 1,
                "bg_color": colors["orange"],
                "align": "center",
                "font_name": "Arial",
                "num_format": "#,##0.00",
            }
        )
        wbf["total_orange"].set_left()
        wbf["total_orange"].set_right()
        wbf["total_orange"].set_top()
        wbf["total_orange"].set_bottom()

        wbf["header_detail_space"] = workbook.add_format({"font_name": "Arial"})
        wbf["header_detail_space"].set_left()
        wbf["header_detail_space"].set_right()
        wbf["header_detail_space"].set_top()
        wbf["header_detail_space"].set_bottom()

        wbf["header_detail"] = workbook.add_format(
            {"bg_color": "#E0FFC2", "font_name": "Arial"}
        )
        wbf["header_detail"].set_left()
        wbf["header_detail"].set_right()
        wbf["header_detail"].set_top()
        wbf["header_detail"].set_bottom()

        return wbf, workbook
