Distributed chat based on Chang-Roberts algorithm
=================================================

This program is a semestral project on MI-PYT and MI-DSV courses. It is implemented in Python 3.7 and uses `AsyncIO <https://docs.python.org/3/library/asyncio.html>`_.

Since a few new AsyncIO features were used in this program, it is necessary to have **Python 3.7 or higher** to run it.

This application is a CLI chat room program. However, it does not use a simple server-client way. All nodes are clients, any node can be a server from this point of view.

For better understanding, the server (node that manages the user messages) will be referred to as the *leader* and the AsyncIO component of the application that listens on the given port will be refered to as the *server* further on in the docuentation. Meaning that any node has a *server*, however only one node in the chatroom is the *leader*.

The chatroom is a network ring (a node only knows its *next* and *previous* node), however all nodes know the *leader* node as well in order to send it a message. The first node that creates the chatroom is automtically its *leader*. When the *leader* dies or logs out, the new *leader* is elected using `Chang-Roberts leader election algorithm <https://en.wikipedia.org/wiki/Chang_and_Roberts_algorithm>`_. 

When the user types a message, the node sends it to the *leader* node and the *leader* distributes it to all the participants (the *leader* knows them all).

When a node wants to join the chat room, all it needs is one address of any node that is already in the room.

When a node logs out or dies without informing the others, its next and previous nodes detect it and repair the ring.

Installation
------------
The program is uploaded on `PyPI <https://pypi.org/project/soucevi1-dist-chat/>`_.

For the newest version, just type::

   python -m pip install soucevi1_dist_chat

For any specific version, type::

   python -m pip install soucevi1_dist_chat==<version>

You can also clone and use the `GitHub repository <https://github.com/soucevi1/dist-chat>`_.

Usage
-----

Creating the chatroom
^^^^^^^^^^^^^^^^^^^^^

To run the application as the leader node after the installation, type::

   soucevi1_dist_chat -l -a <IP> -p <port> -n <your name>

Where ``<IP>`` and ``<port>`` is the IP address and port the node will listen on, ``<your name>`` is the username of your choice and ``-l`` stands for being the *leader*.

Joining the existing chatroom
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To join the existing chatroom, you need to know IP ``<nIP>`` and port ``<nPort>`` of any node that is already in the chatroom::

   soucevi1_dist_chat -a <IP> -p <port> -n <your name> -na <nIP> -np <nPort>

Logging
^^^^^^^

In both cases you can specify the option ``-v`` that stands for verbose. Without ``-v``, the application logs into file (``chat_<port>.log``). With ``-v`` the application logs to the file as well as to the stdout.

The format of the log message is::

   TS: message

Where ``TS`` is Lamport logical clock timestamp.

Chatting
^^^^^^^^

Once you start the *leader*, you won't be able to do anything until the first connection of another node is made. After that, you get a prompt that looks like this::

   > Name(IP:port): 

Where you can write your message and press Enter to send it. Received message looks simillar::

   > Name(IP:port)[Lamport timestamp]: Hello from Name


To exit the application, instead of your message simply write ``//exit``.

Help
^^^^

For help, run::

   soucevi1_dist_chat --help


Documentation
-------------
You can take a look at the documentation on this `website <https://soucevi1-dist-chat.readthedocs.io/en/latest/>`_.

Or, you can build it using Sphinx::

   $ cd docs
   $ make html

You can replace ``html`` in the command with whatever Sphinx currently supports. Beware that some third party Sphinx extensions might be required (listed in ``docs/requirements.txt``).