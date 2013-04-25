from setuptools import setup, find_packages

import djcroco


setup(
    name='djcroco',
    packages=find_packages(),
    include_package_data=True,
    version=djcroco.__version__,
    description='',
    long_description=open('README.rst').read(),
    author=djcroco.__author__,
    author_email='matt.lenc@gmail.com',
    url='https://github.com/mattack108/djcroco/',
    install_requires=[
        'crocodoc',
    ],
    zip_safe=False,
)
