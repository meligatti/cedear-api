import re
from datetime import datetime


# Set of functions meant to search hour or date in a string and to reformate a certain date.

def get_hour_index(hour):
    hour_match = re.search("[0-2][0-9]:[0-5][0-9]", hour)
    return hour_match.span()

def get_hour_str(date_tag):
    (start, finish) = get_hour_index(date_tag)
    return date_tag[start: finish]

def get_hour_pos(tag):
        return re.search("[0-2][0-9]:[0-5][0-9]", tag).span()

def get_date_pos(tag):
    return re.search("[0-3][0-9]/[0-1][0-9]", tag).span()

def reformat_date(str_date):
    date_datetime = datetime.strptime(str_date, '%d/%m/%Y')
    return date_datetime.strftime('%Y-%m-%d')

def clean_hour_str(hour_str):
    hour_offset = 5
    (start, _) = get_hour_index(hour_str)
    return hour_str[start : start + hour_offset]


# The data has some extra symbols (\r\n) which must be removed
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


# Function to convert strings into decimal numbers
def remove_separator_points(str_number):
    return str_number.replace('.', '')

def fixed_point_conversion(str_number):
    clean_str = clean_data(str_number)
    str_no_point = remove_separator_points(clean_str)
    str_fixed_point = str_no_point.replace(',', '.')
    return float(str_fixed_point)


# Function to fix some bugs related with stock names with points or that which has
# same name as SQL operator. See line 35 from main.py.
def fix_stock_name(stock_name):
    clean_stock_name = clean_data(stock_name)
    # Replace points in stock name to avoid errors in table name
    key = stock_name.replace(".", "_")
    # This is to correct an error caused for a MySQL operator named "MOD"
    if clean_stock_name == "MOD":
        key = "MOD_STK"
    return key

# Function to get the original stock name for those that had changed.
def revert_stock_name_fix(stock_name):
    if stock_name == 'mod_stk':
        reversed_stock_name = 'mod'
    elif '_' in stock_name:
        reversed_stock_name = stock_name.replace('_', '.')
    else:
        reversed_stock_name = stock_name
    return reversed_stock_name



# Check if is possible to find a key in a tag
def is_key_in_tag(tag, key):
    result = False
    if (str(tag).find(key)) != -1:
        result = True
    return result



# Auxiliary functions that help to determine a stock currency

def is_base_stock_name(str_to_eval, substr):
    return substr == str_to_eval

def is_usd_stock_exception(str_to_eval):
    return str_to_eval == 'bad' or str_to_eval == 'c_d' or str_to_eval == 'gogld' or str_to_eval == 'mod_stk' or str_to_eval == 'vd'

def is_ars_stock_exception(str_to_eval):
    return str_to_eval == 'bbd' or str_to_eval == 'tmd'