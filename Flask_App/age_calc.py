from datetime import date

def age(birthdate):
    if birthdate is None:
        return("N/A")
    today = date.today()
    
    one_or_zero = ((today.month, today.day) < (birthdate.month, birthdate.day))
    
    year_diff = today.year - birthdate.year

    age = year_diff - one_or_zero
    
    return age