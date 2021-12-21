from bs4 import BeautifulSoup
import requests

import textparsing as tp

from datetime import date

from Stock import Stock

# This function returns a dictionary with all the downloaded stock data.
def iol_parsing():
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
                   "UltimoPrecio": 1,
                   "Variacion": 2,
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
            if key == "href":  # column_dict[0]
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

            elif key == "UltimoPrecio":
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