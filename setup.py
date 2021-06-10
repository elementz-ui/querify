from setuptools import setup, find_packages

setup(
    name='elementz_querify',
    version='1.0.4',
    description='SQL Query Builder for Elementz Table',
    long_description='',
    license='GPL 3.0',
    author='Elis',
    author_email='open@elis.cc',
    keywords='elementz, table, sql, filters, parse, build',
    install_requires=['mysqlclient'],
    include_package_data=True,
    zip_safe=False,
	packages=find_packages(),
)