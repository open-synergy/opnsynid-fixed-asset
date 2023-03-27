# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Fixed Asset Report",
    "version": "14.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "report_xlsx",
        "ssi_fixed_asset",
    ],
    "external_dependencies": {

    },
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
    "demo": [

    ],
    "images": [

    ],
}
