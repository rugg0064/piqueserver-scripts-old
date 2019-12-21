"""
Gives the player infinite blocks and a given amount of grenades

CONFIG SETTING EXAMPLE for 5 grenades
"regen" : {
	"regen_delay" : 1,
	"heal_loop_speed" : 0.07,
	"heal_amount" : 1
}
w
Script by Rugg
"""
import math
from twisted.internet import reactor
from pyspades.constants import GRENADE_KILL
from pyspades.contained import *
from pyspades.constants import BLOCK_TOOL
from pyspades import contained as loaders
from piqueserver.config import config
grenades_config = config.option('starting_grenades', default = 3)
def apply_script(protocol, connection, config):
	class EnterConnection(connection):
		startinggrenades = grenades_config.get()
		grenadecount = 0
		
		def on_spawn(self, position):
			self.grenadecount = self.startinggrenades
			connection.on_spawn(self, position)

		def on_grenade_thrown(self, grenade):
			self.grenadecount -= 1
			if(self.grenadecount<-4):
				grenade.fuse = 500000
				connection.send_chat(self, "You have thrown too many dud grenades.",global_message = False)
				connection.kill(self)
			elif(self.grenadecount==-4):
				connection.send_chat(self, "You will die if you throw one more dud grenade.",global_message = False)
			elif(self.grenadecount<0):
				connection.send_chat(self, "You are out of live grenads, you can throw %d more grenades until you die!" % (4-abs(self.grenadecount)),global_message = False)
				grenade.fuse = 500000
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
			self.grenadecount = self.startinggrenades
			connection.send_chat(self, "Grenades refilled", global_message=False)
			connection.on_refill(self)
	return protocol, EnterConnection
