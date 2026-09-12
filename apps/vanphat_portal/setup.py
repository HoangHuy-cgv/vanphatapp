from setuptools import find_packages, setup

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

from vanphat_portal import __version__ as version

setup(
	name="vanphat_portal",
	version=version,
	description="Van Phat portal (visual shell only, logic lives in ERPNext native)",
	author="Van Phat",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
)
