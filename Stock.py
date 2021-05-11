from datetime import date

def today_formatted_string():
    unf_date = date.today()
    return unf_date.strftime("%Y-%m-%d %H:%M:%S")

class Stock:
    def __init__(self):
        self.name = ""
        self.date = today_formatted_string()
        # The last update hour can be at 3 am or 5 pm
        self.hour = "03:00" 
        
        self.opening = 0
        self.closing = 0
        self.min_price = 0
        self.max_price = 0
        
        self.amount_exchanged = 0
        self.daily_variation = 0
        