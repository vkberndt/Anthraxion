import re
import pytz
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from config import (
    DISCORD_TOKEN, DISCORD_GUILD_ID, STAFF_ROLE_ID,
    GSHEET_NAME, GSHEET_TAB, load_google_credentials_dict
)
from sheets_client import SheetsClient, SHEET_HEADERS

# Restrict command usage to members with the configured staff role.
def user_has_staff_role(interaction: discord.Interaction) -> bool:
    if not isinstance(interaction.user, discord.Member):
        return False
    return any(role.id == STAFF_ROLE_ID for role in interaction.user.roles)

# Alderon ID must strictly match 000-000-000.
ALDERON_ID_PATTERN = re.compile(r"^\d{3}-\d{3}-\d{3}$")

def is_valid_alderon_id(value: str) -> bool:
    return bool(ALDERON_ID_PATTERN.match(value or ""))

def validate_verdict(value: str) -> bool:
    return value in {"Reminder", "Strike", "Warning"}

def validate_player_informed(value: str) -> bool:
    return value in {"Yes", "No"}

def get_est_timestamp() -> str:
    est = pytz.timezone("America/New_York")
    now_est = datetime.now(est)
    # Format: Month/Day/Year : Time EST (12-hour with AM/PM)
    return now_est.strftime("%m/%d/%Y : %I:%M %p")

class AnthraxBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True

        super().__init__(command_prefix="!", intents=intents)

        creds = load_google_credentials_dict()
        self.sheets = SheetsClient(credentials_dict=creds, sheet_name=GSHEET_NAME, tab_name=GSHEET_TAB)

    async def setup_hook(self):
        if DISCORD_GUILD_ID:
            self.tree.copy_global_to(guild=discord.Object(id=DISCORD_GUILD_ID))
            await self.tree.sync(guild=discord.Object(id=DISCORD_GUILD_ID))
        else:
            await self.tree.sync()

bot = AnthraxBot()

VERDICT_CHOICES = [
    app_commands.Choice(name="Reminder", value="Reminder"),
    app_commands.Choice(name="Strike", value="Strike"),
    app_commands.Choice(name="Warning", value="Warning"),
    app_commands.Choice(name="Ban", value="Ban"),
]

PLAYER_INFORMED_CHOICES = [
    app_commands.Choice(name="Yes", value="Yes"),
    app_commands.Choice(name="No", value="No"),
]

@bot.tree.command(name="infraction", description="Add a player infraction to the sheet.")
@app_commands.describe(
    alderon_name="Player's Alderon Name",
    alderon_id="Player's Alderon ID in 000-000-000 format.",
    rules_broken="Rule(s) broken",
    ticket_id="Associated ticket ID",
    verdict="Outcome: Reminder, Strike, or Warning",
    player_informed="Whether the player was informed: Yes or No"
)
@app_commands.choices(verdict=VERDICT_CHOICES, player_informed=PLAYER_INFORMED_CHOICES)
async def add_infraction(
    interaction: discord.Interaction,
    alderon_name: str,
    alderon_id: str,
    rules_broken: str,
    ticket_id: str,
    verdict: app_commands.Choice[str],
    player_informed: app_commands.Choice[str],
):
    if not user_has_staff_role(interaction):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    if not is_valid_alderon_id(alderon_id):
        await interaction.response.send_message("Alderon ID must be exactly 000-000-000.", ephemeral=True)
        return

    if not validate_verdict(verdict.value) or not validate_player_informed(player_informed.value):
        await interaction.response.send_message("Invalid verdict or player informed value.", ephemeral=True)
        return

    timestamp = get_est_timestamp()
    admin_name = interaction.user.display_name

    row = [
        timestamp,
        alderon_name.strip(),
        alderon_id,
        rules_broken.strip(),
        ticket_id.strip(),
        verdict.value,
        admin_name,
        player_informed.value
    ]

    try:
        bot.sheets.append_infraction_row(row)
    except Exception as e:
        await interaction.response.send_message(f"Failed to write to sheet: {e}", ephemeral=True)
        return

    await interaction.response.send_message("Infraction recorded.", ephemeral=True)

@bot.tree.command(name="callinfractions", description="Retrieve infractions by Alderon Name or Alderon ID.")
@app_commands.describe(
    alderon_name="Player's Alderon Name",
    alderon_id="Player's Alderon ID in 000-000-000 format"
)
async def call_infractions(
    interaction: discord.Interaction,
    alderon_name: str = None,
    alderon_id: str = None
):
    if not user_has_staff_role(interaction):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    if not alderon_name and not alderon_id:
        await interaction.response.send_message("Provide an Alderon Name or Alderon ID.", ephemeral=True)
        return

    if alderon_id and not is_valid_alderon_id(alderon_id):
        await interaction.response.send_message("Alderon ID must be exactly 000-000-000.", ephemeral=True)
        return

    try:
        rows = bot.sheets.query_by_alderon(name=alderon_name, alderon_id=alderon_id)
    except Exception as e:
        await interaction.response.send_message(f"Failed to query sheet: {e}", ephemeral=True)
        return

    if not rows:
        await interaction.response.send_message("No infractions found.", ephemeral=True)
        return

    idx = {h: i for i, h in enumerate(SHEET_HEADERS)}
    lines = []
    for r in rows:
        lines.append(
            f"{r[idx['Timestamp']]} | {r[idx['Alderon Name']]} | {r[idx['Alderon ID']]} | "
            f"{r[idx['Verdict']]} | {r[idx['Player Informed?']]} | "
            f"Ticket {r[idx['Ticket ID']]} | {r[idx['Rule(s) Broken']]}"
        )

    output = "\n".join(lines)
    if len(output) > 1800:
        output = "\n".join(lines[:25]) + f"\n...and {len(lines) - 25} more."

    await interaction.response.send_message(output, ephemeral=True)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)