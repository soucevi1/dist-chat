.. _ref-tutor:

How To Use The Program
======================
This chapter will show you how to use the chat program.

Installation
------------

First of all, you need to install the program.

The program is uploaded on `PyPI <https://pypi.org/project/soucevi1-dist-chat/>`_, so to get the newest version, just type::

   python -m pip install soucevi1_dist_chat

For any specific version, type::

   python -m pip install soucevi1_dist_chat==<version>

You can also clone and use the `GitHub repository <https://github.com/soucevi1/dist-chat>`_.

Program arguments
-----------------
The program only has a CLI mode so far. You can run it with several arguments:
  * ``-l, --leader``: The node will be started as a leader node
  * ``-a, --address``: IP address of the node
  * ``-p, --port``: TCP port of the node
  * ``-na, --neighbor-address``: In case this node is not a leader, this is the address of the node it will connect to
  * ``-np, --neighbor-port``: In case this node is not a leader, this is the TCP port of the node it will connect to
  * ``-n, --name``: Username that will be displayed at your messages
  * ``-v, --verbose``: Log messages will be printed to ``stdout`` as well as to the log file
  * ``--help``: Display help message on what parameters are and should be used

Chatroom creation
-----------------

The chatroom is created by running the leader node. A chatroom can only have one leader node, so if you already run onw and start another, the other will create a new room.

To create a chatroom with the leader called ``Lojza`` on IP:port ``1.2.3.4:12345`` type the following command::

   soucevi1_dist_chat -l -a 1.2.3.4 -p 12345 -n Lojza

Other nodes
^^^^^^^^^^^

To run another node (user ``Pepa`` on IP:port ``7.8.9.1:45678``) and connect it to the existing chatroom, type::

   soucevi1_dist_chat -n Pepa -a 7.8.9.1 -p 45678 -na 1.2.3.4 -np 12345

The new node will automatically create the ring with the existing leader node. Should you want another node to join the chatroom, the neighbor address and port arguments you can use either the ``Lojza``'s or ``Pepa``'s contact information.

Chatting
--------
Two users, ``Lojza`` and ``Pepa`` are already in the chatroom, so they can chat freely. Right after ``Pepa`` joined, ``Lojza`` (the leader) saw this (verbose mode off)::

   > Lojza(1.2.3.4:12345)[14]: Pepa joined the ring!
   /// Welcome to the dist-chat, you're free to write messages now. ///
   > Lojza(1.2.3.4:12345):

As you can see, at first, ``Lojza`` got an automatically generated message about ``Pepa`` joining in. This is a message that is broadcasted by the leader (that's why there's his name in the message)  every time a new node joins the ring.

Then, there was a welcome message from the program. ``Lojza`` was the only node so far, so he couldn't chat with anyone.

The third line is the prompt. If you type something, it appears next to it.

Now ``Pepa`` wants to greet ``Lojza``, so he writes::

   > Pepa(7.8.9.1:45678): Hi, Lojza!

And then he presses Enter. Lojza (and any other users present in the chatroom) will see a similar thing::

   > Pepa(7.8.9.1:45678)[18]: Hi, Lojza!

As you can see, there is a number in square brackets. It's the logical time of the message being sent. The principles of logical time are explained in :ref:`ref-impl`.

The overall structure of the received user message is::

   > Sender_name(sender_IP, sender_port)[Lamports_time]: message_contents

Exiting the chatroom
--------------------

To exit the chatroom, instead of your message, type ``//exit`` and press Enter::

   > Name(IP:port): //exit

Or you can simply close the terminal window. There is no logout proces, so even if you use the ``//exit`` command, the node will just close. After the node has left, the ring renewal is done just like it is described in :ref:`ref-impl`.

Logging
-------
By default, the program logs only into a file. The file is created in the same directory, where the program is run and its name is ``chat_PORT.log``, where ``PORT`` is the TCP port of the node.

If you run the program with ``-v`` or ``--verbose``, every message that gets logged is also printed on stdout::

   1: Initializing the server

The format is the same as in the log file. In general, the messages look like this::

   Lamports_time: Logged_event_content

Pretty much every action is logged, so the verbose mode is quite messy with all the messages.