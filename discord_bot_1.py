import collections
import os
import random

import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)


# Category definitions (resources and attributes)
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

DUEL_ATTRIBUTES = ["Cunning", "Prowess", "Strategy"]
ALL_ATTRIBUTES = ["Rulership", "Cunning", "Charisma", "Prowess", "Magic", "Strategy"]

CATEGORIES = {
    "nrg_iron": NON_RESEARCH_GENERAL_PLUS_IRON,
    "nrg": NON_RESEARCH_GENERAL,
    "general": GENERAL,
    "luxury": LUXURY,
    "all": ALL,
    "attr_duel": DUEL_ATTRIBUTES,
    "attr_all": ALL_ATTRIBUTES,
}


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (id: {bot.user.id})")
    await bot.tree.sync()


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.tree.command(name="random", description="Pick a random resource or attribute")
@app_commands.choices(
    category=[
        app_commands.Choice(
            name="Resources: Non-Research General + Iron", value="nrg_iron"
        ),
        app_commands.Choice(name="Resources: Non-Research General", value="nrg"),
        app_commands.Choice(name="Resources: General", value="general"),
        app_commands.Choice(name="Resources: Luxury", value="luxury"),
        app_commands.Choice(name="Resources: All", value="all"),
        app_commands.Choice(name="Attribute: Duel", value="attr_duel"),
        app_commands.Choice(name="Attribute: All", value="attr_all"),
    ]
)
@app_commands.describe(amount="How many resources to roll (1-100, default 1)")
async def random_command(
    interaction: discord.Interaction,
    category: app_commands.Choice[str],
    amount: app_commands.Range[int, 1, 100] = 1,
):
    resources = CATEGORIES[category.value]
    rolls = random.choices(resources, k=amount)
    counts = collections.Counter(rolls)
    parts = [
        f"{count} {name}"
        for name, count in sorted(
            counts.items(), key=lambda item: resources.index(item[0])
        )
    ]
    await interaction.response.send_message("; ".join(parts))


if __name__ == "__main__":
    token = os.environ["DISCORD_BOT_TOKEN"]
    bot.run(token)
