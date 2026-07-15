import os
import random

import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)


# Resource category definitions
NON_RESEARCH_GENERAL = ["Food", "Wood", "Stone", "Mounts", "Magic Points"]
GENERAL = ["Food", "Wood", "Stone", "Mounts", "Research", "Magic Points"]
LUXURY = [
    "Narcotics",
    "Spices",
    "Medicinal Herbs",
    "Dyes",
    "Magical Crystals",
    "Gold",
    "Moonstone",
    "Furs",
    "Quintessence",
    "Cocoa",
    "Star Iron",
    "Tea",
]
NON_RESEARCH_GENERAL_PLUS_IRON = NON_RESEARCH_GENERAL + ["Iron"]
ALL = GENERAL + ["Iron"] + LUXURY

RESOURCE_CATEGORIES = {
    "nrg_iron": NON_RESEARCH_GENERAL_PLUS_IRON,
    "nrg": NON_RESEARCH_GENERAL,
    "general": GENERAL,
    "luxury": LUXURY,
    "all": ALL,
}


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (id: {bot.user.id})")
    await bot.tree.sync()


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.tree.command(name="random", description="Pick a random resource from a category")
@app_commands.choices(
    category=[
        app_commands.Choice(
            name="Resources: Non-Research General + Iron", value="nrg_iron"
        ),
        app_commands.Choice(name="Resources: Non-Research General", value="nrg"),
        app_commands.Choice(name="Resources: General", value="general"),
        app_commands.Choice(name="Resources: Luxury", value="luxury"),
        app_commands.Choice(name="Resources: All", value="all"),
    ]
)
async def random_command(
    interaction: discord.Interaction, category: app_commands.Choice[str]
):
    resources = RESOURCE_CATEGORIES[category.value]
    await interaction.response.send_message(random.choice(resources))


if __name__ == "__main__":
    token = os.environ["DISCORD_BOT_TOKEN"]
    bot.run(token)
