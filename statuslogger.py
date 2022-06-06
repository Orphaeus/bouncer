'''
Handles read/write operations on the status_logs.csv file.
'''

import discord
import pandas as pd
from datetime import datetime, timedelta

status_logs = pd.read_csv("status_logs.csv", header=0)


def update_member_list(guild:discord.Guild):
	'''
	Check the guild for members that are not currently on the status_logs list and add them to it. Then, remove any members that are no longer in the guild.
	'''

	# Add missing members
	global status_logs
	for member in guild.members:
		if not member.name in status_logs["name"].values:
			status_logs = pd.concat([status_logs, pd.DataFrame({"name":[member.name],"last_online":[datetime.now().date()]})], ignore_index=True)

	# Remove members that aren't on the server anymore
	for name in status_logs["name"].values:
		if not name in [member.name for member in guild.members]:
			status_logs = status_logs.drop(status_logs.loc[status_logs["name"] == name].index)

	# Update the file
	status_logs.to_csv("status_logs.csv", index=False)


def update_record(name:str):
	'''
	Update a specific row in status_logs.csv.
	'''

	status_logs.loc[status_logs["name"] == name, "last_online"] = datetime.now().date()
	# Update the file
	status_logs.to_csv("status_logs.csv", index=False)


def get_record(name:str):
	'''
	Get a single row from status_logs.csv by name.
	'''

	return status_logs.loc[status_logs["name"] == name]["last_online"]


def get_lapsed_members(warn_days:int, prune_days:int):
	'''
	Find which members have been inactive for more than prune_days days. Those who have been inactive for exactly warn_days days will receive a warning only.
	'''
	
	warn_members = []
	prune_members = []
	for index in status_logs.index:
		row = status_logs.iloc[index]
		print(type(row["last_online"]))
		date_parts = [int(char) for char in row["last_online"][:10].split('-')]
		diff = datetime.now().date() - datetime(date_parts[0], date_parts[1], date_parts[2]).date()
		if diff == timedelta(warn_days):
			warn_members.append(row)
		if diff > timedelta(prune_days):
			prune_members.append(row["name"])
	return warn_members, prune_members
