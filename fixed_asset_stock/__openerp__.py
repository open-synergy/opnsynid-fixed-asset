# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Stock and Asset Management Integration",
    "version": "8.0.2.5.0",
    "category": "Accounting & Finance",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "fixed_asset",
        "stock_move_backdating",
    ],
    "data": [
        "wizards/create_fixed_asset_from_lot.xml",
        "wizards/link_fixed_asset_to_lot.xml",
        "views/account_asset_views.xml",
        "views/product_template_views.xml",
        "views/product_category_views.xml",
        "views/stock_production_lot_views.xml",
        "views/stock_move_views.xml",
        "views/stock_quant_views.xml",
        "views/account_asset_config_setting_views.xml",
    ],
}
