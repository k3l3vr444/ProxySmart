from setuptools import setup

setup(
    name='proxysmart',
    version='0.1',
    description='https://proxysmart.org/ API wrapper',
    author='k3l3vr444',
    author_email='ayukanov.nikita@gmail.com',
    packages=['proxysmart', 'proxysmart.types'],  # same as name
    install_requires=['pydantic', 'requests'],  # external packages as dependencies
)
