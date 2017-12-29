import os, random, subprocess, sys, time
from websocket import create_connection

BOT = "mybot.exe --conservative"
URL = "ws://127.0.0.1:8016"

# We send the server a token which it will prefix messages to us with,
# so we can be sure the messages we receive are actually intended.

random.seed(time.time())

token = ""

for n in range(10):
	token += random.choice("0123456789abcdefghijklmnopqrstuvwxyz")

# ---------------------------------------------------------------------------

def relay_ws_to_bot(ws, bot):

	line = ws.recv().strip()

	# Skip all lines not intended for us...

	while not line.startswith(token):
		line = ws.recv().strip()

	line = line[len(token):].strip()
	line = bytes(line + "\n", encoding = "ascii")
	bot.stdin.write(line)
	bot.stdin.flush()

def relay_bot_to_ws(ws, bot):
	line = bot.stdout.readline().decode("ascii").strip()
	ws.send("{} {}".format(token, line))

# ---------------------------------------------------------------------------

print("Running...")

bot = subprocess.Popen(BOT, shell = False, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
ws = create_connection(URL)

print("Connected...")

ws.send("NEW_TOKEN {}".format(token))

for n in range(3):
	relay_ws_to_bot(ws, bot)

while 1:
	relay_bot_to_ws(ws, bot)
	relay_ws_to_bot(ws, bot)

