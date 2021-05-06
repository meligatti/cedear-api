import re

def get_hour_index(hour):
    hour_match = re.search("[0-2][0-9]:[0-5][0-9]", hour)#:[0-5][0-9]",
                           #hour)
    return hour_match.span()

def get_hour_pos(tag):
        return re.search("[0-2][0-9]:[0-5][0-9]", tag).span()

def get_date_pos(tag):
    return re.search("[0-3][0-9]/[0-1][0-9]", tag).span()


# Para los nombres y simbolos tiene que ser '\r\n ', en los casos que no me acuerdo era con '\\r\\n '
def clean_data(data):
    removable_chars = '\r\n '
    return data.translate({ord(i): None for i in removable_chars})


def check_if_today(data_orig_title_content):
    try:
        idx = data_orig_title_content.rindex("hoy")
    except ValueError:
        return False
    else:
        return True

# # Función para reformatear la fecha para cargar en la db
# def reformat_date(date_str):
#     day_end_index = 2
#     month_width = 2
#     month_end_index = day_end_index + month_width
#     return date_str[month_end_index + 1 : -1] + ""

# Function to convert strings into decimal numbers

def remove_separator_points(str_number):
    return str_number.replace('.', '')

def fixed_point_conversion(str_number):
    str_no_point = remove_separator_points(str_number)
    str_fixed_point = str_no_point.replace(',', '.')
    return float(str_fixed_point)

# Function to fix some bugs related with stock names with points or that which has
# same name as SQL operator
def fix_stock_name(stock_name):
    # Replace points in stock name to avoid errors in table name
    key = stock_name.replace(".", "_")
    # This is to correct an error caused for a MySQL operator named "MOD"
    if stock_name == "MOD":
        key = "MOD_STK"
    return key