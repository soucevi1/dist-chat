import sys
import click
from soucevi1_dist_chat import CNode
import asyncio


@click.command()
@click.option('-l/-L', '--leader/--not_leader', is_flag=True, default=False,
              help='This is the first node to started in this chatroom, e.g. the leader')
@click.option('-p', '--port', prompt='Enter port number please', type=int,
              help='Port this node will bind to')
@click.option('-na', '--neighbor-address',  help='IP address of the neighbor')
@click.option('-np', '--neighbor-port',  help='Port of the neighbor')
@click.option('-n', '--name', prompt='Enter your name please',
              help='Name that will be displayed to other participants')
def main(leader, port, neighbor_address, neighbor_port, name):
    """
    Main function of the CLI program.
    Runs one instance of the node with given parameters.
    :param leader: Bool flag saying if the started node is the leader of a new chatroom.
    :param port: Port the node will listen to and send from
    :param neighbor_address: IP adderss of the neighbor
    :param neighbor_port: Port of the neighbor
    :param name: Name of the user
    """
    if not leader:
        if neighbor_address is None or neighbor_port is None:
            print('/// Neighbor address and port need to be supplied for non-leader nodes')
            print(f'a {neighbor_address}')
            print(f'p {neighbor_port}')
            sys.exit(1)
    node = CNode.CNode(leader, port, neighbor_address, neighbor_port, name)
    asyncio.run(node.run())
