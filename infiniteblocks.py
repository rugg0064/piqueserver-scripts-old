"""
NOTE: This is a depricated module, please use blocksandgrenades.py
Does stuff
.. codeauthor:: rugg
"""
from pyspades.contained import *
from pyspades.constants import BLOCK_TOOL
from pyspades import contained as loaders
def apply_script(protocol, connection, config):
	class EnterConnection(connection):
		grenadecount = 0
		def on_spawn(self, position):
			#print("SPAWNED")
			self.grenadecount = 5
			#print(self.grenadecount)
			connection.on_spawn(self, position)

		def on_grenade_thrown(self, grenade):
			if(self.grenadecount<=0):
				grenade.fuse = 500000
			self.grenadecount -= 1
			#print("grenades = ",self.grenadecount)
			if(self.grenadecount<0):
				connection.send_chat(self, "You are out of live grenades!",global_message = False)
			else:
				connection.send_chat(self, "You have %d grenades left!" % (self.grenadecount), global_message = False)

			self.refillAndSetHPAmmo()

			connection.on_grenade_thrown(self, grenade)

		def refillAndSetHPAmmo(self):
			currentHP = self.hp
			weaponLoader = loaders.WeaponReload()
			weaponLoader.player_id = self.player_id
			weaponLoader.clip_ammo = self.weapon_object.current_ammo
			weaponLoader.reserve_ammo = self.weapon_object.current_stock
			connection.refill(self)
			self.send_contained(weaponLoader)
			connection.set_hp(self, currentHP, kill_type=FALL_KILL)
		

		def on_block_build(self, x,y,z):
			self.refillAndSetHPAmmo()
			connection.on_block_build(self, x, y, z)

		def on_line_build(self, points):
			self.refillAndSetHPAmmo()
			connection.on_line_build(self,points)

		def on_refill(self):
			self.grenadecount = 5
			connection.send_chat(self, "Grenades refilled", global_message=False)
			connection.on_refill(self)

		def on_login(self, name):
			#print("poopass")
			#self.protocol.send_chat("abababababa", global_message=None)
			connection.on_login(self, name)
	return protocol, EnterConnection
