from enum import Enum


class MessageType(Enum):
    """
    Class wrapping the types of messages used in the program
    * user_message: chat message sent by another user
    * election_message: message used during the elections
    * login_message: message sent by the node that wants to log in
    * leader_info_message: message sent as a response to login_message
                         by the node that is not a leader, contains
                         information about the leader node
    * info_message: message sent as a response to login_message by the leader node,
                  contains information about the chatroom
    * logout_message: message sent if a non-leader node want to log out
    * logout_election_message: message sent if a leader wants to log out, initiates election
    * new_message: message created from the user input, to be sent to the leader
    """
    user_message = 1
    election_message = 2
    login_message = 3
    leader_info_message = 4
    info_message = 5
    logout_message = 6
    logout_election_message = 7
    new_message = 8


class CMessage:
    """
    Class representing a single instance of a message that is sent
    during chatting or inside mechanisms of the program.
    """

    def __init__(self, sender_address, sender_port, sender_name,
                 message_type, message_data, message_json=None):
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
        """
        if message_json is not None:
            self.JSON_to_message(message_json)
        else:
            self.sender_address = sender_address
            self.sender_port = sender_port
            self.sender_name = sender_name
            self.message_type = message_type
            self.message_data = message_data

    def convert_to_JSON(self):
        """
        Convert message to JSON.
        :return: Message in the JSON format
        """
        ...

    def JSON_to_message(self, received_json):
        """
        Convert JSON to the CMessage class.
        :param received_json: JSON by the server
        """
        ...
