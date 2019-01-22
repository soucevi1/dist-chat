import pytest
import asyncio
import pytest_asyncio
from asynctest import CoroutineMock
from unittest.mock import patch
from soucevi1_dist_chat.CMessage import MessageType
from tests.fixtures import node_instance, message_instance


@pytest.mark.asyncio
async def test_add_connection_record(node_instance, message_instance):
    node_instance.connections = [{'addr': '1.1.1.1', 'port': '1111', 'reader': 'reader1', 'writer': 'writer1'}]
    with patch('asyncio.open_connection', new=CoroutineMock()) as mocked_open:
        mocked_open.return_value = 'reader2', 'writer2'
        await node_instance.add_connection_record(message_instance, 'reader3')
        assert node_instance.connections == [{'addr': '1.1.1.1', 'port': '1111',
                                              'reader': 'reader1', 'writer': 'writer1'},
                                             {'addr': '127.0.0.1', 'port': '54321',
                                              'reader': 'reader3', 'writer': 'writer2'}]


def test_remove_from_connections(node_instance):
    node_instance.connections = [{'addr': '1.1.1.1', 'port': '1111', 'reader': 'reader1', 'writer': 'writer1'},
                                 {'addr': '127.0.0.1', 'port': '54321', 'reader': 'reader3', 'writer': 'writer2'}]
    node_instance.remove_from_connections('reader3665', 'writer634566')
    assert node_instance.connections == [{'addr': '1.1.1.1',
                                          'port': '1111',
                                          'reader': 'reader1',
                                          'writer': 'writer1'},
                                         {'addr': '127.0.0.1',
                                          'port': '54321',
                                          'reader': 'reader3',
                                          'writer': 'writer2'}]
    node_instance.remove_from_connections('reader1', 'writer634566')
    assert node_instance.connections == [{'addr': '1.1.1.1',
                                          'port': '1111',
                                          'reader': 'reader1',
                                          'writer': 'writer1'},
                                         {'addr': '127.0.0.1',
                                          'port': '54321',
                                          'reader': 'reader3',
                                          'writer': 'writer2'}]
    node_instance.remove_from_connections('reader1', 'writer1')
    assert node_instance.connections == [{'addr': '127.0.0.1',
                                          'port': '54321',
                                          'reader': 'reader3',
                                          'writer': 'writer2'}]


def test_find_in_connections(node_instance):
    node_instance.connections = [{'addr': '1.1.1.1', 'port': '1111', 'reader': 'reader1', 'writer': 'writer1'},
                                 {'addr': '127.0.0.1', 'port': '54321', 'reader': 'reader3', 'writer': 'writer2'}]
    assert node_instance.find_in_connections('reader3')
    assert not node_instance.find_in_connections('reader256')


@pytest.mark.asyncio
async def test_wait_for_connection(node_instance):
    node_instance.next_node_reader = 'reader'
    await node_instance.wait_for_connection()
    # Test is not stuck in an endless loop
    assert node_instance.next_node_reader == 'reader'


@pytest.mark.asyncio
async def test_connect_to_leader(node_instance):
    node_instance.leader_address = '1.2.3.4'
    node_instance.leader_port = '12345'
    with patch('asyncio.open_connection', new=CoroutineMock()) as mocked_open:
        mocked_open.return_value = ('reader', 'writer')
        with patch('soucevi1_dist_chat.CNode.CNode.send_message_to_leader', new=CoroutineMock()) as mocked_send:
            await node_instance.connect_to_leader()
            mocked_open.assert_called_once_with(node_instance.leader_address, node_instance.leader_port)
            mocked_send.assert_called_once()


