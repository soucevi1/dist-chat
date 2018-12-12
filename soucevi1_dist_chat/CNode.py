from soucevi1_dist_chat.CMessage import CMessage, MessageType
import asyncio
import socket
import json


class CNode:
    """
    Class that represents the node -- one participant of the chat.
    """

    def __init__(self, is_leader, port, neighbor_address, neighbor_port, name=''):
        self.name = name
        self.address = '127.0.0.1'
        self.port = port
        self.neighbor_address = neighbor_address
        self.neighbor_port = neighbor_port
        self.logical_clock = 0
        self.is_leader = is_leader
        self.next_node_reader = None
        self.next_node_writer = None
        self.prev_node_reader = None
        self.prev_node_writer = None
        if is_leader:
            self.leader_contact = self.port
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
        :type message: CMessage.CMessage
        """
        ...

    async def run(self):
        """
        Run the node -- the main function of the node.
        """

        print(f'/// Starting node on port: {self.port}')
        loop = asyncio.get_event_loop()
        server_coro = asyncio.create_task(self.server_init())
        while self.next_node_reader is None or self.next_node_writer is None:
            try:
                self.next_node_reader, self.next_node_writer = await asyncio.open_connection(self.neighbor_address,
                                                                                             self.neighbor_port)
            except ConnectionRefusedError:
                pass
        print(f'/// Connection established with {self.neighbor_address}:{self.neighbor_port}')
        socket_coro = asyncio.create_task(self.read_socket(loop))
        input_coro = asyncio.create_task(self.read_input(loop))
        try:
            await socket_coro
            await input_coro
            if socket_coro.cancelled() or socket_coro.done():
                input_coro.cancel()
                server_coro.cancel()
            elif input_coro.cancelled() or input_coro.done():
                socket_coro.cancel()
                server_coro.cancel()
            elif server_coro.cancelled() or server_coro.done():
                input_coro.cancel()
                socket_coro.cancel()
            await server_coro
        except asyncio.CancelledError:
            print('/// Tasks cancelled')

    def set_logical_clock(self, other_clock):
        """
        Synchronize the logical (Lamport) clock of this node.
        :param other_clock: Logical clock of the node it is
        synchronizing with.
        """
        ...

    async def server_init(self):
        server = await asyncio.start_server(self.run_server, self.address, self.port)
        async with server:
            await server.serve_forever()

    async def run_server(self, reader, writer):
        while True:
            data = await reader.read()

            # Previous node died, send message to its previous node so that it can connect
            if data == b'':
                writer.close()
                await writer.wait_closed()
                print('/// Lost connection to previous node')
                self.prev_node_reader = None
                self.prev_node_writer = None
                self.send_prev_inform_message()

            message = CMessage(None, None, None, None, None, data.decode().json())

            # Previous node is dead and this message comes from its previous node
            if message.message_type == MessageType.prev_connect_message:
                self.prev_node_writer = writer
                self.prev_node_reader = reader

            self.handle_message(message)

    async def read_socket(self):
        while True:
            # Next node died, must wait for message telling where to connect
            if self.next_node_writer.is_closing():
                print('/// Waiting for connection...')
                self.next_node_writer = None
                self.next_node_reader = None
                while self.next_node_writer is None or self.next_node_reader is None:
                    await asyncio.sleep(1)

            try:
                data = await self.next_node_reader.read()
            except asyncio.CancelledError:
                continue

            if data == b'':
                self.next_node_writer.close()
                await self.next_node_writer.wait_closed()
                print('/// Lost connection to next node')
                continue

    async def read_input(self, loop):
        while True:
            message = await loop.run_in_executor(None, input)

            if message == '//exit':
                print('Exiting...')
                self.next_node_writer.close()
                await self.next_node_writer.wait_closed()
                return

            umsg = self.craft_user_message(message)
            self.send_user_message(umsg)

    def send_prev_inform_message(self):
        pass

    def craft_user_message(self, user_input):
        message = CMessage(self.address, self.port, self.name, MessageType.user_message, user_input)
        return message

    def send_user_message(self, message):
        pass

