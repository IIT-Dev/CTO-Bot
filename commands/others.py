from discord.ext import commands

import sqlite3

class OtherCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def confirmation(self, ctx):
		confirmation = await ctx.send(f'Do you really want to delete data from table {tableName}?')
		await confirmation.add_reaction('✅')
		await confirmation.add_reaction('❌')

		def check(reaction, user):
			return user == ctx.author and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

		try:
			reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
		except asyncio.TimeoutError:
			await confirmation.edit('Timed Out!')
			await confirmation.clear_reactions()
			return

	return reaction, user

	@commands.command(name='ping', aliases=['p'])
	async def ping(self, ctx):
		await ctx.send(f"Pong! 🏓\nPing : {int(self.bot.latency*1000)} ms")

	@commands.command()
	@commands.is_owner()
	async def set_db(self, ctx):
		conn = sqlite3.connect('Konsultasi.db')
		cursor = conn.cursor()

		setup1 = """
		CREATE TABLE IF NOT EXISTS konsultasi (
			id_konsul int NOT NULL AUTOINCREMENT,
			nama_konsul str NOT NULL,
			solved int NOT NULL,
			PRIMARY KEY (id_konsul)
		);
		"""
		cursor.execute(setup1)

		setup2 = """
		CREATE TABLE IF NOT EXISTS settings (
			guild_id int NOT NULL,
			category_id int NOT NULL,
			message_id int NOT NULL
		);
		"""
		cursor.execute(setup2)

		conn.commit()
		conn.close()

	@commands.command()
	@commands.is_owner()
	async def delete_table(self, ctx, tableName:str=None):
		conn = sqlite3.connect()
		cursor = conn.cursor()

		selection = f"""
		SELECT *
		FROM {tableName}
		"""
		exist = cursor.execute(selection).fetchall()

		if exist:

			deletion = f"""
			DELETE FROM {tableName}
			"""
			cursor.execute(deletion)

			await ctx.send(f'Data from table {tableName} has been deleted!')
		else:
			await ctx.send(f'Table {tableName} doesn\'t exist!')

		conn.commit()
		conn.close()

def setup(bot):
	bot.add_cog(OtherCommands(bot))
