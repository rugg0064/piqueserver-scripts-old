"""
MY SCRIPT FREAKER, GET OUT!
"""


from pyspades.constants import *
from piqueserver.commands import (command, admin, get_player, player_only, target_player)

@command('die', 'd')
def die(connection, *args):
	player = connection
	player.add_score(5)

def apply_script(protocol, connection, config):
	class RefillBlocks(connection):
		print("abcaba")
		def on_block_build(connection,x,y,z):
			connection.refill()
			connection.kill()
			connection.tool.restock()
			on_block_build(connection,x,y,z)

	return RefillBlocks, protocol
