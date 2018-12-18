from enum import Enum
import json


class MessageType(Enum):
    """
    Class wrapping the types of messages used in the program
    * user_message: chat message sent by another user
    * election_message: message used during the elections
    * login_message: message sent by the node that wants to log in
    * prev_inform_message: previous node is dead, inform its previous node about address and port to connect to
    * i_am_prev_message: message sent by new prev node to its next node
    * hello_leader_message: let the leader know about new node
    * elected_message: leader is already elected
    """
    user_message = 1
    login_message = 2
    prev_inform_message = 3
    i_am_prev_message = 4
    hello_leader_message = 5
    election_message = 6
    elected_message = 7


class CMessage:
    """
    Class representing a single instance of a message that is sent
    during chatting or inside mechanisms of the program.
    """

    def __init__(self, **kwargs):
        """
        This concstructor serves as two constructors in fact.
        First is a constructor creating the instance in a common way
        using given parameters.
        Second is a constructor that creates the message from received JSON.
        :param sender_address: IP address of the sender of the message
        :param sender_port: Port of the sender of the message
        :param sender_name: Name of the sender of the message
        :param message_type: Type of the message
        :param message_data: Data carried by the message, the main body
        :param message_json: JSON received by the server
        :param message_str: same as JSON, in string format
        """
        if 'message_json' in kwargs:
            self.from_json(kwargs['message_json'])
        elif 'sender_address' in kwargs:
            self.sender_address = kwargs['sender_address']
            self.sender_port = kwargs['sender_port']
            self.sender_name = kwargs['sender_name']
            self.message_data = kwargs['message_data']
            self.time = kwargs['time']
            if type(kwargs['message_type']) == int:
                self.message_type = kwargs['message_type']
            else:
                self.message_type = kwargs['message_type'].value
        elif 'message_str' in kwargs:
            self.from_string(kwargs['message_str'])

    def convert_to_json(self):
        """
        Convert message to JSON.
        :return: Message in the JSON format
        """
        d = {'s_addr': self.sender_address,
             's_port': self.sender_port,
             's_name': self.sender_name,
             'data': self.message_data,
             'time': self.time}

        if type(self.message_type) == int:
            d['m_type'] = self.message_type
        else:
            d['m_type'] = self.message_type.value

        j = json.dumps(d)
        return json.loads(j)

    def convert_to_string(self):
        """
        Convert message to string
        :return: Message JSON in string format
        """
        d = {'s_addr': self.sender_address,
             's_port': self.sender_port,
             's_name': self.sender_name,
             'data': self.message_data,
             'time': self.time}

        if type(self.message_type) == int:
            d['m_type'] = self.message_type
        else:
            d['m_type'] = self.message_type.value

        j = json.dumps(d)
        return j

    def from_json(self, received_json):
        """
        Convert JSON to the CMessage class.
        :param received_json: JSON by the server
        """
        self.sender_address = received_json['s_addr']
        self.sender_port = received_json['s_port']
        self.sender_name = received_json['s_name']
        self.message_data = received_json['data']
        self.time = received_json['time']
        if type(received_json['m_type']) == int:
            self.message_type = received_json['m_type']
        else:
            self.message_type = received_json['m_type'].value

    def from_string(self, str):
        """
        Convert string to CMessage.
        :param str: JSON in string format
        :return:
        """
        j = json.loads(str)
        self.from_json(j)

    def print(self):
        """
        Print the message together with its info.
        """
        print(f'Sender: {self.sender_address}:{self.sender_port}')
        print(f'Name: {self.sender_name}')
        print(f'Type: {self.message_type} ({MessageType(self.message_type)})')
        print(f'Data: {self.message_data}')
        print(f'Time: {self.time}')
