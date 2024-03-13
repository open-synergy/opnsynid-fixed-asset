# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fixed Asset Report",
    "version": "14.0.1.7.0",
    "category": "Accounting & Finance",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "report_xlsx",
        "ssi_fixed_asset",
        "account_fiscal_year",
    ],
    "external_dependencies": {},
    "data": [
        "security/ir.model.access.csv",
        "wizards/wizard_fixed_yearly_asset.xml",
        "reports.xml",
        "report/templates/fixed_asset_yearly.xml",
        "report/templates/layouts.xml",
        "views/report_template.xml",
    ],
    "qweb": [
        "static/src/xml/report.xml",
    ],
    "demo": [],
    "images": [],
}
