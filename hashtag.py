"""
Kicks users who's name contains a '#'

Script by Rugg
"""
def apply_script(protocol, connection, config):
	class hashtagConnection(connection):
		def on_login(self, name):
			if name is not None and '#' in name:
				connection.kick(self, "#'s in names are not allowed in this server", True)
			connection.on_login(self, name)
	return protocol, hashtagConnection