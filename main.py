import os
import discord
from discord.ext import commands
from cogwatch import watch

import asyncio
from uptime import uptime
from dotenv import load_dotenv

class CTO(commands.Bot):
	def __init__(self):
		intents = discord.Intents().all()
		super().__init__(command_prefix = '..', case_insensitive=True, intents=intents)

	@watch(path='commands')
	async def on_ready(self):
		print('Logged in as :', self.user.name)
		print('UID :', self.user.id)
		print('Discord version :', discord.__version__)
		print('----------------------')
		print('Connected to :')
		for guild in self.guilds:
			print('-', guild.name)
		activity = discord.Activity(name="konsultasi", type=discord.ActivityType.watching)
		await self.change_presence(activity=activity)

async def main():
	client = CTO()
	client.load_extension()
	await client.start(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
	uptime()
	load_dotenv()
	asyncio.run(main())
