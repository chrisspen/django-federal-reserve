#http://research.stlouisfed.org/fred2/newcategoryzipfileformat
SEMIANNUALLY = 'SA'
ANNUALLY = 'A'
QUARTERLY = 'Q'
MONTHLY = 'M'
BIWEEKLY = 'BW'
WEEKLY = 'W'
DAILY = 'D'
NA = 'NA'

FREQUENCY_CHOICES = (
    (ANNUALLY, 'annually'),
    (BIWEEKLY, 'bi-weekly'),
    (DAILY, 'daily'),
    (MONTHLY, 'monthly'),
    (NA, 'not-applicable'),
    (QUARTERLY, 'quarterly'),
    (SEMIANNUALLY, 'semi-annually'),
    (WEEKLY, 'weekly'),
)


SEASONALLY_ADJUSTED = 'SA'# Seasonally Adjusted
NOT_SEASONALLY_ADJUSTED = 'NSA'# Not Seasonally Adjusted
SEASONALLY_ADJUSTED_ANNUAL_RATE = 'SAAR'# Seasonally Adjusted Annual Rate
NOT_APPLICABLE = 'NA'# Not Applicable
SMOOTHED_SEASONLLY_ADJUSTED = 'SSA'

ADJUSTED_CHOICES = (
    (SEASONALLY_ADJUSTED, 'seasonally adjusted'),
    (SEASONALLY_ADJUSTED_ANNUAL_RATE, 'seasonally adjusted annual rate'),
    (SMOOTHED_SEASONLLY_ADJUSTED, 'smoothed seasonally adjusted'),
    (NOT_APPLICABLE, 'not applicable'),
    (NOT_SEASONALLY_ADJUSTED, 'not seasonally adjusted'),
)
