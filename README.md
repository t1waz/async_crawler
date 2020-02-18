	.__. __..   ,.  . __  __ .__ .__..  ..   .___.__ 
	[__](__  \./ |\ |/  `/  `[__)[__]|  ||   [__ [__)
	|  |.__)  |  | \|\__.\__.|  \|  ||/\||___[___|  \


GETTING STARTED
===============

App main puropose is to show possible solution for building app using Starlette with Tortoise ORM.
Project initialy inspired by Django REST.

- new resources should be put inside separate apps.
- thanks to generic serializators, generic views, and "app architecture" - fast development, and high flexibility should be accomplished.
- pipeline can be easily extended.
- it's just a simple demo, source code should evolve with development.


ENDPOINTS
---------

	+----------------------+---------+-------------------+--------+
	|    endpoint          | methods |       data        | return |
	+----------------------+---------+-------------------+--------+
	| /add_link            |   POST  | 'url', 'interval' |   id   |
	| /get_link_info       |   GET   |                   |        |
	| /get_link_info/{id}' |   GET   |                   |  data  |
	+----------------------+---------+-------------------+--------+


- /add_link - interval parameter is optional. In future, this parameter will be used to periodically get link data. Return token/id for registered data.

- /get_link_info - return status for all links

- /get_link_info/{id} - return status for link with id(token)


OTHER
-----

server_test.py - simple script to auto generate data. In future simple benchmark for core modules.


INSTALL
=======

Software requirements
---------------------

Required Python >= 3.7

Required Postgres


Postgresql install
------------------

Create database and database user:

	$ sudo su - postgres
	$ psql

Create database:

	postgres=# CREATE DATABASE <db_name>;

Create database user:

	postgres=# CREATE USER <username> WITH PASSWORD '<secret_password>';

Set database:

	postgres=# ALTER ROLE <username> SET client_encoding TO 'utf8';
	postgres=# ALTER ROLE <username> SET default_transaction_isolation TO 'read committed';
	postgres=# ALTER ROLE <username> SET timezone TO 'UTC';
	postgres=# GRANT ALL PRIVILEGES ON DATABASE <db_name> TO <username>

Quit:

	postgres=# \q


Project dev install
-------------------

Create python venv:

	$ python3 -m venv .venv


Activate:

	$ source .venv/bin/activate


Install packages:

	$ pip install -r requirements.txt


Create .env file==from main dir):

	$ touch .env


Fill .env with data:

	DB_HOST=<host>
	DB_PORT=<port>
	DB_USER=<username>
	DB_PASSWORD=<password>
	DB_NAME=<db_name>

Start:

	$ python crawler/main.py

Enjoy !