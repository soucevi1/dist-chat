import click
from soucevi1_dist_chat import CNode


@click.command()
@click.option('-l/-L', '--leader/--not_leader', is_flag=True, default=False,
              help='This is the first node to started in this chatroom, e.g. the leader')
@click.option('-p', '--port', prompt='Enter port number please', type=int,
              help='Port this node will bind to')
@click.option('-n', '--name', prompt='Enter your name please',
              help='Name that will be displayed to other participants')
def main(leader, port, name):
    """
    Main function of the CLI program.
    Runs one instance of the node with given parameters.
    :param leader: Bool flag saying if the started node is the leader of a new chatroom.
    :param port: Port the node will listen to and send from
    :param name: Name of the user
    """
    node = CNode.CNode(leader, port, name)
    node.run()
