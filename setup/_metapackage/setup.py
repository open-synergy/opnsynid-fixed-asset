import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-open-synergy-opnsynid-fixed-asset",
    description="Meta package for open-synergy-opnsynid-fixed-asset Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-fixed_asset',
        'odoo11-addon-fixed_asset_disposal',
        'odoo11-addon-fixed_asset_queue',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 11.0',
    ]
)
