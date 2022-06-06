'''
Module for constructing all messages sent to either Discord or the console output. Exists to abstract massive text strings into a separate file.
'''

import discord
from discord.errors import HTTPException

from info import Info


BEN_EMAIL = ''
BEN_DISCORD = ''
NICK_HELP_MSG = 'https://discord.com/channels/750102333987356682/750142461514481664/818541647661891594' 


def initialize(info:Info):
	global BEN_EMAIL
	global BEN_DISCORD
	BEN_EMAIL = info.ben_email
	BEN_DISCORD = info.ben_discord


class Bouncer:
	'''
	Contains methods for constructing messages to be delivered via Discord.
	'''

	@staticmethod
	def approval():
		msg = f"Thank you for setting your nickname. You should now have full access to the server!\n\nIf you are still unable to access the full list of server channels, please contact Ben Pickard here on Discord ({BEN_DISCORD}) or by email ({BEN_EMAIL})."
		return msg
	
	@staticmethod
	def no_match():
		msg = f"The nickname you have set was not found in the EU Data Science classlist. Double-check that the first and last name you used EXACTLY match your first and last name as they appear on Brightspace.\nIf you believe this is an error, please contact Ben Pickard here on Discord ({BEN_DISCORD}) or by email ({BEN_EMAIL}).\n\nNOTE: If you are attempting to join before the first day of your first term in the program, your name will not be recognized and you will need to be verified manually. Contact Ben Pickard to do so."
		return msg
	
	@staticmethod
	def nickname_reminder(role:discord.Role, ben:discord.Member):
		msg = f'{role.mention} Hello, welcome to the server! Before you can participate in discussion, you need to change your nickname so that it complies with the #code-of-conduct. ***Until you set your nickname, you will not be able to see any of the discussion channels.***\n\nFor more information about what an acceptable nickname looks like, see Rule #2 (IDENTITY) on the code-of-conduct.\n\nFor information on **how to change your nickname**, see this message: {NICK_HELP_MSG}\n\nOnce you set your nickname, you will be granted full access to the server.\n\n*Note: If you believe you have received this notification in error, please contact {ben.mention} here on Discord or by email ({BEN_EMAIL}).*'
		return msg
	
	@staticmethod
	def prune_reminder(days_absent:int, days_left:int):
		msg = f"PLEASE NOTE:\nYou have not been seen on the EU Master's in Data Science server in {days_absent} days. If you do not visit within the next {days_left} days, you will be removed from the server. If you are removed but wish to rejoin the server, you may do so at any time via the link on Brightspace.\n\nIf you no longer wish to participate in the EU Master's in Data Science server, you can disregard this message."
		return msg


class Logs:
	'''
	Contains methods for constructing messages to be delivered as output to the console.
	'''

	@staticmethod
	def approval(member:discord.Member):
		msg = f"Approved member {member} (Nickname '{member.nick}')."
		return msg

	@staticmethod
	def connect(user:discord.ClientUser, guild:discord.Guild):
		msg = f'{user} has connected to:\n'f'{guild.name} (id: {guild.id})'
		return msg

	@staticmethod
	def exception(exc:HTTPException, method_name:str):
		msg = f"HTTPException on {method_name}: {exc.code} {exc.text}"
		return msg

	@staticmethod
	def found_match(result): # str?
		msg = f"\nFound match {result}"
		return msg

	@staticmethod
	def nick_changed(before:discord.Member, after:discord.Member):
		msg = f"Member {before.name} (nickname '{before.nick}') updated nickname to '{after.nick}'."
		return msg

	@staticmethod
	def new_member(member:discord.Member):
		msg = f"New member: {member.name} (nickname '{member.nick}')"
		return msg

	@staticmethod
	def no_match():
		msg = f"NO MATCH FOUND."
		return msg
