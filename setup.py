from setuptools import setup

from auto_version import calculate_version

name = 'jsonsocket'

version = calculate_version()
setup(
    name=name,
    version=version,
    description='This is a small Python library for sending data over sockets. ',
    author='github',
    author_email='',
    packages=[name],  #same as name
    requirements=["schedule"]
)