# Script called by Halite Engine to connect to the remote bot.

PORT = 8016

# ----------------------------------------------------------------------------

import sys, threading, time
import SimpleWebSocketServer as swss

# ----------------------------------------------------------------------------

def log(msg):
	with open("server_log.txt", "a+") as logfile:
		logfile.write(msg.strip() + "\n")

# ----------------------------------------------------------------------------

mutex = threading.Lock()
o_client = None
halite_lines = []

# ----------------------------------------------------------------------------

class HaliteBot(swss.WebSocket):

	def handleConnected(self):
		with mutex:
			global o_client; o_client = self
			self.token = "notoken"
			log("New connection! {}".format(o_client))

	def handleClose(self):
		with mutex:
			log("Connection closing!")
			global o_client; o_client = None
			self.sendMessage("disconnected")

	def handleMessage(self):
		with mutex:
			msg = self.data.strip()
			log("<< {}".format(msg))

			if msg.startswith("NEW_TOKEN"):
				self.token = msg.split()[1]
				log("Token now {}".format(self.token))
				for line in halite_lines:
					self.sendMessage("{} {}".format(self.token, line))
					log(">> " + "{} {}".format(self.token, line))

			elif msg.startswith(self.token):
				print(msg[len(self.token):].strip())
				sys.stdout.flush()
				log("++ {}".format(msg[len(self.token):].strip()))

# ----------------------------------------------------------------------------

def server_start():
	server = swss.SimpleWebSocketServer("", PORT, HaliteBot, selectInterval = 0.1)
	server.serveforever()

def relay():
	while True:
		msg = input().strip()			# Get line from Halite/Stdin
		log("-- {}".format(msg))
		log("client was: {}".format(o_client))
		with mutex:
			halite_lines.append(msg)
			if o_client is not None:
				o_client.sendMessage("{} {}".format(o_client.token, msg))
				log(">> " + "{} {}".format(o_client.token, msg))

# ----------------------------------------------------------------------------

log("Starting up!")

threading.Thread(target = server_start, daemon = True).start()

relay()
