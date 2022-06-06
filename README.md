# Bouncer

On the Eastern University Master's in Data Science Discord server, I use a bot, affectionately known as "Bouncer", to manage the verifiation of new users. This is the source code for Bouncer.

### What does Bouncer do?
All server members' nicknames must match their names as they appear on Brightspace, and Bouncer enforces that rule. It also has a few other functions that help me run the server.
- Assign new members a role that flags them as unverified
- When an unverified member changes their nickname, check it against the class list to see if it matches. Approve them if it does, let them know it's still no good if it doesn't.
- [INDEV] Track member activity and warn members a few days before they will be pruned from the server
- [INDEV] Prune members who have not been seen for more than X days
- [PLANNED] Scrape (or something) the classlist from Brightspace daily so that I don't have to manually update it.

### What tools does Bouncer use?
Bouncer is written in Python using the [discord.py](https://github.com/Rapptz/discord.py) wrapper for the Discord API. It uses Pandas to interface with the .csv files.

### A note on playing around with Bouncer yourself
If you want to try your hand at improving Bouncer or writing your own bot, you will need to register a bot via the [Discord Developer Portal](https://discord.com/developers/applications). For an in-depth tutorial on how to setup and write a Discord bot, try [this piece from Real Python](https://realpython.com/how-to-make-a-discord-bot-python/).

Critical information such as the bot's token has been obfuscated in the `info.py` file, which is not uploaded to this repository. In order to run the bot yourself, you will need to provide it with your own version of `info.py`'s `Info` object, the definition of which can be found below. Because I use two separate bot identities to allow for testing, `Info` can be initialized for either testing or live deployment.

```Python
class Info:
	'''
	Interface for the information relevant to the selected mode ("live" or "test").
	'''
	def __init__(self, mode:str) -> None:
		if mode == "live":
			# Values for the EUMDS server
			self.token = "<token>"
			self.guild_id = "<guild_id>"
			self.default_role_id = "<default_role_id>"
			self.reminder_channel = "<reminder_channel_id>"
			self.classlist_path = "<path_to_classlist.csv>"
		if mode == "test":
			# Values for the test server
			self.token = "<token>"
			self.guild_id = "<guild_id>"
			self.default_role_id = "<default_role_id>"
			self.reminder_channel = "<reminder_channel_id>"
			self.classlist_path = "<path_to_classlist.csv>"
		
		# Values included in messages to users
		self.ben_email = "<email>"
		self.ben_discord = "<discord_username>"
