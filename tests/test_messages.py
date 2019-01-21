import pytest
from soucevi1_dist_chat.CMessage import CMessage, MessageType


@pytest.fixture
def message_instance():
    message = CMessage(sender_address='127.0.0.1',
                       sender_port='12345',
                       sender_name='Lojza',
                       time=78,
                       message_type=MessageType.user_message,
                       message_data='Ahoj')
    return message


def test_cmessage_from_string(message_instance):
    from_string = CMessage(message_str='{"s_addr": "127.0.0.1", "s_port": "12345", "s_name": "Lojza", '
                                       '"data": "Ahoj", "time": 78, "m_type": 1}')
    assert from_string.sender_address == message_instance.sender_address
    assert from_string.sender_port == message_instance.sender_port
    assert from_string.sender_name == message_instance.sender_name
    assert from_string.time == message_instance.time
    assert from_string.message_type == message_instance.message_type
    assert from_string.message_data == message_instance.message_data


def test_cmessage_from_json(message_instance):
    json_dict = {'s_addr': '127.0.0.1',
                 's_port': '12345',
                 's_name': 'Lojza',
                 'data': 'Ahoj',
                 'time': 78,
                 'm_type': 1}
    from_json = CMessage(message_json=json_dict)
    assert from_json.sender_address == message_instance.sender_address
    assert from_json.sender_port == message_instance.sender_port
    assert from_json.sender_name == message_instance.sender_name
    assert from_json.time == message_instance.time
    assert from_json.message_type == message_instance.message_type
    assert from_json.message_data == message_instance.message_data


def test_convert_to_json(message_instance):
    json_dict = {'s_addr': '127.0.0.1',
                 's_port': '12345',
                 's_name': 'Lojza',
                 'data': 'Ahoj',
                 'time': 78,
                 'm_type': 1}
    from_cmessage = message_instance.convert_to_json()
    assert json_dict == from_cmessage


def test_convert_to_string(message_instance):
    string = '{"s_addr": "127.0.0.1", "s_port": "12345", "s_name": "Lojza", "data": "Ahoj", "time": 78, "m_type": 1}'
    from_cmessage = message_instance.convert_to_string()
    assert string == from_cmessage

