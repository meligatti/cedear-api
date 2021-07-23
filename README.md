# CEDEAR API

This program is intended to read the daily records from the webpage Invertir Online and store the different parameters
of the CEDEAR stock values in a relational database (MySQL). The stored data can be visualized by the user.  

## Dependences
This API was written and tested on Python 3.6. It's necessary to install the packages beautifulsoup4 (4.9.1), requests (2.23.0), matplotlib (3.2.1),
and mysql-connector-python (8.0.21).

The database used was local, so you'll need to install MySQL Community Edition Workbench (8.0.21) which can be 
downloaded on: https://dev.mysql.com/downloads/workbench/. The user should set the hostname as localhost to execute a local database and I've made the tests using the root user.

## Execution
The program must be executed from the main file. There's a function that creates the database if not exists and another one
that fills the db with all the tables (one with the dates tracked and one per company).

In the folder _'sample_db_dump'_, you can load a dump from the database used to have your own copy. It covers from 
06/14/2021 to 07/20/2021. To do that, you'll need to enter into MySQL Workbench, create your database in a query tab and
then import the provided .sql file onto your db. 

To check the proper working, you should use the function called _show_sample_stock_plot_ that can be used to read a table
from a company specified by the user and a date range and see the corresponding plots (OHLC and amount exchanged).

The data table on Invertir Online refreshes periodically every 20 minutes up to 5 pm (time in Argentina) on working days,
so take this into account to make sure that you'll store the final daily data. It's convenient to run the program when 
the _'Último Operado'_ and _'Último cierre'_ values are the same.






