from soucevi1_dist_chat.CMessage import CMessage, MessageType
import asyncio
import sys
import logging
from soucevi1_dist_chat.colors import Colors
from prompt_toolkit import prompt
from prompt_toolkit.eventloop.defaults import use_asyncio_event_loop
from prompt_toolkit.patch_stdout import patch_stdout


class CNode:
    """
    Class that represents the node -- one participant of the chat.
    """

    def __init__(self, is_leader, address, port, neighbor_address, neighbor_port, name=''):
        self.name = name
        self.address = address
        self.port = port
        self.next_node_address = neighbor_address
        self.next_node_port = neighbor_port
        self.logical_clock = 0
        self.is_leader = is_leader
        self.next_node_reader = None
        self.next_node_writer = None
        self.prev_node_reader = None
        self.prev_node_writer = None
        self.leader_reader = None
        self.leader_writer = None
        self.exiting = False
        self.connections = []
        self.voting = False
        self.initiate = False
        if is_leader:
            self.leader_address = self.address
            self.leader_port = self.port
        else:
            self.leader_address = None
            self.leader_port = None

    async def handle_message(self, message, reader, writer):
        """
        Decide what to do with received message.
        :param message: Received message to handle
        :param reader: Reader/writer pair of the message sender
        :param writer: Reader/writer pair of the message sender
        :type message: CMessage
        """
        m_type = MessageType(message.message_type)
        sender = message.sender_address, message.sender_port

        self.set_logical_clock(message.time)

        # New node wants to log in
        if m_type == MessageType.login_message:

            logging.info(f'{self.logical_clock}: Received login message from {sender}')
            await self.handle_login_message(message, writer)

        # New node informing about itself
        elif m_type == MessageType.i_am_prev_message:

            logging.info(f'{self.logical_clock}: Received i am prev message from {sender}')
            await self.handle_i_am_prev_message(reader, writer)

        # Prev node died, inform its prev where to connect
        elif m_type == MessageType.prev_inform_message:

            logging.info(f'{self.logical_clock}: Received prev inform message from {sender}')
            await self.handle_prev_inform_message(message)

        # Another user writes a message
        elif m_type == MessageType.user_message:

            await self.handle_user_message(message, reader)

        elif m_type == MessageType.hello_leader_message:

            await self.handle_hello_leader_message(message, reader, writer)

        elif m_type == MessageType.election_message:

            logging.info(f'{self.logical_clock}: Received election message from {sender}')
            await self.handle_election_message(message)

        elif m_type == MessageType.elected_message:

            logging.info(f'{self.logical_clock}: Received elected message from {sender}')
            await self.handle_elected_message(message)

        else:

            logging.error(f'{self.logical_clock} Received unknown message type: {m_type}')

    async def handle_elected_message(self, message):
        """
        When received elected_message, it means the new leader is known already.
        This message should run around the circle until it comes to the sender
        (leader) again. All non-leader nodes should connect to the leader.
        :param message: CMessage with new leader information
        """
        self.leader_address = message.message_data['addr']
        self.leader_port = message.message_data['port']
        self.voting = False

        logging.info(f'{self.logical_clock}: New leader is {self.leader_address}:{self.leader_port}')

        sender_id = str(message.message_data['addr'] + str(message.message_data['port']))
        self_id = str(self.address) + str(self.port)

        if sender_id != self_id:
            logging.info(f'{self.logical_clock}: Passing elected message on...')
            await self.send_message_to_ring(message)

        if not self.is_leader:
            await self.connect_to_leader()

    async def handle_election_message(self, message):
        """
        Election messages are the main communication during the
        Chang-Roberts algorithm. The node with the biggest ID
        (concatenated string "IP+port") will become the next leader.
        This coroutine is the main body of the Chang-Roberts algorithm.
        :param message: Election CMessage from the previous node
        """
        sender_id = str(message.message_data['addr']) + str(message.message_data['port'])
        self_id = str(self.address) + str(self.port)

        if sender_id > self_id:

            # If the sender of the message as bigger ID, he's the candidate.
            logging.info(f'{self.logical_clock}: Passing election message on...')
            await self.send_message_to_ring(message)
            self.voting = True

        elif sender_id < self_id and not self.voting:

            # If this node has bigger ID, he's the candidate.
            logging.info(f'{self.logical_clock}: I am the new leader candidate')
            m = self.craft_message(MessageType.election_message, {'addr': self.address, 'port': self.port})
            await self.send_message_to_ring(m)
            self.voting = True

        elif sender_id == self_id:

            # If the message arrived with this node's ID, he won the election.
            logging.info(f'{self.logical_clock}: Received election message with my number -- NEW LEADER')
            m = self.craft_message(MessageType.elected_message, {'addr': self.address, 'port': self.port})
            self.is_leader = True
            await self.send_message_to_ring(m)

    async def handle_hello_leader_message(self, message, reader, writer):
        """
        New node registers to the message broadcast.
        :param message:
        :param reader:
        :param writer:
        """
        if self.find_in_connections(reader):
            # Connection already exists
            logging.error(f'{self.logical_clock}: Hello leader received from known node!')
            return
        logging.info(f'{self.logical_clock}: Adding {message.sender_address}:'
                     f'{message.sender_port} to the broadcast list')
        await self.add_connection_record(message, reader)
        logging.info(f'{self.logical_clock}: Number of connections: {len(self.connections)}')
        await self.send_hello_from_leader(message)

    async def send_hello_from_leader(self, message):
        """
        The leader node distributes a message telling everyone in
        the ring (except the new node) that a new node joined.
        :param message: Original hello message
        """
        m = self.craft_message(MessageType.user_message, f'{message.sender_name} joined the ring!')

        # The leader user needs to be told about the new node too...
        self.print_user_message(m)

        await self.distribute_message(m)

    async def handle_user_message(self, message, reader):
        """
        The node received the user message.
        If it it not a leader node, it just displays the message
        to the console.
        If it is a leader, it must distribute the message to all the
        nodes in the ring.
        :param message: User message to handle
        :param reader: Stream reader
        """
        self.print_user_message(message)
        if self.is_leader:
            if not self.find_in_connections(reader):
                logging.error(f'{self.logical_clock}: Received user message from unknown node')
                await self.add_connection_record(message, reader)
            await self.distribute_message(message)

    def print_user_message(self, message):
        """
        Print received user message.
        :param message: CMessage to be printed.
        """
        print(Colors.BOLD + Colors.CYAN + f'> {message.sender_name}' + Colors.RESET +
              f'({message.sender_port})' + Colors.GREEN + f'[{message.time}]: '
              + Colors.RESET + f'{message.message_data}')

    async def add_connection_record(self, message, reader):
        """
        Add new connection to the broadcasting list.
        :param message: Received user message
        :param reader: Stream reader
        """
        conn = {
            'addr': message.sender_address,
            'port': message.sender_port,
            'reader': reader,
        }
        try:
            _, conn['writer'] = await asyncio.open_connection(message.sender_address, message.sender_port)
        except ConnectionError:
            logging.error(f'{self.logical_clock}: Cannot open backwards connection to client')
            return
        self.connections.append(conn)

    def find_in_connections(self, reader):
        """
        Find if there is a record of the connection
        represented by the given stream writer.
        :param reader: Stream writer
        :return: True if writer is in connections, False otherwise.
        """
        for c in self.connections:
            if c['reader'] == reader:
                return True
        return False

    async def distribute_message(self, message, exc=None):
        """
        Distribute message to all known nodes.
        :param message: User message
        :param exc: Exception in distribution: IP and port of a node that will not receive the message
        """
        for conn in self.connections:

            # Do not send the message back to the sender
            if conn['addr'] == message.sender_address and conn['port'] == message.sender_port:
                continue

            if exc and conn['addr'] == exc[0] and conn['port'] == exc[1]:
                continue

            try:

                logging.info(f'{self.logical_clock}: Distribution to: {conn["addr"]}:{conn["port"]}')
                conn['writer'].write(message.convert_to_string().encode())
                await conn['writer'].drain()

            except ConnectionError:

                logging.error(f'{self.logical_clock}: {conn["addr"]}:{conn["port"]} not reachable to broadcast')
                self.remove_from_connections(conn['reader'], conn['writer'])

    async def handle_prev_inform_message(self, message):
        """
        A node died. Its next node detects it and sends
        a message to the ring. If this node's next is dead,
        its new next node is the sender of the message.
        :param message: Message to handle
        """
        # Pass the message on if this node's next is alive.
        if self.next_node_writer is not None:
            logging.info(f'{self.logical_clock}: Passed prev inform message on...')
            await self.send_message_to_ring(message)
            return

        # Update new next node and address.
        self.next_node_reader, self.next_node_writer = await asyncio.open_connection(message.sender_address,
                                                                                     message.sender_port)
        self.next_node_address = message.sender_address
        self.next_node_port = message.sender_port

        logging.info(f'{self.logical_clock}: Opened new connection to {message.sender_address}:{message.sender_port}')

        # Inform the new next about the connection,
        # so that it can update the prev streams.
        m = self.craft_message(MessageType.i_am_prev_message, {})
        await self.send_message_to_ring(m)
        logging.info(f'{self.logical_clock}: Ring renewed')
        if self.initiate:
            await self.initiate_election()

    async def handle_i_am_prev_message(self, reader, writer):
        """
        The previous node of the current node has changed
        and it's informing this node about being its new prev,
        so it can update the instance streams.
        :param reader: Stream reader of the new previous node
        :param writer: Stream writer of the new previous node
        """
        # There is still an active connection to the old previous node
        if self.prev_node_writer is not None and not self.prev_node_writer.is_closing():

            self.prev_node_writer.close()
            logging.info(f'{self.logical_clock}: Closing the old prev')
            await self.prev_node_writer.wait_closed()

        # Update the instance streams
        self.prev_node_reader = reader
        self.prev_node_writer = writer

    async def handle_login_message(self, message, writer):
        """
        A new node wants to log in. Make the new node this
        node's next and tell it where to connect (its next
        is this node's old next).
        :param message: Login message to handle
        :param writer: Writer stream of the new node
        """

        # If the node is the leader without other conections
        if self.next_node_port is None or self.next_node_address is None:

            answer = {
                      'next_IP': self.address,
                      'next_port': self.port,
                      'leader_IP': self.leader_address,
                      'leader_port': self.leader_port
                      }

        # If the ring already exists
        else:

            answer = {
                      'next_IP': self.next_node_address,
                      'next_port': self.next_node_port,
                      'leader_IP': self.leader_address,
                      'leader_port': self.leader_port
                      }

        a = self.craft_message(MessageType.login_message, answer)
        s_answer = a.convert_to_string()

        try:

            logging.info(f'{self.logical_clock}: Sending info to the new node')
            writer.write(s_answer.encode())
            await writer.drain()

        except ConnectionRefusedError:

            logging.critical(f'{self.logical_clock}: Critical error while answering to login message')
            sys.exit(1)

        self.next_node_port = message.sender_port
        self.next_node_address = message.sender_address

        try:

            logging.info(f'{self.logical_clock}: Opening connection to new next')
            self.next_node_reader, self.next_node_writer = await asyncio.open_connection(self.next_node_address,
                                                                                         self.next_node_port)

        except ConnectionRefusedError:

            logging.critical(f'{self.logical_clock}: Critical error while connecting to the new next node')
            sys.exit(1)

        logging.info(f'{self.logical_clock}: New connection opened, next node is:'
                     f' {self.next_node_address}:{self.next_node_port}')

        logging.info(f'{self.logical_clock}: Informing next about being its prev')
        m = self.craft_message(MessageType.i_am_prev_message, {})
        await self.send_message_to_ring(m)

        logging.info(f'{self.logical_clock}: Closing the old connection')
        writer.close()
        await writer.wait_closed()

    async def run(self):
        """
        The main function of the node.
        Opens connection to the given node, which helps to connect this node into the ring.
        Starts 3 coroutines: one is reading the user input, one is watching the open connection
        and one is listening to incoming connections.
        """

        logging.info(f'{self.logical_clock}: Starting node on port: {self.port}')
        server_coro = asyncio.create_task(self.server_init())

        # If node is the leader, it just needs to wait for a connection
        if self.is_leader:

            await self.wait_for_connection()

        # If node is not the leader, it can open the connection
        else:

            try:

                self.next_node_reader, self.next_node_writer = await asyncio.open_connection(self.next_node_address,
                                                                                             self.next_node_port)
            except ConnectionRefusedError:

                logging.critical(f'{self.logical_clock}: Invalid IP or port passed in argument')
                sys.exit(1)

            logging.info(f'{self.logical_clock} Initial connection established with ' 
                         f'{self.next_node_address}:{self.next_node_port}')
            await self.join_the_ring()
            logging.info(f'{self.logical_clock}: Ring joined')

        logging.info(f'{self.logical_clock}: Initialize socket reading')
        socket_coro = asyncio.create_task(self.read_socket())
        logging.info(f'{self.logical_clock} Initialize input reading')
        input_coro = asyncio.create_task(self.read_input())

        print(Colors.GREEN + "/// Welcome to the dist-chat, you're free to write messages now. ///" + Colors.RESET)

        try:

            await input_coro

            # Wait for the input_coro to end (= user wants to exit)
            # and cancel all the remaining running tasks.
            if input_coro.cancelled() or input_coro.done():
                socket_coro.cancel()
                server_coro.cancel()

            await socket_coro
            await server_coro

        except asyncio.CancelledError:
            logging.info(f'{self.logical_clock}: All tasks cancelled')

    async def wait_for_connection(self):
        """
        The leader is alone and must wait for the first connection
        is order to continue creating the ring.
        """
        while True:

            # Try if already connected
            if self.next_node_reader is not None:
                logging.info(f'{self.logical_clock}: First connection - waking up...')
                break

            # Not connected -- pass the execution for a while
            await asyncio.sleep(0.1)

    async def join_the_ring(self):
        """
        Send message to the open connection to join the ring.
        The open connection becomes the previous node. The previous node sends a message
        with information about its next node, that is to become this node's next node.
        """

        logging.info(f'{self.logical_clock}: Joining the ring')

        # Send login message to given node.
        message = self.craft_message(MessageType.login_message, {})
        logging.info(f'{self.logical_clock}: Sending login message')
        try:
            await self.send_message_to_ring(message)
        except ConnectionRefusedError:
            logging.critical(f'{self.logical_clock}: Critical ring error')
            sys.exit(1)

        # Wait for the answer, close the current
        # connection to the node.
        logging.info(f'{self.logical_clock}: Waiting for the answer to login message')
        answer_raw = await self.next_node_reader.read()
        answer = answer_raw.decode()
        m_answer = CMessage(message_str=answer)
        answer_data = m_answer.message_data
        self.set_logical_clock(m_answer.time)

        # Save the old writer to close it in the end.
        old_w = self.next_node_writer

        # The answer contains IP and port
        # of the new next node and the leader.
        self.next_node_address = answer_data['next_IP']
        self.next_node_port = answer_data['next_port']
        self.leader_address = answer_data['leader_IP']
        self.leader_port = answer_data['leader_port']

        logging.info(f'{self.logical_clock}: Next node is {self.next_node_address}:{self.next_node_port}')

        # Open new connection to the node whose
        # address and port were in the answer.
        logging.info(f'{self.logical_clock}: Opening the new connection')
        try:
            self.next_node_reader, self.next_node_writer = await asyncio.open_connection(self.next_node_address,
                                                                                         self.next_node_port)
        except ConnectionError:
            logging.error(f'{self.logical_clock}: Connection to the next node cannot be opened')
            sys.exit(1)

        # Close the old connection now.
        old_w.close()
        await old_w.wait_closed()
        logging.info(f'{self.logical_clock}: Closed old connection')

        # Inform next node to change its prev
        m = self.craft_message(MessageType.i_am_prev_message, {})
        logging.info(f'{self.logical_clock}: Informing new next node')
        await self.send_message_to_ring(m)

        await self.connect_to_leader()

    async def connect_to_leader(self):
        # Connect to the leader and send him a hello
        logging.info(f'{self.logical_clock}: Connecting to leader: {self.leader_address}:{self.leader_port}')
        try:
            self.leader_reader, self.leader_writer = await asyncio.open_connection(self.leader_address,
                                                                                   self.leader_port)
        except ConnectionError:
            logging.error(f'{self.logical_clock}: Connection to the leader cannot be opened')
            sys.exit(1)
        except asyncio.CancelledError:
            logging.error(f'{self.logical_clock}: CancelledError')
            sys.exit(1)

        m = self.craft_message(MessageType.hello_leader_message, {})
        await self.send_message_to_leader(m)

    def set_logical_clock(self, other_clock):
        """
        Synchronize the logical (Lamport) clock of this node.
        :param other_clock: Logical clock of the node it is
        synchronizing with.
        """
        self.logical_clock = max(self.logical_clock, other_clock) + 1

    async def server_init(self):
        """
        Initialize the server coroutine, make it run forever.
        """
        logging.info(f'{self.logical_clock}: Initializing the server')
        server = await asyncio.start_server(self.run_server, self.address, self.port)
        async with server:
            await server.serve_forever()

    async def run_server(self, reader, writer):
        """
        Callback made whenever a connection with the server is made.
        Try to read some data.
        If the writer is closing, return (callback ends, there is nothing else to do).
        If the received data is empty, and this node is exiting, return.
        If the data is empty and the prev reader is not the current reader,
        return (the previous node must have changed).
        Otherwise if the data is empty, close the connection, set the prev streams to none
        and inform the dead previous' previous node where to connect.
        If the data is OK, create a CMessage instance out of them and handle the message.
        :param reader: AsyncIO StreamReader, high level socket for receiving data from the connection.
        :param writer: ASyncIO StreamWriter, high level socket for sending data through the connection.
        """
        while True:

            # Read the data from the connection.
            data = await reader.read(10000)

            # If the connection is closed/ing,
            # end the callback.
            if writer.is_closing():
                return

            # Previous node died, send message to its
            # previous node so that it can connect.
            if data == b'':

                if writer != self.prev_node_writer:

                    # Other than prev died, remove it from the connection list
                    if self.is_leader:
                        self.remove_from_connections(reader, writer)
                    return

                if self.exiting:
                    return

                writer.close()
                await writer.wait_closed()
                logging.info(f'{self.logical_clock}: Lost connection to previous node')
                self.prev_node_reader = None
                self.prev_node_writer = None
                await asyncio.sleep(0.5)
                if self.next_node_writer is not None:
                    logging.info(f'{self.logical_clock}: Informing the new prev')
                    await self.send_prev_inform_message()
                else:
                    logging.info(f'{self.logical_clock}: Left alone, became the leader')
                    self.is_leader = True
                    self.leader_address = self.address
                    self.leader_port = self.port
                return

            message = CMessage(message_str=data.decode())

            await self.handle_message(message, reader, writer)

    def remove_from_connections(self, reader, writer):
        """
        Remove the connection represented by streams in argument
        form the leader connections list.
        :param reader: Stream reader of the removed connection
        :param writer: Stream writer of the removed connection
        """
        for c in self.connections:
            if c['reader'] == reader and c['writer'] == writer:
                self.connections.remove(c)
                return

    async def read_socket(self):
        """
        Coroutine keeping the connection to the next node alive.
        No data is expected except for when the next node dies.
        """

        # Flag is there to give the writer another change if the connection seems
        # to be lost. During the various reconnections while logging in a new node
        # it sometimes looked disconnected (probably a race condition).
        flag = True

        while True:

            # Next node is dead, must wait for message telling where to connect
            if self.next_node_writer.is_closing():

                logging.info(f'{self.logical_clock}: Waiting for connection...')
                self.next_node_writer = None
                self.next_node_reader = None
                self.next_node_address = None
                self.next_node_port = None

                while self.next_node_writer is None or self.next_node_reader is None:
                    await asyncio.sleep(0.1)

                flag = True
                continue

            # Wait for some data to come. The only data to come through
            # this stream should be b'' in case of the next node's death.
            try:

                data = await self.next_node_reader.read()

            except (asyncio.CancelledError, ConnectionError) as e:

                logging.info(f'{self.logical_clock}: Waiting for connection to the next node...')
                self.next_node_writer = None
                self.next_node_reader = None
                self.next_node_address = None
                self.next_node_port = None

                while self.next_node_writer is None or self.next_node_reader is None:
                    await asyncio.sleep(0.1)

                flag = True
                continue

            # Next node just died, close the connection
            if data == b'':

                if self.exiting:
                    return

                # If there is a second chance, wait and repeat the reading.
                if flag:

                    await asyncio.sleep(0.3)
                    flag = False
                    continue

                self.next_node_writer.close()
                await self.next_node_writer.wait_closed()
                logging.info(f'{self.logical_clock}: Lost connection to next node')
                if self.next_node_address == self.leader_address and self.next_node_port == self.leader_port:
                    self.initiate = True

            flag = True

    async def read_input(self):
        """
        Coroutine reading the user's keyboard input and
        transforming it into the CMessage.
        If '//exit' is read here, the program exits.
        """
        use_asyncio_event_loop()

        while True:

            with patch_stdout():
                message = await prompt(f'> {self.name}({self.port}): ', async_=True)

            if message == '//exit':

                logging.info(f'{self.logical_clock}: Exiting...')
                self.exiting = True

                if self.next_node_writer is not None:
                    self.next_node_writer.close()
                    await self.next_node_writer.wait_closed()

                return

            umsg = self.craft_message(MessageType.user_message, message)
            await self.send_user_message(umsg)

    def craft_message(self, m_type, data):
        """
        Create CMessage instance with information about
        the sender (current node), given type and body.
        First, logical clock needs to be incremented.
        :param m_type: Type of the message
        :type m_type: MessageType
        :param data: Main body of the message.
        :return: CMessage instance
        """
        self.logical_clock = self.logical_clock + 1
        message = CMessage(sender_address=self.address, sender_port=self.port, sender_name=self.name,
                           message_type=m_type, message_data=data, time=self.logical_clock)
        return message

    async def send_user_message(self, message):
        """
        Send user input as a message to the leader node.
        :param message: CMessage made from the user input.
        """
        if not self.is_leader:
            logging.info(f'{self.logical_clock}: Sending mesage to leader')
            await self.send_message_to_leader(message)
        else:
            logging.info(f'{self.logical_clock}: No need to send user message, distributing')
            await self.distribute_message(message)

    async def send_prev_inform_message(self):
        """
        Inform the node whose next is dead to connect to this node.
        """
        data = {'new_next_IP': self.address, 'new_next_port': self.port}
        message = self.craft_message(MessageType.prev_inform_message, data)
        await self.send_message_to_ring(message)

    async def send_message_to_ring(self, message):
        """
        Send given message to the next node in the ring.
        :param message: CMessage to be sent
        """
        m = message.convert_to_string()
        try:
            self.next_node_writer.write(m.encode())
            await self.next_node_writer.drain()
        except ConnectionRefusedError:
            logging.error(f'{self.logical_clock}: Connection refused while sending: {m}')

    async def send_message_to_leader(self, message):
        """
        Send given message directly to the leader node.
        :param message: CMessage to be sent
        """
        m = message.convert_to_string()
        try:
            self.leader_writer.write(m.encode())
            await self.leader_writer.drain()
        except ConnectionError:
            logging.error(f'{self.logical_clock}: Error - Connection to the leader')

    async def initiate_election(self):
        """
        After the death of the leader, the ring must be renewed at first.
        After the ring is renewed, the node who was previous to the leader
        initiates the election algorithm.
        """
        self.voting = True
        m = self.craft_message(MessageType.election_message, {'addr': self.address, 'port': self.port})
        await self.send_message_to_ring(m)



