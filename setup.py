from anobbs_core import AppConstant
from setuptools import setup, find_packages

setup(
    name=AppConstant.NAME,
    version=AppConstant.VERSION,
    packages=find_packages(),
    description=AppConstant.DESC,
    url=AppConstant.URL,
    author=AppConstant.AUTHOR_NAME,
    author_email=AppConstant.AUTHOR_EMAIL,
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "click",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            f'anobbs=anobbs_cli.app:cli'
        ],
    },
)
