import webscraping as ws

import sqlhandler as sqlh
import dboperations as dbo

from datetime import datetime

if __name__ == "__main__":
    # It generates a dictionary of Stock objects with all the daily parameters read from "Invertir Online" inside.
    # These are: opening, closing, minimum price, maximum price, daily variation and amount exchanged.
    stock_dict = ws.iol_parsing()

    # Database configuration
    host_name = "localhost"
    user_name = "root"
    user_password = "Darkwater_06"
    db = "sample_cedears_db"

    # Execute these lines to create the database. It doesn't overwrite an existing one with same name.
    conn = sqlh.create_connection(host_name, user_name, user_password)
    dbo.create_db(conn, db)
    conn.close()

    conn = sqlh.create_connection(host_name, user_name, user_password, db)

    # This function is necessary to be able to create a table and track a possible new stock. It doesn't overwrite
    # the existing ones.
    dbo.create_db_tables(conn, stock_dict)
    # It stores the downloaded data in the database
    # dbo.add_stock_data(conn, stock_dict)

    # This function is used to plot stock parameters on selected dates. The user can edit the date interval. The
    # followed format is datetime(YYYY, MM, DD). When any of the dates is outside the range, the results include up to
    # last date contained.
    # Stock names:
    # There are some stocks which names contain a point. To be able to query the corresponding table, you should
    # replace the point with an underscore.
    # In the case of the stock named 'MOD', it's called as a MySQL operator. For this reason, it's renamed as 'MOD_STK'
    # Here, the user can edit the date interval. The followed format is datetime(YYYY, MM, DD).
    # When any of the dates is outside the range, the results include up to last date contained.
    desired_dates = (datetime(2021, 6, 14), datetime(2021, 6, 23))
    dbo.show_sample_stock_plots(conn, 'aapl', desired_dates)

    # If you need to erase the database, execute this lines
    # erase_db_query = "DROP DATABASE " + db
    # sqlh.execute_query(conn, erase_db_query)

    conn.close()
