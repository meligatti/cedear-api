# CEDEAR API

This program is intended to read the daily records from the webpage Invertir Online and store the different parameters
of the CEDEAR stock values in a relational database (MySQL).

## Dependences
This was written and tested on Python 3.6. It's necessary to install the packages beautifulsoup4 (4.9.1), requests (2.23.0) 
and mysql-connector-python (8.0.21).

The database on the test was local, so you'll need to install MySQL Community Edition Workbench (8.0.21) which can be 
downloaded on: https://dev.mysql.com/downloads/workbench/ . The user should set the hostname as localhost to execute a local database and I've made the tests using the root user.

## Execution
The program must be executed from the main file. There is a function that creates the database if not exists and another one
that fills the db with all the tables (one with the dates tracked and one per company).

To check the correct working, there is another function (called _read_db_) that can be used to read a table from some companies in a date range 
or a single day specified by the user. The data table on Invertir Online refreshes periodically every 20 minutes up to 5 pm (time in Argentina) on working days.  

__NOTE:__ This is a working first version, and it has a known bug to fix. 
It is related with the possibility of writing data on the database several times from the same day. For this reason, I suggest
to run the software after the last table update to guarantee that there will be just one record (the final one) per day until the bug can be fixed.
is fixed.





