
from setuptools import setup

with open('requirements.txt') as f:
    install_packs = f.read().splitlines()


setup(
    name='pyVcsa',
    version='0.0.1',
    description='VMware VCSA module for dealing with the appliance REST api',
    license='Apache',
    packages=['pyVcsa'],
    install_requires=install_packs,
    author='Sammy Shuck github.com/ToxicSamN',
    keywords=['pyvcsa'],
    url='https://github.com/ToxicSamN/pyVcsa'
)
