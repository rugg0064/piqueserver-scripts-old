"""
Allows players to regenerate health at a given hp/time after a given amount of time

CONFIG EXAMPLE for beginning regneration after one second at 1hp/0.07seconds
"regen" : {
	"regen_delay" : 1,
	"heal_loop_speed" : 0.07,
	"heal_amount" : 1
}

Script by Rugg
"""
from pyspades.contained import *
from twisted.internet.task import LoopingCall
from pyspades.constants import FALL_KILL
from twisted.internet import reactor
from twisted.internet.error import AlreadyCalled
from piqueserver.config import config

#define variables from config
regen_config = config.section("regen")
regen_delay_config = regen_config.option("regen_delay", default = 5)
heal_loop_speed_config = regen_config.option("heal_loop_speed", default = 0.05)
heal_amount_config = regen_config.option("heal_amount", default = 1)

regen_delay = regen_delay_config.get()
heal_loop_speed = heal_loop_speed_config.get()
heal_amount = heal_amount_config.get()

def apply_script(protocol, connection, config):
	class Regen(connection):
		hpValues = []
		regencalllater = None #X is the regen delayed call, can't think of a concise descriptive name for it
		def starthealing(self, hpAfterHit): #Activates healing
			if self.hp is not None:
				hp = round(self.hp)
				if hp>hpAfterHit-5 and hp<hpAfterHit+5: #Seems like cancelling actually doesn't work at all, not too sure
					if not self.heal_loop.running: #So this makes sure that you havent gotten hit since the call, because current hp will be different than
						self.heal_loop.start(heal_loop_speed) #hp when you got hit originally

		def doHeal(self): #Stops heal loop if max hp, otherwise heals by specified amount
			if not self.hp is None:
				if self.hp>=100:
					if self.heal_loop.running:
						self.heal_loop.stop()
				else:
					connection.set_hp(self, self.hp + heal_amount, kill_type=FALL_KILL)
			else:
				if self.heal_loop.running:
						self.heal_loop.stop()

		def __init__(self, *arg, **kw): #Defines healing loop to be used
			self.heal_loop = LoopingCall(self.doHeal)
			connection.__init__(self, *arg, **kw)

		def on_kill(self, killer, type, grenade): #Same as on_spawn, cancels everything
			self.cancelTimer()
			if self.heal_loop.running:
				self.heal_loop.stop()
			connection.on_kill(self, killer, type, grenade)

		def cancelTimer(self): #Easy way to cancel the active regen timer
			try:
				self.regencalllater.cancel
				self.assertRaises(error.AlreadyCalled, self.regencalllater.cancel)
			except:
				pass

		def on_fall(self, damage):
			if self.heal_loop.running:
				self.heal_loop.stop()
			self.cancelTimer()
			self.regencalllater = reactor.callLater(regen_delay, self.starthealing, round(self.hp-damage))

		def on_hit(self, hit_amount, hit_player, kill_type, grenade): #Stops healing, cancels any timer and creates a new one
			if hit_player.heal_loop.running:
				hit_player.heal_loop.stop()
			hit_player.cancelTimer()
			if hit_player.hp is not None:
				hit_player.regencalllater = reactor.callLater(regen_delay, hit_player.starthealing, round(hit_player.hp-hit_amount))
			connection.on_hit(self, hit_amount, hit_player, type, grenade)

		def on_spawn(self, position): #Makes sure there's no timer and not healing
			self.cancelTimer()
			if self.heal_loop.running:
				self.heal_loop.stop()
			connection.on_spawn(self, position)
	return protocol, Regen
