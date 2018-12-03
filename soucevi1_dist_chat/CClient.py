
class CClient:

    def __init__(self):
        ...

    def handle_message(self, message):
        """
        Handle received message passed from the CNode.
        :param message: Message to handle
        :type message: CMessage
        """
        ...

    def show_message(self, message):
        """
        Print the received message on the stdout.
        :param message: Message to print
        :type message: CMessage
        """
        ...

    def send_to_leader(self, message, leader):
        """
        Send the message to the leader node.
        :param message: Message to send
        :type message: CMessage
        :param leader: Leader node
        """
        ...
