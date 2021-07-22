import random

from bs4 import BeautifulSoup
import requests

from Stock import Stock
import textparsing as tp

import sqlhandler as sqlh

from datetime import date
from datetime import datetime

import stockplot as sp


def create_db_tables(connection, stock_dict):
    primary_query = """
        CREATE TABLE IF NOT EXISTS date_ids (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL
        );
        """
    sqlh.execute_query(connection, primary_query)

    for key in stock_dict:
        # Here the name of the stock is modified to prevent any error on table creation. See line 279.
        key = tp.fix_stock_name(key)
        company_query = """
                CREATE TABLE IF NOT EXISTS
                """ + key + """(
                    date_id INT NOT NULL AUTO_INCREMENT,
                    opening NUMERIC(8,2),
                    closing NUMERIC(8,2),
                    min_price NUMERIC(8,2),
                    max_price NUMERIC(8,2),
                    amount_exchanged NUMERIC(11,0),
                    daily_variation NUMERIC(4,2),
                    FOREIGN KEY (date_id) REFERENCES date_ids(id)
                );
                """
        sqlh.execute_query(connection, company_query)

# Set of auxiliary functions. They are meant to help to check a record existence for a given date because the query
# to write the data changes

# Checks on date_ids table the associate numeric id to a certain date
def get_date_id(connection, ref_date):
    search_date_query = """SELECT id FROM date_ids WHERE date_ids.date = """ + "'" + ref_date + "'"
    return sqlh.execute_read_query(connection, search_date_query)

def check_date_existence(connection, ref_date):
    return get_date_id(connection, ref_date) != []

# Returns a row with all the stock information from the selected date.
def get_record(connection, ref_date_id, selected_stock):
    read_stock_query = """SELECT * FROM """ + selected_stock + """ WHERE """ + selected_stock + ".date_id = " + str(
        ref_date_id)
    return sqlh.execute_read_query(connection, read_stock_query)

def check_record_existence(connection, ref_date_id, selected_stock):
    return get_record(connection, ref_date_id, selected_stock) != []




def add_stock_data(connection, stock_dict):
    # All the stocks were tracked on the same dates, 'AAPL' was selected just because it's the first named and it's not
    # a new stock in the market.
    key = 'AAPL'
    company_stock = stock_dict[key]
    ref_date = company_stock.date
    # Here a new date is inserted. Code added to prevent that a single date can have several ids.
    if not check_date_existence(connection, ref_date):
        date_query = """INSERT INTO date_ids(date)
                        VALUES (%s)"""
        insert_date_tuple = (ref_date, )
        sqlh.execute_insertion_query(connection, date_query, insert_date_tuple)
    else:
        print("Date already inserted")

    # Obtain the id number associated with the last date
    ref_date_id = get_date_id(connection, ref_date)
    ref_date_id = ref_date_id[0][0]

    # This section writes the downloaded information on each company table
    for key in stock_dict:
        company_stock = stock_dict[key]
        # If there is no record made for a given date, it will store it. If there is a previous one, it's overwritten
        # to update the data.
        if not check_record_existence(connection, ref_date_id, key):
            stock_data_query = """
                INSERT INTO """ + key + """(DATE_ID, OPENING, CLOSING, MIN_PRICE, MAX_PRICE, AMOUNT_EXCHANGED, DAILY_VARIATION)
                VALUES (%s, %s, %s, %s, %s, %s, %s)"""

            insert_stock_tuple = (ref_date_id, company_stock.opening, company_stock.closing, company_stock.min_price,
                                  company_stock.max_price, company_stock.amount_exchanged, company_stock.daily_variation)
            sqlh.execute_insertion_query(connection, stock_data_query, insert_stock_tuple)
        else:
            stock_data_query = """UPDATE """ + key + """ SET OPENING = %s, CLOSING = %s, MIN_PRICE = %s, MAX_PRICE = %s, AMOUNT_EXCHANGED = %s, DAILY_VARIATION = %s WHERE """ + key + ".date_id = %s"

            update_stock_tuple = (company_stock.opening, company_stock.closing, company_stock.min_price,
                                  company_stock.max_price, company_stock.amount_exchanged, company_stock.daily_variation,
                                  ref_date_id)
            sqlh.execute_insertion_query(connection, stock_data_query, update_stock_tuple)


