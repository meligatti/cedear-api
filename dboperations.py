import sqlhandler as sqlh

import textparsing as tp

import stockplot as sp

from datetime import datetime


# These functions execute the main database functions (Create, Read, Update, Delete) by creating the corresponding
# queries and mixing them with data provided by the user.

def create_db(connection, db):
    create_db_query = """CREATE DATABASE IF NOT EXISTS """ + db
    sqlh.execute_query(connection, create_db_query)

def create_db_tables(connection, stock_dict):
    primary_query = """
        CREATE TABLE IF NOT EXISTS date_ids (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL
        );
        """
    sqlh.execute_query(connection, primary_query)

    for key in stock_dict:
        # Here the name of the stock is modified to prevent any error on table creation. See line 35 from main.py.
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
# to write the data changes if there is a previous one or not.

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


# Writes the downloaded information from 'Invertir Online' onto the tables from each company.
def add_stock_data(connection, stock_dict):
    # The reference date is obtained from a sample stock which value updates daily.
    key = 'AAPL'
    company_stock = stock_dict[key]
    ref_date = company_stock.date
    # Here, a new date is inserted. Code added to prevent a date from having multiple ids.
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

# Deletes the rows from the dates indicated by the user.
def delete_stock_rows(connection, stock_dict, datetimes_to_delete):
    id_list = []
    # Generate a list of ids associated with the dates to be deleted.
    for dtime in datetimes_to_delete:
        get_id_query = """SELECT id FROM date_ids WHERE date = %s"""
        desired_id = sqlh.execute_read_query(connection, get_id_query, dtime)
        desired_id = desired_id[:][0]
        id_list.append(desired_id)
    # Iterate over the database to erase the rows listed above.
    for key in stock_dict:
        delete_stock_row_query = """DELETE FROM """ + key + """ WHERE """ + key + ".date_id = %s"""
        sqlh.execute_deletion_query(connection, delete_stock_row_query, id_list)
    delete_dates_query = """DELETE FROM date_ids WHERE id = %s"""
    sqlh.execute_deletion_query(connection, delete_dates_query, id_list)


# Plots both charts (ohlc and amount exchanged).
def show_sample_stock_plots(connection, selected_stock, desired_dates):
    read_dates_query = """SELECT * FROM date_ids WHERE date BETWEEN %s AND %s"""
    date_records = sqlh.execute_read_query(connection, read_dates_query, desired_dates)

    if date_records == []:
        print("There's no record between the given dates")
    else:
        id_col = 0
        date_col = 1
        date_list = [current_date[:][date_col] for current_date in date_records]

        stock_records_list = []
        for date_id in range(len(date_list)):
            read_stock_query = """SELECT * FROM """ + selected_stock + " WHERE DATE_ID = " + str(date_records[date_id][id_col])
            stock_records = sqlh.execute_read_query(connection, read_stock_query)
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
