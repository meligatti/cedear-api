import random

from bs4 import BeautifulSoup
import requests

from Stock import Stock
import textparsing as tp

import sqlhandler as sqlh

from datetime import date
from datetime import datetime


def create_db_tables(connection, stock_dict):
    primary_query = """
        CREATE TABLE IF NOT EXISTS date_ids (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL
        );
        """
    sqlh.execute_query(connection, primary_query)

    for key in stock_dict:
        # Here the name of the stock is modified if it can cause any error on table creation
        # Continues on line 74.
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


def add_stock_data(connection, stock_dict):
    # All the stocks were tracked on the same dates, 'AAPL' was selected just because it's the first named and it's not
    # a new stock in the market.

    # Here it's inserted a new date
    key = 'AAPL'
    # The key must be uppercase
    company_stock = stock_dict[key.upper()]
    date_query = """INSERT INTO date_ids(date)
                    VALUES (%s)"""
    insert_date_tuple = (company_stock.date, )
    sqlh.execute_insertion_query(connection, date_query, insert_date_tuple)

    # This code writes the downloaded information on each company table
    for key in stock_dict:
        company_stock = stock_dict[key]
        curr_date = company_stock.date
        date_id_query = """SELECT * FROM date_ids WHERE date = %s"""
        date_id_found = sqlh.execute_read_query(connection, date_id_query, (datetime.strptime(curr_date, '%Y-%m-%d'),))
        date_id = date_id_found[0][0]

        stock_data_query = """
            INSERT INTO """ + key + """(DATE_ID, OPENING, CLOSING, MIN_PRICE, MAX_PRICE, AMOUNT_EXCHANGED, DAILY_VARIATION)
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""

        insert_stock_tuple = (date_id, company_stock.opening, company_stock.closing, company_stock.min_price,
                              company_stock.max_price, company_stock.amount_exchanged, company_stock.daily_variation)
        sqlh.execute_insertion_query(connection, stock_data_query, insert_stock_tuple)

def read_db(connection):
    # There were some stocks which names contain a point. To be able to query the corresponding table, you should
    # replace the point with an underscore.
    # In the case of the stock named 'MOD', it's called as a MySQL operator. For this reason, it's renamed as 'MOD_STK'

    # If you want to select a single stock, it's important to put its name between brackets
    # selected_companies = ['aapl']
    selected_companies = ['aapl', 'ba_c', 'mod_stk']
    # If you want to select a specific date (not an interval), you should put it between parenthesis and with a comma
    # at the end, like in the following line:
    # desired_dates = (datetime(YYYY, MM, DD),)
    desired_dates = (datetime(2021, 5, 11), datetime(2021, 5, 12))
    dates_length = len(desired_dates)

    if dates_length == 1:
        read_date_query = """SELECT * FROM date_ids WHERE date = %s"""
    elif dates_length == 2:
        read_date_query = """SELECT * FROM date_ids WHERE date BETWEEN %s AND %s"""
    else:
        read_date_query = """SELECT * FROM date_ids"""

    date_list = sqlh.execute_read_query(connection, read_date_query, desired_dates)
    id_row = 0
    date_row = 1

    result_dict = {}

    for company in selected_companies:
        print(company)
        stock_list = []
        for date_id in range(len(date_list)):
            read_single_query = """SELECT * FROM """ + company + " WHERE DATE_ID = " + str(date_list[date_id][id_row])
            company_row = sqlh.execute_read_query(connection, read_single_query)
            print(date_list[date_id][date_row])
            print(company_row)
            stock_list.append(company_row)
        print('\n')
        result_dict[company] = stock_list


def main():

    # Load into a variable the HTML code of the page
    url = 'https://www.invertironline.com/mercado/cotizaciones/argentina/cedears/todos'
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
    db = "stock_prices_db"

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

    # This function is used to print stock parameters on selected date(s). The user can edit the variables named
    # selected companies and desired dates.
    read_db(conn)
    conn.close()

    # If you need to erase the database, execute this lines
    # erase_db_query = "DROP DATABASE " + db
    # sqlh.execute_query(conn, erase_db_query)
