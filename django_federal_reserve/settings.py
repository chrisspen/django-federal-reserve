from django.conf import settings

# If true, ensures there's a value for every day.
# e.g. If values are only given for the first day of the month,
# then this will duplicate that value for each day in the month.
# Creates more records, but allows for faster indexing and joins
# since no inequality operators are needed.
EXPAND_DATA_TO_DAYS = settings.DFR_EXPAND_DATA_TO_DAYS = getattr(
    settings,
    'DFR_EXPAND_DATA_TO_DAYS',
    False)

BULK_URL = settings.DFR_BULK_URL = getattr(
    settings,
    'DFR_BULK_URL',
    'http://research.stlouisfed.org/fred2/downloaddata/FRED2_csv_2.zip')

CHUNK = settings.DFR_CHUNK = getattr(
    settings,
    'DFR_CHUNK',
    16 * 10240)

BULK_INDEX_FN = settings.DFR_BULK_INDEX_FN = getattr(
    settings,
    'DFR_BULK_INDEX_FN',
    'FRED2_csv_2/README_SERIES_ID_SORT.txt')

# The number of days a series must be stale with before its checked
# for an update.
# A bigger value allows fewer updates but risks having more stale data.
# A smaller value keeps fresher data but may waste more time unnecessarily
# checking for updates.
LAST_UPDATE_DAYS = settings.DFR_LAST_UPDATE_DAYS = getattr(
    settings,
    'DFR_LAST_UPDATE_DAYS',
    60)

API_KEY = settings.DFR_API_KEY = getattr(
    settings,
    'DFR_API_KEY',
    None)
