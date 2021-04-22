from bs4 import BeautifulSoup
import requests

from Stock import Stock
import textparsing as tp

import SQLHandler as sqlh

from datetime import date


def db_connect():
    host_name = "localhost"
    username = "root"
    passwrd = "Darkwater_06"
    db_name = "stock_price_db"

    connection = sqlh.create_connection(host_name, username, passwrd, db_name)
    return connection

def create_db_tables(stock_dict, connection):
    # Nota: no me convendrá que la key sea la fecha?
    primary_query = """
    CREATE TABLE IF NOT EXISTS date_ids (
        ID INT PRIMARY KEY AUTO_INCREMENT,
        DATE DATETIME NOT NULL
    );
    """
    sqlh.create_table(connection, primary_query)

    for key in stock_dict:
        # Basado en los datos, veo que la apertura y cierre están en un máximo de 50k.
        # De cuántas cifras sería un orden de magnitud razonable?
        company_query = """
        CREATE TABLE IF NOT EXISTS
        """ + key + """(
            DATE_ID DATETIME NOT NULL,
            OPENING NUMERIC(5,2),
            CLOSING NUMERIC(5,2),
            MIN_PRICE NUMERIC(5,2),
            MAX_PRICE NUMERIC(5,2),          
            AMOUNT_EXCHANGED NUMERIC(9,0),
            DAILY_VARIATION NUMERIC(2,2),          
            FOREIGN KEY (DATE_ID) REFERENCES date_ids(DATE)
        );
        """
        print(company_query)
        sqlh.create_table(connection, company_query)

def add_stock_data(stock_dict, connection):
    for key in stock_dict:
        company_stock = stock_dict[key]
        date_query = """
        INSERT INTO date_ids(DATE)
        VALUES (""" + company_stock.date + """);"""

        sqlh.add_records(connection, date_query)

        # Va el DATE_ID?
        stock_data_query = """
        INSERT INTO""" + key + """(DATE_ID, OPENING, CLOSING, MIN_PRICE, MAX_PRICE, AMOUNT_EXCHANGED, DAILY_VARIATION)""" + """VALUES (""" + company_stock.date, company_stock.opening, company_stock.closing, company_stock.min_price, company_stock.max_price, company_stock.amount_exchanged, company_stock.daily_variation + """);"""

        sqlh.add_records(connection, stock_data_query)



def main():
    
    #url = 'https://www.invertironline.com/mercado/cotizaciones/argentina/acciones/cedears'
    url = 'https://www.invertironline.com/mercado/cotizaciones/argentina/cedears/todos'
    response = requests.get(url)

    web_content = BeautifulSoup(response.text, 'lxml')
    #print(BeautifulSoup.prettify(web_content))

    #tag = web_content.attrs
    #print(tag)

    # # Cada elemento en una página web tiene un id único. En este caso, la tabla tiene de id "cotizaciones"
    # # Consta de una cabecera <thead>, un cuerpo <tbody> y un pie <tfoot>. Se puede ver como tabla con un
    # # encabezado con los campos, el contenido, y el pie con, por ejemplo, la suma de las ventas
    table_results = web_content.find(id = 'cotizaciones')
    print(table_results.prettify())
    #
    # Segmento la tabla en filas <TableRow>, que representan a cada empresa
    table_rows = table_results.find_all('tr')
    header_parsed = False

    # En mayuscula guardo 2020 y en minúscula 20 (primero más ineficiente en espacio
    # pero es unívoco el año, fallo 2k)
    year_format = "%Y"
    current_year = date.today().strftime(year_format)
    current_date = date.today().strftime("%d/%m/" + year_format)

    hour_offset = 5

    stock_dict = {}


    dict_columns = {"href": 0,
                    "UltimoOperado": 1,
                    # En tags
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
                    # En tags
                    "FechaHoraFormated": 12}

    # Por cada ciclo tengo una fila de la tabla
    for tr in table_rows:
        tds = tr.find_all('td')

        if header_parsed == True:
            new_stock = Stock()
            for key in dict_columns:
                stock_tags = tds[dict_columns[key]].contents

                if key == "href":   # dict_columns[0]
                    for tag in stock_tags:
                        idx = str(tag).find(key)
                        if idx != -1:
                            name = tag['title']
                            symbol = tp.clean_data(tag.b.contents[0])
                            new_stock.name = name
                            break

                elif key == "Variacion":
                    for tag in stock_tags:
                        idx = str(tag).find(key)
                        if idx != -1:
                            new_stock.daily_variation = tag.get_text()
                            break

                elif key == "Apertura":
                    new_stock.opening = tp.clean_data(stock_tags[0])

                elif key == "Minimo":
                    new_stock.min_price = tp.clean_data(stock_tags[0])

                elif key == "Maximo":
                    new_stock.max_price = tp.clean_data(stock_tags[0])

                elif key == "UltimoCierre":
                    new_stock.closing = tp.clean_data(stock_tags[0])

                elif key == "MontoOperado":
                    new_stock.amount_exchanged = tp.clean_data(stock_tags[0])

                elif key == "FechaHoraFormated":
                    for tag in stock_tags:
                        idx = str(tag).find(key)
                        if idx != -1:
                            date_tag = tag['data-original-title']
                            if tp.check_if_today(date_tag) == True:
                                hour = tag.span.contents[0]
                                (start, _) = tp.get_hour_index(hour)
                                #second_sep = hour.rindex(":")
                                #clean_hour = hour[: second_sep]
                                clean_hour = hour[start : start + hour_offset]
                                new_stock.hour = clean_hour
                                new_stock.date = current_date
                            else:
                                # Debería estar bien
                                (start, finish) = tp.get_hour_index(date_tag)
                                new_stock.hour = date_tag[start : finish]
                                new_stock.date = tp.clean_data(tag.span.contents[0]) + "/" + current_year
                            ## NOTA: Me sale que la key que le pongo no puede ser una expresion, pero es un string!
                            ## Versión que no me funcaba era update(new_stock.symbol = new_stock)
                            stock_dict.update({symbol : new_stock })

        else:
            header_parsed = True

    return stock_dict


if __name__ == "__main__":
    stock_list = main()
    # If applies
    host_name = "localhost"
    user_name = "root"
    user_password = "Darkwater_06"
    db = "stock_prices_db"
    
    # Uso esta versión si ya tengo la base creada
    #conn = sqlh.create_connection(host_name, user_name, user_password)
    #create_db_query = "CREATE DATABASE " + db
    #sqlh.create_database(conn, create_db_query)
    
    
    # Uso esta otra si necesito crearla
    conn = sqlh.create_connection(host_name, user_name, user_password, db)
    
    create_db_tables(stock_list, conn)
    #add_stock_data(stock_list, conn)