@pytest.mark.asyncio
async def test_join_the_ring(node_instance, message_instance):
    message_instance.message_data = {'next_IP': '1.1.1.1',
                                     'next_port': '11111',
                                     'leader_IP': '2.2.2.2',
                                     'leader_port': '22222'}
    node_instance.next_node_reader = asyncio.StreamReader()
    node_instance.next_node_writer = asyncio.StreamWriter(None, None, None, None)
    with patch('soucevi1_dist_chat.CNode.CNode.send_message_to_ring', new=CoroutineMock()) as mocked_send:
        with patch('asyncio.StreamReader.read', new=CoroutineMock()) as mocked_read:
            mocked_read.return_value = message_instance.convert_to_string().encode()
            with patch('asyncio.StreamWriter.wait_closed', new=CoroutineMock()) as mocked_closed:
                with patch('asyncio.StreamWriter.close') as mocked_close:
                    with patch('asyncio.open_connection', new=CoroutineMock()) as mocked_open:
                        mocked_open.return_value = ('reader', 'writer')
                        with patch('soucevi1_dist_chat.CNode.CNode.connect_to_leader',
                                   new=CoroutineMock()) as mocked_connect:
                            await node_instance.join_the_ring()
                            mocked_connect.asset_called_once()
                            assert mocked_send.call_count == 2
                            assert node_instance.next_node_address == message_instance.message_data['next_IP']
                            assert node_instance.next_node_port == message_instance.message_data['next_port']
                            assert node_instance.leader_address == message_instance.message_data['leader_IP']
                            assert node_instance.leader_port == message_instance.message_data['leader_port']


def test_logical_clock(node_instance):
    node_instance.logical_clock = 16
    node_instance.set_logical_clock(3)
    assert node_instance.logical_clock == 17
    node_instance.set_logical_clock(25)
    assert node_instance.logical_clock == 26


def test_craft_message(node_instance, message_instance):
    message_instance.sender_address = node_instance.address
    message_instance.sender_port = node_instance.port
    message_instance.sender_name = node_instance.name

    m = node_instance.craft_message(message_instance.message_type, message_instance.message_data)
    assert m.sender_address == message_instance.sender_address
    assert m.sender_port == message_instance.sender_port
    assert m.sender_name == message_instance.sender_name
    assert m.message_type == message_instance.message_type
    assert m.message_data == message_instance.message_data


@pytest.mark.asyncio
async def test_send_user_message(node_instance, message_instance):
    with patch('soucevi1_dist_chat.CNode.CNode.send_message_to_leader', new=CoroutineMock()) as mocked_send:
        node_instance.is_leader = False
        await node_instance.send_user_message(message_instance)
        mocked_send.assert_called_once_with(message_instance)
    with patch('soucevi1_dist_chat.CNode.CNode.distribute_message', new=CoroutineMock()) as mocked_distribute:
        node_instance.is_leader = True
        await node_instance.send_user_message(message_instance)
        mocked_distribute.assert_called_once_with(message_instance)


@pytest.mark.asyncio
async def test_send_message_to_ring(node_instance, message_instance):
    node_instance.next_node_writer = asyncio.StreamWriter(None, None, None, None)
    with patch('asyncio.StreamWriter.drain', new=CoroutineMock()) as mocked_drain:
        with patch('asyncio.StreamWriter.write') as mocked_write:
            await node_instance.send_message_to_ring(message_instance)
            mocked_write.assert_called_once_with(message_instance.convert_to_string().encode())
            mocked_drain.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_to_leader(node_instance, message_instance):
    node_instance.leader_writer = asyncio.StreamWriter(None, None, None, None)
    with patch('asyncio.StreamWriter.drain', new=CoroutineMock()) as mocked_drain:
        with patch('asyncio.StreamWriter.write') as mocked_write:
            await node_instance.send_message_to_leader(message_instance)
            mocked_write.assert_called_once_with(message_instance.convert_to_string().encode())
            mocked_drain.assert_called_once()


@pytest.mark.asyncio
async def test_initiate_election(node_instance):
    with patch('soucevi1_dist_chat.CNode.CNode.send_message_to_ring', new=CoroutineMock()) as mocked_send:
        await node_instance.initiate_election()
        a, k = mocked_send.call_args
        assert a[0].message_data['addr'] == node_instance.address
        assert a[0].message_data['port'] == node_instance.port

