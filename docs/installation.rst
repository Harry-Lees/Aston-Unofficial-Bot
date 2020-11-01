Installation
============

Python Version
--------------

We recommend using the latest version of Python3. This project was created using Python3.8

Python Dependancies
-------------------

These dependancies will be installed automatically when using Docker.

::

    $ pip3 install -r requirements.txt

- Flask
- ItsDangerous
- FlaskMail
- Gunicorn
- FlaskWTF
- Discord

Docker
------

To run this project, you must have Docker and Docker-compose installed. These services
handle running the Database, Flask, and Discord bot. Although it is possible to run snippets of this project
individually, you will not be able to use the entire project without the use of docker-compose.

You may follow the `docker installation guide <https://docs.docker.com/get-docker/>`_ for more information
about this topic.

Once all of these dependancies have been installed, you may follow the Quickstart guide for information 
about building and developing the project. 