# brotatotes 3/1/2018

# A simple Facebook Messenger bot that provides a setup for adding and implementing 
# simple commands.
# WARNING: these commands are susceptible to python injection so make sure they
# can only be run by you or those you trust.

from fbchat import log, Client
from fbchat.models import *
from getpass import getpass, getuser
import math, time, random, pprint
import PyDictionary, wikipedia, URLShortener
from Commands import Commands
from MathFunctions import MathFunctions

class FBBot(Client):
	def __init__(self, *args):
		self.dictionary = PyDictionary.PyDictionary()
		self.urlshortener = URLShortener.TinyURL()
		self.wikipedia = wikipedia
		# self.google =
		self.pp = pprint.PrettyPrinter()
		super().__init__(*args)


	def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
		self.markAsDelivered(author_id, thread_id)

		# if author_id == self.uid and message_object.text[0] == '/':
		if message_object.text[0] == '/':
			parsed = self.parse_command(message_object)
			if parsed == None:
				return
			else:
				cmd, args = parsed

			eval_string = 'self.' + cmd + '(' + ((str(args)[1:-1] + ', ') if len(args) else '') + 'thread_id=' + str(thread_id) + ', ' + 'thread_type=' + str(thread_type) + ')'
			print("RUNNING COMMAND:", eval_string)
			eval(eval_string)


	def parse_command(self, message_object):
		first_space = message_object.text.find(' ')
		if first_space == -1:
			first_space = len(message_object.text)

		cmd = message_object.text[1:first_space].lower()

		# not a real command
		if not cmd in Commands: 
			return

		args = []
		arg_types = Commands[cmd]
		prev_space = first_space
		for i, arg_type in enumerate(arg_types):
			# Assumption: the last arg is always str and may contain spaces.
			# For the last arg_type, just take the rest of the text:
			if i == len(arg_types) - 1:
				args.append(message_object.text[prev_space + 1:])
				break

			# Find the next space. Quit if none found.
			next_space = message_object.text.find(' ', prev_space + 1)
			if next_space == -1:
				return

			# get the argument string (between previous space and next space)
			# try to cast the arg into corresponing arg_type
			arg = message_object.text[prev_space + 1:next_space]
			try: 
				arg = arg_type(arg)
			except Exception as e:
				print("Invalid args:", e)
				return

			args.append(arg)

			prev_space = next_space

		print("Successfully parsed command:", cmd, args)
		return cmd, args


	def ppsend(self, msg, **kwargs):
		if msg == None:
			msg = "No results found."
		else:
			msg = self.pp.pformat(msg)
		print(msg)

		self.send(Message(text=msg), **kwargs)

	##################### COMMAND FUNCTIONS #####################

	def help(self, **kwargs):
		self.send(Message(text="Here are a list of commands you can use."), **kwargs)
		self.ls(**kwargs)

	def ls(self, **kwargs):
		self.ppsend(Commands, **kwargs)

	def spam(self, n, msg, **kwargs):
		for _ in range(n):
			time.sleep(0.25) # TODO: make this an input to the command
			self.send(Message(text=msg), **kwargs)

	
	def define(self, s, **kwargs):
		try:
			msg = self.dictionary.meaning(s)
		except Exception as e:
			print("PyDictionary search for", s, "failed:", e)
			msg = None

		self.ppsend(msg, **kwargs)


	def wiki(self, s, **kwargs):
		try:
			msg = self.wikipedia.summary(s)
		except Exception as e:
			msg = str(e)

		self.send(Message(text=msg), **kwargs)


	def calc(self, c, **kwargs):
		c = c.replace('^', '**')
		for math_func in MathFunctions:
			c = c.replace(math_func, 'math.' + math_func)

		try:
			res = str(eval(c))
		except Exception as e:
			res = "Failed to evaluate expression: " + str(e) + ":\n" + c

		self.send(Message(text=res), **kwargs)


	def chickenize(self, s, **kwargs):
		new = ""
		cap = False
		for c in s:
			if c == " ":
				new += c
				cap = not cap
			elif cap:
				new += c.upper()
			else:
				new += c.lower()
			cap = not cap
		
		self.send(Message(text=new), **kwargs)

	def google(self, s, **kwargs):
		link = "https://www.google.com/search?q=" + s.replace(' ', '+').strip()
		self.shorten(link, **kwargs)
		

	def lmgtfy(self, s, **kwargs):
		link = "http://lmgtfy.com/?q=" + s.replace(' ', '+').strip()
		self.shorten(link, **kwargs)

	def youtube(self, s, **kwargs):
		link = "https://www.youtube.com/results?search_query=" + s.replace(' ', '+').strip()
		self.shorten(link, **kwargs)
		

	def shorten(self, link, **kwargs):
		msg = self.urlshortener.create(link)
		if msg == None:
			msg = "Unable to shorten link."
		self.send(Message(text=msg), **kwargs)




if __name__ == "__main__":
	FBBot(getpass(prompt="Username: "), getpass()).listen()