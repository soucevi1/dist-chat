import pytest
import asyncio
import pytest_asyncio
from asynctest import CoroutineMock
from unittest.mock import patch
from soucevi1_dist_chat.CMessage import CMessage
from soucevi1_dist_chat.CMessage import MessageType
from soucevi1_dist_chat.CNode import CNode


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


@pytest.mark.asyncio
async def test_handle_message(node_instance, message_instance):
    # User message
    with patch('soucevi1_dist_chat.CNode.CNode.handle_user_message', new=CoroutineMock()) as mocked_handle:
        await node_instance.handle_message(message_instance, 'reader', None)
        mocked_handle.assert_called_once_with(message_instance, 'reader')

    # Login message
    message_instance.message_type = MessageType.login_message
    with patch('soucevi1_dist_chat.CNode.CNode.handle_login_message', new=CoroutineMock()) as mocked_handle:
        await node_instance.handle_message(message_instance, None, 'writer')
        mocked_handle.assert_called_once_with(message_instance, 'writer')

    # I am prev message
    message_instance.message_type = MessageType.i_am_prev_message
    with patch('soucevi1_dist_chat.CNode.CNode.handle_i_am_prev_message', new=CoroutineMock()) as mocked_handle:
        await node_instance.handle_message(message_instance, 'reader', 'writer')
        mocked_handle.assert_called_once_with('reader', 'writer')

    # Prev inform message
    message_instance.message_type = MessageType.prev_inform_message
    with patch('soucevi1_dist_chat.CNode.CNode.handle_prev_inform_message', new=CoroutineMock()) as mocked_handle:
        await node_instance.handle_message(message_instance, None, None)
        mocked_handle.assert_called_once_with(message_instance)

    # Hello leader message
    message_instance.message_type = MessageType.hello_leader_message
    with patch('soucevi1_dist_chat.CNode.CNode.handle_hello_leader_message', new=CoroutineMock()) as mocked_handle:
        await node_instance.handle_message(message_instance, 'reader', None)
        mocked_handle.assert_called_once_with(message_instance, 'reader')

    # Election message
    message_instance.message_type = MessageType.election_message
    with patch('soucevi1_dist_chat.CNode.CNode.handle_election_message', new=CoroutineMock()) as mocked_handle:
        await node_instance.handle_message(message_instance, None, None)
        mocked_handle.assert_called_once_with(message_instance)

    # Elected message
    message_instance.message_type = MessageType.elected_message
    with patch('soucevi1_dist_chat.CNode.CNode.handle_elected_message', new=CoroutineMock()) as mocked_handle:
        await node_instance.handle_message(message_instance, None, None)
        mocked_handle.assert_called_once_with(message_instance)


@pytest.mark.asyncio
async def test_handle_elected_message(node_instance, message_instance):
    # Check that the received with different ID sends the message on and sets the leader
    message_instance.message_type = MessageType.elected_message
    message_instance.message_data = {'addr': '127.0.0.1', 'port': '8888'}
    with patch('soucevi1_dist_chat.CNode.CNode.send_message_to_ring', new=CoroutineMock()) as mocked_handle:
        with patch('soucevi1_dist_chat.CNode.CNode.connect_to_leader', new=CoroutineMock()) as mocked_connect:
            await node_instance.handle_elected_message(message_instance)
            mocked_handle.assert_called_once()
            mocked_connect.asset_called_once()
            assert node_instance.leader_address == '127.0.0.1'
            assert node_instance.leader_port == '8888'


@pytest.mark.asyncio
async def test_handle_election_message(node_instance, message_instance):
    message_instance.message_type = MessageType.election_message
    message_instance.message_data = {'addr': '127.0.0.1', 'port': '99999'}
    with patch('soucevi1_dist_chat.CNode.CNode.send_message_to_ring', new=CoroutineMock()) as mocked_send:
        # Test losing node -- pass the message on
        message_instance.message_data = {'addr': '127.0.0.1', 'port': '99999'}
        await node_instance.handle_election_message(message_instance)
        mocked_send.assert_called_once_with(message_instance)

        # Test candidate node -- send message with this node's address
        message_instance.message_data = {'addr': '127.0.0.1', 'port': '11111'}
        await node_instance.handle_election_message(message_instance)
        message_new = message_instance
        message_new.message_data = {'addr': node_instance.address, 'port': node_instance.port}
        mocked_send.assert_called_once_with(message_new)

        # Test winning node -- send Elected message
        message_instance.message_data = {'addr': '127.0.0.1', 'port': '12345'}
        await node_instance.handle_election_message(message_instance)
        assert node_instance.is_leader
