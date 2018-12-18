import sys
import click
from soucevi1_dist_chat import CNode
import asyncio
import logging


@click.command()
@click.option('-l/-L', '--leader/--not_leader', is_flag=True, default=False,
              help='This is the first node to started in this chatroom, e.g. the leader')
@click.option('-a', '--address', required=True, help='IP address this node will run on')
@click.option('-p', '--port', type=int, help='Port this node will bind to')
@click.option('-na', '--neighbor-address',  help='IP address of the neighbor')
@click.option('-np', '--neighbor-port',  help='Port of the neighbor')
@click.option('-n', '--name', help='Name that will be displayed to other participants')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Logging not only to'
                                                                   'file, but also to stdout.')
def main(leader, address, port, neighbor_address, neighbor_port, name, verbose):
    """
    Main function of the CLI program.
    Runs one instance of the node with given parameters.
    :param leader: Bool flag saying if the started node is the leader of a new chatroom.
    :param address: IP address of this node.
    :param port: Port the node will listen to and send from
    :param neighbor_address: IP adderss of the neighbor
    :param neighbor_port: Port of the neighbor
    :param name: Name of the user
    :param verbose: If set, log to the file as well as to stdout. If not, log only to file.
    """

    # Initialize logging
    root_logger = logging.getLogger()
    file_handler = logging.FileHandler(f'chat_{port}.log')
    root_logger.addHandler(file_handler)

    # Verbose: log messages printed to stdout
    if verbose:
        console_handler = logging.StreamHandler(sys.stdout)
        root_logger.addHandler(console_handler)

    root_logger.setLevel(logging.INFO)

    # In case the log file already exists, divide the chat sessions
    logging.info('-------------------------------------')

    if not leader:
        if neighbor_address is None or neighbor_port is None:
            print('/// Neighbor address and port need to be supplied for non-leader nodes')
            print(f'a {neighbor_address}')
            print(f'p {neighbor_port}')
            sys.exit(1)
    node = CNode.CNode(leader, address, port, neighbor_address, neighbor_port, name)
    asyncio.run(node.run())
