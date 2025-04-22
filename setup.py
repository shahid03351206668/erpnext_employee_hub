from setuptools import setup, find_packages

with open("requirements.txt") as f:
        install_requires = f.read().strip().split("\n")

# get version from __version__ variable in test/__init__.py
from erpnext_employee_hub import __version__ as version

setup(
        name="erpnext_employee_hub",
        version=version,
        description="ERPNext Employee Hub",
        author="Codes Soft",
        author_email="info@codessoft.com",
        packages=find_packages(),
        zip_safe=False,
        include_package_data=True,
        install_requires=install_requires,
)
