import discord
from discord.errors import HTTPException
from discord.ext import tasks
import datetime as dt
from os import path
import pandas as pd
import messages
import statuslogger
import info


# Determine location to set state
state = ''
if path.exists('Bot1/ds_classlist.csv'):
	state = "live"
else:
	state = "test"
print(messages.Logs.confirm_state(state))

# Initialize the bot's private and state-dependent data
info = info.Info(state)
messages.initialize(info)
statuslogger.initialize(info)

TOKEN = info.token
GUILD_ID = info.guild_id
DEFAULT_ROLE_ID = info.default_role_id
REMINDER_CHANNEL = info.reminder_channel
CLASSLIST_PATH = info.classlist_path

# Misc constants
TZINFO = dt.timezone(-dt.timedelta(hours=4)) # EDT
PRUNE_WARNING_DAYS = 60 # Warn members about pruning after this many days absent
PRUNE_GRACE_DAYS = 3 # Prune members this many days absent after warning
PRUNE_DAYS = PRUNE_WARNING_DAYS + PRUNE_GRACE_DAYS # Prune members after this many days absent
CLASSLIST = pd.read_csv(CLASSLIST_PATH)
INTENTS = discord.Intents().all()
client = discord.Client(intents=INTENTS)


@client.event
async def on_ready():
	# Create globals for various functions
	global guild
	global channel
	global default_role
	global ben
	guild = discord.utils.get(client.guilds, id=GUILD_ID)
	channel = discord.utils.get(guild.text_channels, id=REMINDER_CHANNEL)
	default_role = discord.utils.get(guild.roles, id=DEFAULT_ROLE_ID)
	ben = guild.owner
	
	# Print connection info
	print(messages.Logs.connect(client.user, guild))
	# Start reminder loop
	daily_tasks.start()


@client.event
async def on_member_join(member:discord.Member):
	'''
	On new member join, assign them the default role so we know their nick has not been set
	'''
	# Log the event
	await send_dm(ben, messages.Logs.new_member(member), to_console=True)

	# Add the role
	try:
		await member.add_roles(default_role, reason="Add default role")
	except HTTPException as exc:
		print(messages.Logs.exception(exc, 'member.add_roles'))
	
	# Check nickname against classlist
	result = await validate_name(member)
	if result:
		# Approve them for server access
		await send_dm(ben, messages.Logs.found_match(result), to_console=True)
		await approve_member(member)
	else:	
		# Log the match failure
		await send_dm(ben, messages.Logs.no_match(), to_console=True)


@client.event
async def on_member_update(before:discord.Member, after:discord.Member):
	'''
	Make sure this user has the default role and that it was their nickname that changed
	'''

	if default_role in before.roles and before.nick != after.nick:
		# Log the name change
		await send_dm(ben, messages.Logs.nick_changed(before, after), to_console=True)
		# Check the nick against the classlist
		result = await validate_name(after)
		if result:
			# Approve them for server access and log it
			await approve_member(after)
			await send_dm(ben, messages.Logs.found_match(result), to_console=True)
			await send_dm(after, messages.Bouncer.approval())
		else:
			# Tell them their name was not recognized and log it
			await send_dm(ben, messages.Logs.no_match(), to_console=True)
			await send_dm(before, messages.Bouncer.no_match())
	

@client.event
async def on_presence_update(before:discord.Member, after:discord.Member):
	'''
	Update this member's "last_online" column in status_logs
	'''
	# RIP this only exists in v2.0
	statuslogger.update_record(after.name)
	print(f"---{after.name} presence now {after.status}")


async def send_dm(recipient:discord.Member, msg:str, to_console=False):
	'''
	Handles sending DMs to users.
	'''

	# Print the message to the console if True
	if to_console:
		print(msg)

	# Make sure this isn't a bot
	if recipient.bot:
		return

	# Get or create the dm channel for this user
	if not recipient.dm_channel:
		await recipient.create_dm()
		dm = recipient.dm_channel
	else:
		dm = recipient.dm_channel

	# Send the message to this user
	try:
		await dm.send(msg)
	except HTTPException as exc:
		print(messages.Logs.exception(exc, 'member.dm_channel.send'))


async def validate_name(member:discord.Member):
	'''
	Check the member's nickname against the classlist to see if it is present.
	'''
	
	# If no nickname, use name
	s = ''
	if member.nick == None:
		s = member.name
	else:
		s = member.nick

	# Make s lowercase and remove non-alphabetical characters
	s_lower_alpha = lower_alpha(s)
	
	# Search classlist for a first and last name that are in s
	match_found = False
	match_row = pd.DataFrame()
	for lastname in CLASSLIST["last"]:
		if lower_alpha(lastname) in s_lower_alpha:
			# Search the first names associated with this last name
			for firstname in CLASSLIST.loc[CLASSLIST["last"] == lastname]["first"]:
				if lower_alpha(firstname) in s_lower_alpha:
					match_found = True
					match_row = CLASSLIST.loc[(CLASSLIST["first"] == firstname) & (CLASSLIST["last"] == lastname)]
					break
	
	# Return match state
	if match_found:
		return match_row["Name"].iloc[0]
	else:
		return


async def approve_member(member:discord.Member):
	'''
	Remove the default role from the member.
	'''
	
	try:
		await member.remove_roles(default_role, reason="Member approved")
		# Notify them and log the approval
		await send_dm(ben, messages.Logs.approval(member), to_console=True)
		await send_dm(member, messages.Bouncer.approval())
	except HTTPException as exc:
		print(messages.Logs.exception(exc, 'member.remove_roles'))


def lower_alpha(s:str) -> str:
	s_clean = s.lower()
	if not s.isalpha():
		for c in s:
			if not c.isalpha():
				s_clean = s_clean.replace(c, '')
	return s_clean


#@tasks.loop(time=dt.time(hour=12, minute=0, second=0, tzinfo=TZINFO)) # Run at noon EDT (v2.0 only)
@tasks.loop(seconds=1)
async def daily_tasks():
	# Run at specific time not an option until v2.0, so get hacky
	now = dt.datetime.now(tz=TZINFO).time()
	if not (now.hour == 12 and now.minute == 0 and now.second == 0):
		return

	# NICKNAME REMINDER
	# Clear the previous reminders
	history = [message async for message in channel.history()]
	for msg in history:
		if msg.author != ben:
			await msg.delete()
	# Send the new reminder
	await channel.send(messages.Bouncer.nickname_reminder(default_role, ben))


	# Disable prune functionality until I can be bothered to debug it :/
	return
	# PRUNE REMINDER
	warn_members, prune_members = statuslogger.get_lapsed_members(PRUNE_WARNING_DAYS, PRUNE_DAYS)
	for name in warn_members:
		member = discord.utils.get(guild.members, name=name)
		print(f"warning {member.name}")
		#await send_dm(member, messages.Bouncer.prune_reminder(PRUNE_WARNING_DAYS, PRUNE_GRACE_DAYS))
	
	# PRUNE
	for name in prune_members:
		member = discord.utils.get(guild.members, name=name)
		try:
			print(f"kicking {member.name}")
			#await guild.kick(member, reason=f"Inactive for more than {PRUNE_DAYS} days.")
		except (HTTPException, discord.Forbidden) as exc:
			print(messages.Logs.exception(exc, f"guild.kick (user {member.name})"))

	# UPDATE MEMBER LIST IN STATUS LOGS
	statuslogger.update_member_list(guild=guild)


client.run(TOKEN)

