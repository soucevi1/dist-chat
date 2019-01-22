.. soucevi1_dist_chat documentation master file, created by
   sphinx-quickstart on Mon Jan 21 15:04:17 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

soucevi1_dist_chat
==================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules
   tutorial
   usage


This program is a semestral project on MI-PYT and MI-DSV courses at FIT CTU in Prague. It is implemented in Python 3.7 and uses `AsyncIO <https://docs.python.org/3/library/asyncio.html>`_. Since a few new AsyncIO features were used in this program, it is necessary to have **Python 3.7 or higher** to run it.

This application is a CLI chat room program. However, it does not use a simple server-client way. All nodes are clients, any node can be a server from this point of view.

The chatroom is a network ring (a node only knows its *next* and *previous* node), however all nodes know the *leader* node (chat coordinator) as well in order to send it a message. The first node that creates the chatroom is automtically its *leader*. When the *leader* dies or logs out, the new *leader* is elected using `Chang-Roberts leader election algorithm <https://en.wikipedia.org/wiki/Chang_and_Roberts_algorithm>`_.

Installation
============
The program is uploaded on `PyPI <https://pypi.org/project/soucevi1-dist-chat/>`_.

For the newest version, just type::

 $ python -m pip install soucevi1_dist_chat

For any specific version, type::

 $ python -m pip install soucevi1_dist_chat==<version>

You can also clone and use the `GitHub repository <https://github.com/soucevi1/dist-chat>`_.

Example usage
=============
If you installed the program, you can create the room and chat!

Chatroom creation is very simple. You only need to run the leader node::

   $ soucevi1_dist_chat -l -n Name -a 1.2.3.4 -p 12345

The command above will run the leader node (``-l``) on IP address ``1.2.3.4`` and port ``12345`` with username ``Name``. The leader will listen and as soon as some other node makes a connection to it, the chat will start.

Then, you can start another node that will connect to the running leader::

   $ soucevi1_dist_chat -n Name2 -a 3.4.5.6 -p 54321 -na 1.2.3.4 -np 12345

This node is run by a user called ``Name2`` on ``3.4.5.6:54321``. As you can see, non-leader nodes need an address and a port of any node that is already participating in the chat in order to join the chatroom. If you want to read more about usage, read :ref:`ref-tutor`. More about the inner implementation is in :ref:`ref-impl`.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
