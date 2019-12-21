"""
Protects players when they first spawn for a given time

CONFIG SETTING EXAMPLE for 3 seconds of protection
"spawn_protection_time": 3

Script by Rugg
"""
from pyspades.constants import FALL_KILL
from piqueserver.config import config
from twisted.internet import reactor
spawntimer_config = config.option('spawn_protection_time', default = 3)

def apply_script(protocol, connection, config):
	class invincibilityConnection(connection):
		invulnerable = True
		spawntimer = None
		protectionTime = spawntimer_config.get()
		def on_shoot_set(self, fire):
			if fire and self.invulnerable:
				self.invulnerable = False
			connection.on_shoot_set(self, fire)

		def on_hit(self, hit_amount, hit_player, kill_type, grenade):
			if hit_player.invulnerable:
				return False
			connection.on_hit(self, hit_amount, hit_player, kill_type, grenade)

		def on_kill(self, killer, kill_type, grenade):
			self.invulnerable = True
			if self.spawntimer is not None:
					try:
						self.spawntimer.cancel()
					except:
						pass
			self.spawntimer = None
			connection.on_kill(self, killer, kill_type, grenade)

		def uninvuvlnerable(self):
			self.invulnerable = False

		def on_spawn(self, pos):
			if self is not None:
				self.spawntimer = reactor.callLater(self.protectionTime, self.uninvuvlnerable)
			connection.on_spawn(self, pos)
	return protocol, invincibilityConnection