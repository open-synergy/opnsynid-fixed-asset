import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-open-synergy-opnsynid-fixed-asset",
    description="Meta package for open-synergy-opnsynid-fixed-asset Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-fixed_asset',
        'odoo8-addon-fixed_asset_capital_improvement',
        'odoo8-addon-fixed_asset_complex_asset',
        'odoo8-addon-fixed_asset_estimation_change',
        'odoo8-addon-fixed_asset_from_inventory',
        'odoo8-addon-fixed_asset_impairment',
        'odoo8-addon-fixed_asset_qrcode',
        'odoo8-addon-fixed_asset_retirement_common',
        'odoo8-addon-fixed_asset_retirement_donation',
        'odoo8-addon-fixed_asset_retirement_missing',
        'odoo8-addon-fixed_asset_retirement_sale',
        'odoo8-addon-fixed_asset_retirement_scrap',
        'odoo8-addon-fixed_asset_retirement_stolen',
        'odoo8-addon-fixed_asset_stock',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
