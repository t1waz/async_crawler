	.__. __..   ,.  . __  __ .__ .__..  ..   .___.__ 
	[__](__  \./ |\ |/  `/  `[__)[__]|  ||   [__ [__)
	|  |.__)  |  | \|\__.\__.|  \|  ||/\||___[___|  \


GETTING STARTED
===============

Project main puropose is to show possible solution for building app using Starlette with Tortoise ORM.
Project initialy inspired by Django REST.

- new resources should be implemented inside separate apps.
- thanks to generic serializators, generic views, and "app architecture" - fast development, and high flexibility should be accomplished.
- pipeline can be easily extended.
- it's just a simple demo, source code should evolve with development.

Notice!
-------
exceptions are not properly handled, just for PoC purpose. Logger should be added.

ENDPOINTS
---------

	+----------------------+---------+-------------------+--------+
	|    endpoint          | methods |       data        | return |
	+----------------------+---------+-------------------+--------+
	| /add_link            |   POST  | 'url', 'interval' |   id   |
	| /get_link_info       |   GET   |                   |  data  |
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


Project dev install
-------------------


	$ docker-compose build
	$ docker-compose up


Enjoy !