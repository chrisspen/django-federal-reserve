django-federal-reserve - Django models for storing Federal Reserve data
=======================================================================

Overview
========

Provides a model and tool for loading data series from the
[FRED website](http://research.stlouisfed.org/fred2).

Usage
=====

    python manage.py data_mirror_refresh FederalReserveDataSource
    
    python manage.py data_mirror_refresh FederalReserveDataSource --ids=WUPSHO
    