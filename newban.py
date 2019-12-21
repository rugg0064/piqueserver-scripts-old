import json

from piqueserver.commands import command
from piqueserver.commands import admin
from piqueserver.commands import get_player
from piqueserver.config import config

ban_location = config.option('ban_file_location', default = "./")
ban_loc = ban_location.get()
@command(admin_only=True)
@admin
def nban(connection, value, *arg):
	#print("STARTING")
	#print(value)
	player = get_player(connection.protocol, value)
	ipString = player.address[0]
	#print("BANNING", ipString)
	player.kick("Player has been permanently banned from this server", silent = False)
	for i in range(0,33):
		#print("I:", i)
		xplayer = None
		try:
			xplayer = get_player(connection.protocol, "#" + str(i))
		except:
			pass
			#print("error")
		if xplayer is not None:
			if xplayer.address[0] == ipString:
				#print("FOUND A MATCH")
				xplayer.kick("Player has been permanently banned from this server", silent = False)
				#print(player.address[0])
	print("writing")
	with open(ban_loc, 'r') as f:
		bans_dict = json.load(f)
		bans_dict['bans'].append(ipString)
		with open(ban_loc, 'w') as w:
			json.dump(bans_dict, w, indent = 4)


def apply_script(protocol, connection, config):
	class newbanprotocol(protocol):
		def on_connect(self, peer):
			with open(ban_loc, 'r') as f:
				bans_dict = json.load(f)
			plaintextaddress = str(peer.address)
			address = plaintextaddress[0:plaintextaddress.find(":")]
			#print(address)
			#print(bans_dict['bans'])
			if address in bans_dict['bans']:
				print("Banned user tried to join, IP:", plaintextaddress)
				#print("TRUE")
				peer.disconnect()
			protocol.on_connect(self, peer)
	class newbanconnection(connection):
		pass
	return newbanprotocol, newbanconnection