
API documentation
=================

Here you can take a look at the code documentation.

There are only a few basic modules of the chat: ``cli``, ``CNode`` and ``CMessage``

The ``cli`` module provides all functions managing the command-line interface.

The ``CNode`` module is the main module. The class represents one node present in the chatroom.

The ``CMessage`` module represents the message that is sent between the nodes during the execution.

Important Note
--------------
If you are browsing this documentation on ReadTheDocs, the API documentation probably won't show.

This is caused by ReadTheDocs only supporting Python 3.5 so far -- from their point of view this project is full of syntax errors (f-strings, new AsyncIO expressions... ). The docs won't build with syntax errors in the code.

If you want to see the API documentation, please clone the `GitHub repository <https://github.com/soucevi1/dist-chat>`_ and run::

   $ cd cloned_project/docs
   $ make html

These commands will result in HTML documentation being generated in ``cloned_project/docs/_build/html``, from where you can open it in your browser.

Instead of HTML you can of course generate any other format supported by Sphinx.


Index of documented modules
---------------------------

.. toctree::
   :maxdepth: 4

   soucevi1_dist_chat
