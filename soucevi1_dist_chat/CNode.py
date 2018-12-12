from soucevi1_dist_chat.CMessage import CMessage, MessageType
import asyncio
import socket
import json
import sys
from pprint import pprint


class CNode:
    """
    Class that represents the node -- one participant of the chat.
    """

    def __init__(self, is_leader, port, neighbor_address, neighbor_port, name=''):
        self.name = name
        self.address = '127.0.0.1'
        self.port = port
        self.next_node_address = neighbor_address
        self.next_node_port = neighbor_port
        self.logical_clock = 0
        self.is_leader = is_leader
        self.next_node_reader = None
        self.next_node_writer = None
        self.prev_node_reader = None
        self.prev_node_writer = None
        if is_leader:
            self.leader_address = self.address
            self.leader_port = self.port
        else:
            self.leader_address = None
            self.leader_port = None

    def logout(self):
        """
        Logout from the chatroom. If this node is not the leader,
        let the leader know that this node is leaving. If this node
        is the leader, let other nodes know this node is leaving and start the election.
        """
        ...

    async def handle_message(self, message, reader, writer):
        """
        Decide what to do with received message.
        :param message: Received message to handle
        :param reader: Reader/writer pair of the message sender
        :param writer: Reader/writer pair of the message sender
        :type message: CMessage
        """
        m_type = MessageType(message.message_type)

        # New node wants to log in
        if m_type == MessageType.login_message:
            print(f'/// Received login message from {message.sender_address}:{message.sender_port}')

            # If the node is the leader without other conections
            if self.next_node_port is None or self.next_node_address is None:
                answer = {'next_IP': self.address, 'next_port': self.port,
                          'leader_IP': self.leader_address, 'leader_port': self.leader_port}

            # If the ring already exists
            else:
                answer = {'next_IP': self.next_node_address, 'next_port': self.next_node_port,
                          'leader_IP': self.leader_address, 'leader_port': self.leader_port}
            a = self.craft_message(MessageType.login_message, answer)
            j_answer = a.convert_to_JSON()
            s_answer = json.dumps(j_answer)
            print('/// Sending info to the new node')
            try:
                writer.write(s_answer.encode())
            except ConnectionRefusedError:
                print('/// Critical error while answering to login message')
                sys.exit(1)
            await asyncio.sleep(2)
            print('/// Closing the old connection')
            writer.close()
            await writer.wait_closed()
            self.next_node_port = message.sender_port
            self.next_node_address = message.sender_address
            print('/// Opening new connection')
            try:
                self.next_node_reader, self.next_node_writer = await asyncio.open_connection(self.next_node_address,
                                                                                             self.next_node_port)
            except ConnectionRefusedError:
                print('/// Critical error while connecting to the new next node')
                sys.exit(1)
            print('/// New connection opened')

        # New node informing about itself
        elif m_type == MessageType.i_am_prev_message:
            info = writer.get_extra_info('peername')
            print(f'/// New prev node: {info}')
            self.prev_node_writer.close()
            await self.prev_node_writer.wait_closed()
            self.prev_node_reader = reader
            self.prev_node_writer = writer

        # Previous node is dead and this message comes from its previous node
        elif m_type == MessageType.prev_connect_message:
            info = writer.get_extra_info('peername')
            print(f'/// New prev node: {info}')
            self.prev_node_writer = writer
            self.prev_node_reader = reader

        print(f'/// Unknown message type: {m_type}')

    async def run(self):
        """
        The main function of the node.
        Opens connection to the given node, which helps to connect this node into the ring.
        Starts 3 coroutines: one is reading the user input, one is watching the open connection
        and one is listening to incoming connections.
        """

        print(f'/// Starting node on port: {self.port}')
        loop = asyncio.get_event_loop()
        server_coro = asyncio.create_task(self.server_init())

        # If node is the leader, it just needs to wait for a connection
        if self.is_leader:
            while True:
                if self.next_node_writer is not None and self.next_node_reader is not None:
                    print('/// New connection, wake up')
                    break
                await asyncio.sleep(0.1)

        # If node is not the leader, it can open the connection
        else:
            try:
                self.next_node_reader, self.next_node_writer = await asyncio.open_connection(self.next_node_address,
                                                                                             self.next_node_port)
            except ConnectionRefusedError:
                print('/// Invalid IP or port passed in argument')
                sys.exit(1)
            print(f'/// Initial connection established with {self.next_node_address}:{self.next_node_port}')
            await self.join_the_ring()
            print('/// Ring joined')

        socket_coro = asyncio.create_task(self.read_socket())
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

    async def join_the_ring(self):
        """
        Send message to the open connection to join the ring.
        The open connection becomes the previous node. The previous node sends a message
        with information about its next node, that is to become this node's next node.
        """

        print('/// Joining the ring')
        # Send login message to given node
        data = {}
        message = self.craft_message(MessageType.login_message, data)
        print('/// Sending login message')
        try:
            await self.send_message_to_ring(message)
        except ConnectionRefusedError:
            print('Critical ring error')
            sys.exit(1)

        # Wait or the answer, close the connection to the node
        print('/// Waiting for the answer to login message')
        answer_raw = await self.next_node_reader.read()
        answer = answer_raw.decode()
        m_amswer = CMessage(None, None, None, None, None, json.loads(answer))
        answer_data = m_amswer.message_data
        self.next_node_writer.close()
        await self.next_node_writer.wait_closed()
        print('/// Closed old connection')

        # The answer contains IP and port of the new next node.
        self.next_node_address = answer_data['next_IP']
        self.next_node_port = answer_data['next_port']
        self.leader_address = answer_data['leader_IP']
        self.leader_port = answer_data['leader_port']

        print('/// Opening the new connection')
        self.next_node_reader, self.next_node_writer = await asyncio.open_connection(self.next_node_address,
                                                                                     self.next_node_port)
        m = self.craft_message(MessageType.i_am_prev_message, {})
        await self.send_message_to_ring(m)

    def set_logical_clock(self, other_clock):
        """
        Synchronize the logical (Lamport) clock of this node.
        :param other_clock: Logical clock of the node it is
        synchronizing with.
        """
        ...

    async def server_init(self):
        print('/// Initializing the server')
        server = await asyncio.start_server(self.run_server, self.address, self.port)
        async with server:
            await server.serve_forever()

    async def run_server(self, reader, writer):
        while True:
            data = await reader.read(10000)

            if writer.is_closing():
                continue

            # Previous node died, send message to its previous node so that it can connect
            if data == b'':
                writer.close()
                await writer.wait_closed()
                print('/// Lost connection to previous node')
                self.prev_node_reader = None
                self.prev_node_writer = None
                await self.send_prev_inform_message()
                continue

            s_message = data.decode()
            print(f'smessage: {s_message}')
            j_message = json.loads(s_message)
            print(f'jmessage: {j_message}')

            message = CMessage(None, None, None, None, None, j_message)

            if self.is_leader and self.prev_node_writer is None:
                self.prev_node_writer = writer
                self.prev_node_reader = reader

            print('/// Handling the message')
            await self.handle_message(message, reader, writer)
            print('/// Message handled')

    async def read_socket(self):
        while True:
            # Next node is dead, must wait for message telling where to connect
            if self.next_node_writer.is_closing():
                print('/// Waiting for connection...')
                self.next_node_writer = None
                self.next_node_reader = None
                while self.next_node_writer is None or self.next_node_reader is None:
                    await asyncio.sleep(1)

            # Wait for some data to come. The only data to come through
            # this stream should be b'' in case of the next node's death.
            try:
                data = await self.next_node_reader.read()
            except asyncio.CancelledError:
                continue

            # Next node just died, close the connection
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

            umsg = self.craft_message(MessageType.user_message, message)
            self.send_user_message(umsg)

    def craft_message(self, m_type, data):
        message = CMessage(self.address, self.port, self.name, m_type, data)
        return message

    def send_user_message(self, message):
        pass

    async def send_prev_inform_message(self):
        data = {'new_next_IP': self.address, 'new_next_port': self.port}
        message = self.craft_message(MessageType.prev_inform_message, data)
        await self.send_message_to_ring(message)

    async def send_message_to_ring(self, message):
        j_message = message.convert_to_JSON()
        s_message = json.dumps(j_message)
        try:
            self.next_node_writer.write(s_message.encode())
            await self.next_node_writer.drain()
        except ConnectionRefusedError:
            print(f'Connection refused while sending: {s_message}')


