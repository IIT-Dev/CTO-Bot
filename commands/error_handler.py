from discord.ext import commands

import asyncio
import math

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            err_message = None
            if (error.retry_after > 60):
                minute = math.floor(error.retry_after/60)
                second = math.floor(error.retry_after - minute*60)
                err_message = await ctx.send(f"This command is still on cooldown. Please try again after {minute} minute(s) {second} second(s)")
            else:
                second = math.floor(error.retry_after)
                err_message = await ctx.send(f"This command is still on cooldown. Please try again after {second} second(s)")
            await asyncio.sleep(5)
            await err_message.delete()

        elif isinstance(error, commands.CommandInvokeError):
            err_msg = await ctx.send("Error When Invoking Command!")
            await asyncio.sleep(5)
            await err_msg.delete()

        elif isinstance(error, commands.errors.CommandNotFound):
            pass
        
        elif isinstance(error, commands.RoleNotFound):
            err_msg = await ctx.send("Role Not Found!")
            await asyncio.sleep(5)
            await err_msg.delete()
        
        error_ch = await self.bot.fetch_channel(849749416171536395)
        
        await error_ch.send(error)

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
