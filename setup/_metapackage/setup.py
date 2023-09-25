import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-open-synergy-opnsynid-fixed-asset",
    description="Meta package for open-synergy-opnsynid-fixed-asset Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ssi_fixed_asset',
        'odoo14-addon-ssi_fixed_asset_complex_asset',
        'odoo14-addon-ssi_fixed_asset_disposal',
        'odoo14-addon-ssi_fixed_asset_in_progress',
        'odoo14-addon-ssi_fixed_asset_qrcode',
        'odoo14-addon-ssi_fixed_asset_report',
        'odoo14-addon-ssi_fixed_asset_salvage_value_estimation_change',
        'odoo14-addon-ssi_fixed_asset_useful_life_estimation_change',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
