from discord.ext import commands

class Konsultasi(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
