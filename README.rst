Distributed chat based on Chang-Roberts algorithm
=================================================

This program is a semestral project on MI-PYT and MI-DSV courses. It is implemented in Python 3.7 and uses `AsyncIO <https://docs.python.org/3/library/asyncio.html>`_.

This application is a chat room program. However, it does not use a simple server-client way. All nodes are clients, any node can be a server. 

The server is elected using `Chang-Roberts leader election algorithm <https://en.wikipedia.org/wiki/Chang_and_Roberts_algorithm>`_. Other nodes send their messages to the server node and the server distributes them to all the participants. When the server logs out or dies, new election is initialized on the first detection (a node detects the death of a server while attempting to send a message).

When a node wants to join the chat room, all it needs is one address of any node that is already in the room.

When a node wants to leave the room, it informs the server, which then informs all other nodes.

When a node dies without informing the others, the server detects it during the attempt to deliver a message to it.

Usually, programs like these are implemented using multiple threads (client thread, server thread...). 

Installation
------------
How to install this program.

Documentation
-------------
How to get the documentation.