def show_sample_stock_plots(connection, selected_stock):
    # Here, the user can edit the date interval. The followed format is datetime(YYYY, MM, DD).
    # When any of the dates is outside the range, the results include up to last date contained.
    desired_dates = (datetime(2021, 6, 14), datetime(2021, 8, 30))
    read_dates_query = """SELECT * FROM date_ids WHERE date BETWEEN %s AND %s"""
    date_records = sqlh.execute_read_query(conn, read_dates_query, desired_dates)

    if date_records == []:
        print("There's no record between the given dates")
    else:
        id_col = 0
        date_col = 1
        date_list = [current_date[:][date_col] for current_date in date_records]

        stock_records_list = []
        for date_id in range(len(date_list)):
            read_stock_query = """SELECT * FROM """ + selected_stock + " WHERE DATE_ID = " + str(date_records[date_id][id_col])
            stock_records = sqlh.execute_read_query(conn, read_stock_query)
            stock_records_list.append(stock_records)
        stock_records_list = [elem[0] for elem in stock_records_list]

        date_id = 0
        opening = 1
        closing = 2
        min_price = 3
        max_price = 4
        amount_exchanged = 5
        daily_variation = 6

        # Get a list with all the stock names
        read_names_query = "SHOW TABLES"
        stock_names_list = sqlh.execute_read_query(connection, read_names_query)
        stock_names_list = [stock_name[:][0] for stock_name in stock_names_list]
        stock_names_list.remove('date_ids')

        opening_list = [stock_tuple[opening] for stock_tuple in stock_records_list]
        closing_list = [stock_tuple[closing] for stock_tuple in stock_records_list]
        minimum_price_list = [stock_tuple[min_price] for stock_tuple in stock_records_list]
        maximum_price_list = [stock_tuple[max_price] for stock_tuple in stock_records_list]
        amount_xch_list = [stock_tuple[amount_exchanged] for stock_tuple in stock_records_list]

        sp.ohlc_plot(opening_list, maximum_price_list, minimum_price_list, closing_list, date_list, stock_names_list,
                     selected_stock)
        sp.draw_amount_exchanged(amount_xch_list, date_list, stock_names_list, selected_stock)


