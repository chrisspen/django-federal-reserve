from setuptools import setup, find_packages, Command

import django_federal_reserve

setup(
    name = "django-federal-reserve",
    version = django_federal_reserve.__version__,
    packages = find_packages(),
    author = "Chris Spencer",
    author_email = "chrisspen@gmail.com",
    description = "Django model for storing Federal Reserve time series.",
    license = "LGPL",
    url = "https://github.com/chrisspen/django-federal-reserve",
    #https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    install_requires = [
        'Django>=1.4',
        'fred>=3.0',
        'django-data-mirror>=0.2.2',
    ],
)
