
class CServer:
    """
    Class that represents the server-side of the node.
    """

    def __init__(self):
        ...

    def handle_message(self, message):
        """
        Handle given received message passed from the CNode.
        :param message: Message to handle.
        :type message: CMessage
        """
        ...

    def broadcast_message(self, message, nodes):
        """
        Send the provided message to all nodes in the provided list.
        :param message: Message to broadcast
        :type message: CMessage
        :param nodes: Nodes to send the message to
        :type nodes: SortedList
        """
        ...

    def send_message(self, message, node):
        """
        Send message to node.
        :param message: Message to send
        :type message: CMessage
        :param node: IP and port of the node
        :type node: tulpe
        """
        ...