def main():

    # Load into a variable the HTML code of the page
    url = 'https://iol.invertironline.com/mercado/cotizaciones/argentina/cedears/todos'
    response = requests.get(url)
    web_content = BeautifulSoup(response.text, 'lxml')

    # Each element in a website has a unique id. In this case, the table is named as "cotizaciones".
    # It has a header <thead>, a body <tbody> and a footer <tfoot>.
    table_results = web_content.find(id = 'cotizaciones')

    # Each row represents a company, so I generate a list of all rows <TableRow>.
    table_rows = table_results.find_all('tr')

    # Today date is formatted to comply with the defined one in the database.
    year_format = "%Y"
    current_year = date.today().strftime(year_format)
    current_date = date.today().strftime(year_format + "-%m-%d")

    stock_dict = {}

    # This dictionary contains the data fields of the table
    column_dict = {"href": 0,
                    "UltimoOperado": 1,
                    "Variacion":2,
                    "CantidadCompra": 3,
                    "PrecioCompra": 4,
                    "PrecioVenta": 5,
                    "CantidadVenta": 6,
                    "Apertura": 7,
                    "Minimo": 8,
                    "Maximo": 9,
                    "UltimoCierre": 10,
                    "MontoOperado": 11,
                    "FechaHoraFormated": 12}

    # Each cycle refers to a different company (therefore a different row). The first row is the header of the table
    # so it's necessary to skip it
    for tr in table_rows[1:]:
        # Get every cells of the row
        tds = tr.find_all('td')

        new_stock = Stock()
        # Get the information from the cells I defined on the dictionary
        for key in column_dict:
            # tds[column_dict[key]] returns all the code of that cell while adding .contents returns a list of all
            # the children of the td tag
            # https://towardsdatascience.com/web-scraping-with-python-beautifulsoup-40d2ce4b6252
            stock_tags = tds[column_dict[key]].contents
            if key == "href":   # column_dict[0]
                for tag in stock_tags:
                    # Find the key between the elements of the stock_tags array
                    if tp.is_key_in_tag(tag, key):
                        # The name is the value of the attribute 'title' and the symbol is the text of the tag <b>
                        name = tag['title']
                        symbol = tp.fix_stock_name(tp.clean_data(tag.b.contents[0]))
                        new_stock.name = name
                        break

            elif key == "Variacion":
                for tag in stock_tags:
                    if tp.is_key_in_tag(tag, key):
                        new_stock.daily_variation = tp.fixed_point_conversion(tag.get_text())
                        break

            elif key == "Apertura":
                new_stock.opening = tp.fixed_point_conversion(stock_tags[0])

            elif key == "Minimo":
                new_stock.min_price = tp.fixed_point_conversion(stock_tags[0])

            elif key == "Maximo":
                new_stock.max_price = tp.fixed_point_conversion(stock_tags[0])

            elif key == "UltimoCierre":
                new_stock.closing = tp.fixed_point_conversion(stock_tags[0])

            elif key == "MontoOperado":
                new_stock.amount_exchanged = int(tp.fixed_point_conversion(stock_tags[0]))

            elif key == "FechaHoraFormated":
                for tag in stock_tags:
                    if tp.is_key_in_tag(tag, key):
                        date_tag = tag['data-original-title']
                        if tp.check_if_today(date_tag):
                            hour = tag.span.contents[0]
                            new_stock.hour = tp.clean_hour_str(hour)
                            new_stock.date = current_date
                        else:
                            new_stock.hour = tp.get_hour_str(date_tag)
                            new_stock.date = tp.reformat_date(tp.clean_data(tag.span.contents[0]) + "/" + current_year)

                        stock_dict.update({symbol: new_stock})

    return stock_dict


if __name__ == "__main__":
    # It generates a dictionary of Stock objects with all the daily parameters read from "Invertir Online" inside.
    # These are: opening, closing, minimum price, maximum price, daily variation and amount exchanged.
    stock_dict = main()
    # Database configuration
    host_name = "localhost"
    user_name = "root"
    user_password = "Darkwater_06"
    # db = "14th_jun_db"
    db = "dates_test_db"

    # Execute these lines to create the database. It doesn't overwrite an existing one with same name.
    conn = sqlh.create_connection(host_name, user_name, user_password)
    create_db_query = """CREATE DATABASE IF NOT EXISTS """ + db
    sqlh.execute_query(conn, create_db_query)
    conn.close()

    conn = sqlh.create_connection(host_name, user_name, user_password, db)

    # This function is necessary to be able to create a table and track a possible new stock. It doesn't overwrite
    # the existing ones.
    create_db_tables(conn, stock_dict)
    # It stores the downloaded data in the database
    add_stock_data(conn, stock_dict)

    # This function is used to plot stock parameters on selected dates. They can be edited inside the function.
    # Stock names:
    # There are some stocks which names contain a point. To be able to query the corresponding table, you should
    # replace the point with an underscore.
    # In the case of the stock named 'MOD', it's called as a MySQL operator. For this reason, it's renamed as 'MOD_STK'
    # show_sample_stock_plots(conn, 'aapl')

    # If you need to erase the database, execute this lines
    # erase_db_query = "DROP DATABASE " + db
    # sqlh.execute_query(conn, erase_db_query)

    conn.close()
