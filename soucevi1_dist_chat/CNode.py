from sortedcontainers import SortedList
from soucevi1_dist_chat import CServer, CClient, CMessage


class CNode:
    """
    Class that represents the node -- one participant of the chat.
    """

    def __init__(self, is_leader, port, name=''):
        self.name = name
        self.address = self.get_IP_address()
        self.port = port
        self.neighbours = SortedList()
        self.logical_clock = 0
        self.is_leader = is_leader
        self.server = CServer.CServer()
        self.client = CClient.CClient()
        if is_leader:
            self.leader_contact = self.address, self.port
        else:
            self.leader_contact = None, None

    def login(self, node_to_contact):
        """
        Login to the chat room. This node contacts the other node
        (whose address and port are passed) as a parameter. The other
        node provides either the contact information about the leader,
        or responds with the information about the chatroom
        (in case is the leader itself).
        :param node_to_contact: IP address and port of any node from the chatroom
        that this node wants to join
        :type node_to_contact: tuple (IP, port)
        """
        ...

    def logout(self):
        """
        Logout from the chatroom. If this node is not the leader,
        let the leader know that this node is leaving. If this node
        is the leader, let other nodes know this node is leaving and start the election.
        """
        ...

    def handle_message(self, message):
        """
        Decide what to do with received message.
        :param message: Received message to handle
        :type message: CMessage
        """
        ...

    def run(self):
        """
        Run the node -- the main function of the node.
        """

        # nekonecny cyklus, kde se bude poslouchat uzivateluv vstup a zaroven server na prichozi zpravy

        ...

    def get_IP_address(self):
        """
        Get IP address of machine this node is running on.
        :return: IP address of the machine
        :rtype: string
        """
        ...

    def set_logical_clock(self, other_clock):
        """
        Synchronize the logical (Lamport) clock of this node.
        :param other_clock: Logical clock of the node it is
        synchronizing with.
        """
        ...
