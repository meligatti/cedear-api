from datetime import date

def today_formatted_string():
    unf_date = date.today()
    # return unf_date.strftime("%d/%m/%Y")
    return unf_date.strftime("%Y-%m-%d %H:%M:%S")

class Stock:
    def __init__(self):
        self.name = ""
        #TODO: Replace this definition for the one upwards
        # self.date = date.today().strftime("%Y-%m-%d %H:%M:%S")
        self.date = today_formatted_string()
        # Hora sujeta a empresa (3 am o 5 pm)
        self.hour = "03:00" 
        
        self.opening = 0
        self.closing = 0
        self.min_price = 0
        self.max_price = 0
        
        self.amount_exchanged = 0
        self.daily_variation = 0
        