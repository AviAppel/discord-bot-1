import os
import random

import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (id: {bot.user.id})")
    await bot.tree.sync()


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.tree.command(name="random", description="Get a random integer in an inclusive range")
@app_commands.describe(
    minimum="The minimum value (inclusive, default 1)",
    maximum="The maximum value (inclusive, default 100)",
)
async def random_command(
    interaction: discord.Interaction, minimum: int = 1, maximum: int = 100
):
    if minimum > maximum:
        await interaction.response.send_message(
            f"Minimum ({minimum}) can't be greater than maximum ({maximum})."
        )
        return
    await interaction.response.send_message(str(random.randint(minimum, maximum)))


if __name__ == "__main__":
    token = os.environ["DISCORD_BOT_TOKEN"]
    bot.run(token)
