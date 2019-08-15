import os

from setuptools import setup, find_packages

import django_federal_reserve

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


def get_reqs(*fns):
    lst = []
    for fn in fns:
        for package in open(os.path.join(CURRENT_DIR, fn)).readlines():
            package = package.strip()
            if not package or package.startswith('#'):
                continue
            lst.append(package)
    return lst


setup(
    name="django-federal-reserve",
    version=django_federal_reserve.__version__,
    packages=find_packages(),
    author="Chris Spencer",
    author_email="chrisspen@gmail.com",
    description="Django model for storing Federal Reserve time series.",
    license="LGPLv3",
    url="https://github.com/chrisspen/django-federal-reserve",
    #https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    install_requires=get_reqs('requirements.txt', 'requirements-django.txt'),
    tests_require=get_reqs('requirements-test.txt'),
)
