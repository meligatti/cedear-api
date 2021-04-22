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