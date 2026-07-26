import collections
import os
import random
import re

import aiohttp
import discord
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True  # required to read message content in /count_mrps

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


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


# MRP stat-block counting configuration
MRP_CHANNELS = [
    "mech-rp-guac",
    "mech-rp-whaet",
    "mech-rp-pflegi",
    "mech-rp-tolz",
    "mech-rp-jasper",
    "mech-rp-elphonsa",
    "mech-rp-temp",
]
STAT_BLOCK_WORDS = ["Rulership", "Cunning", "Charisma", "Prowess", "Magic", "Strategy"]
SESSION_START_MARKER = "start of rp for session"

HELLO_ENDPOINT = "https://pathofages.com/api/hello"

STAT_BLOCK_PATTERNS = [
    re.compile(rf"\b{re.escape(w)}\b", re.IGNORECASE) for w in STAT_BLOCK_WORDS
]


def is_stat_block(content: str) -> bool:
    return all(p.search(content) for p in STAT_BLOCK_PATTERNS)


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (id: {client.user.id})")
    await tree.sync()


@tree.command(name="random", description="Pick a random resource or attribute")
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


@tree.command(
    name="count_mrps",
    description="Count stat-block messages since the last session start in the mech-rp channels",
)
async def count_mrps(interaction: discord.Interaction):
    await interaction.response.defer()

    if interaction.guild is None:
        await interaction.followup.send("This command can only be used in a server.")
        return

    lines = ["**Stat-block messages since last session start:**"]
    total = 0

    for name in MRP_CHANNELS:
        channel = discord.utils.get(interaction.guild.text_channels, name=name)
        if channel is None:
            lines.append(f"  {name}: channel not found")
            continue

        count = 0
        marker_found = False
        try:
            async for message in channel.history(limit=None):
                if SESSION_START_MARKER in message.content.lower():
                    marker_found = True
                    break
                if is_stat_block(message.content):
                    count += 1
        except discord.Forbidden:
            lines.append(f"  {name}: no access")
            continue

        total += count
        if marker_found:
            lines.append(f"  {name}: {count}")
        else:
            lines.append(f"  {name}: {count} (no session marker — whole history)")

    lines.append(f"Total: {total}")
    await interaction.followup.send("\n".join(lines))


@tree.command(name="hello", description="Call the Path of Ages hello API and return its response")
async def hello(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(HELLO_ENDPOINT, json={"message": "Hello"}) as resp:
                data = await resp.json()
                if resp.status == 200:
                    await interaction.followup.send(data.get("message", str(data)))
                else:
                    error = data.get("error", f"Request failed with status {resp.status}")
                    await interaction.followup.send(f"Error: {error}")
    except aiohttp.ClientError as exc:
        await interaction.followup.send(f"Error contacting the API: {exc}")


if __name__ == "__main__":
    token = os.environ["DISCORD_BOT_TOKEN"]
    client.run(token)
