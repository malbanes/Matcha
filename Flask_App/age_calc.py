from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


def age(birthdate):
    if birthdate is None:
        return("N/A")
    today = date.today()
    
    one_or_zero = ((today.month, today.day) < (birthdate.month, birthdate.day))
    
    year_diff = today.year - birthdate.year

    age = year_diff - one_or_zero
    
    return age

def age_period(y):
# minus number of year
    currentTimeDate = (datetime.today()-relativedelta(years=int(y))).strftime("%Y-%m-%d")
    print(currentTimeDate)
    return(currentTimeDate)