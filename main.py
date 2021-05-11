import random

from bs4 import BeautifulSoup
import requests

from Stock import Stock
import textparsing as tp

import sqlhandler as sqlh

from datetime import date
from datetime import datetime

def check_date_consistency(stock_dict, connection):
    curr_date = stock_dict['PCAR'].date



def create_db_tables(stock_dict, connection):
    primary_query = """
        CREATE TABLE IF NOT EXISTS date_ids (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL
        );
        """
    sqlh.execute_query(connection, primary_query)

    for key in stock_dict:
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
    # All the stocks were tracked on the same dates, 'AAPL' was selected just because it's the first named
    key = 'PCAR'
    company_stock = stock_dict[key]
    date_query = """INSERT INTO date_ids(date)
                    VALUES (%s)"""
    insert_date_tuple = (company_stock.date, )
    sqlh.execute_insertion_query(connection, date_query, insert_date_tuple)
    for key in stock_dict:
        company_stock = stock_dict[key]
        curr_date = company_stock.date
        date_id_query = """SELECT * FROM date_ids WHERE date = %s"""
        # print(datetime.strptime(curr_date, '%Y-%m-%d'))
        date_id_found = sqlh.execute_read_query(connection, date_id_query, (datetime.strptime(curr_date, '%Y-%m-%d'),))
        date_id = date_id_found[0][0]

        stock_data_query = """
            INSERT INTO """ + key + """(DATE_ID, OPENING, CLOSING, MIN_PRICE, MAX_PRICE, AMOUNT_EXCHANGED, DAILY_VARIATION)
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""

        insert_stock_tuple = (date_id, company_stock.opening, company_stock.closing, company_stock.min_price,
                              company_stock.max_price, company_stock.amount_exchanged, company_stock.daily_variation)
        sqlh.execute_insertion_query(connection, stock_data_query, insert_stock_tuple)

def read_random_stock(connection):
    # There were some stocks which name have a point.
    selected_companies = ['aapl', 'ba_c', 'mod_stk']
    desired_date = (datetime(2021, 5, 6), datetime(2021, 5, 7))
    dates_length = len(desired_date)

    if dates_length == 1:
        read_date_query = """SELECT * FROM date_ids WHERE date = %s"""
    elif dates_length == 2:
        read_date_query = """SELECT * FROM date_ids WHERE date BETWEEN %s AND %s"""
    else:
        read_date_query = """SELECT * FROM date_ids"""

    date_list = sqlh.execute_read_query(connection, read_date_query, desired_date)
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

    # read_single_query = """
    #     SELECT OPENING, CLOSING, MIN_PRICE, MAX_PRICE, AMOUNT_EXCHANGED, DAILY_VARIATION FROM """ + selected_companies + " WHERE DATE_ID = " + str(id)
    # read_single_query = """SELECT * FROM """ + selected_companies + " WHERE DATE_ID = " + str(id)
    # print(read_single_query)
    # The element returned is a list with the values of all the fields of that row.
    # company_row = sqlh.execute_read_query(connection, read_single_query)
    # Here I skipped the first element corresponding to the date id.
    # company_row = company_row[0][1:]


def main():

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
    stock_list = main()
    # If applies
    host_name = "localhost"
    user_name = "root"
    user_password = "Darkwater_06"
    db = "stock_prices_db"
    # db = "concha"

    # Execute these lines if database is not created
    # conn = sqlh.create_connection(host_name, user_name, user_password)
    # create_db_query = """CREATE DATABASE """ + db
    # sqlh.execute_query(conn, create_db_query)
    # conn.close()

    conn = sqlh.create_connection(host_name, user_name, user_password, db)

    # Borro la database para empezar otra vez
    # erase_db_query = "DROP DATABASE " + db
    # sqlh.execute_query(conn, erase_db_query)

    create_db_tables(stock_list, conn)
    add_stock_data(conn, stock_list)

    # read_random_stock(conn)
    conn.close()
