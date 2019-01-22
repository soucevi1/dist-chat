import pytest
from soucevi1_dist_chat.CNode import CNode
from soucevi1_dist_chat.CMessage import CMessage, MessageType


@pytest.fixture
def node_instance():
    node = CNode(False, '127.0.0.1', '12345', '127.0.0.1', '4321', 'Jmeno')
    return node


@pytest.fixture
def message_instance():
    message = CMessage(sender_address='127.0.0.1',
                       sender_port='54321',
                       sender_name='Lojza',
                       time=78,
                       message_type=MessageType.user_message,
                       message_data='Ahoj')
    return message
