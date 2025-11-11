# Anthrax Infractions Bot

This project provides a Discord bot for staff to record and retrieve player infractions directly in Discord using slash commands. Infractions are stored in a Google Sheet for tracking and auditing.

---

## Features

- **/infraction**  
  Add a new infraction with the following fields:
  - Timestamp (saved in Eastern Time, format: `MM/DD/YYYY : h:mm AM/PM`)
  - Alderon Name
  - Alderon ID (must be exactly `000-000-000`)
  - Rule(s) Broken
  - Ticket ID
  - Verdict (Reminder, Strike, Warning)
  - Admin (filled automatically from the staff member’s Discord display name)
  - Player Informed? (Yes or No)

- **/callinfractions**  
  Retrieve all infractions for a given Alderon Name or Alderon ID. Results are returned as ephemeral messages so only the staff member sees them.

- **Access Control**  
  Only members with the configured staff role ID can use these commands.

  - **Google Sheets Integration**
    Infractions are logged in a sheet with enforced headers for easy viewing, editing, and storage.

---

## Prerequisites
Before you deploy or run locally, make sure you have:
- A Discord server where you have admin rights.
- A Google account with access to Google Sheets
- A hosting provider, such as Railway
- Python 3.10+ installed locally if you want to test before deploying.

---

## Environment Setup (.env)
### 1. Discord Setup
- Go to [Discord Developer Portal](https://discord.com/developers/applications).
- Copy the **Bot Token** → `DISCORD_TOKEN`.  
- Enable **Server Members Intent**.  
- Invite the bot with `applications.commands` and `bot` scopes.  
- Copy your server’s Guild ID → `DISCORD_GUILD_ID`.  
- Copy your staff role ID → `STAFF_ROLE_ID`.

### 2. Role IDs
- In Discord, enable **Developer Mode** (User Settings → Advanced → Developer Mode).
- Right-click your staff role → "Copy ID"
- Save this as your `STAFF_ROLE_ID`.
- Copy your server's Guild ID (right‑click server icon → “Copy ID”) and save as `DISCORD_GUILD_ID`.

### 3. Google Sheets Setup
- Create a new Google Sheet
- Save the name of this sheet as `GSHEET_NAME`
- Save the name of the tab as `GSHEET_TAB`
- In row 1, add headers exactly as follows:
  Timestamp | Alderon Name | Alderon ID | Rule(s) Broken | Ticket ID | Verdict | Admin | Player Informed?
- In Google Cloud Console, create a **Service Account** and generate a JSON key.
- Share the sheet with the service account email (Editor access)
- Save the JSON contents as `GOOGLE_CREDENTIALS_JSON`

### 4. Finalize .env
- Create a `.env` file in the project root:
```bash
DISCORD_TOKEN=your_bot_token_here
  DISCORD_GUILD_ID=your_guild_id
  STAFF_ROLE_ID=staff_role_id
  GSHEET_NAME=sheet_name
  GSHEET_TAB=tab_name
  GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}
```

## Dependencies
```bash
pip install -r requirements.txt
```

## Example Usage
- Add an infraction
`/infraction alderon_name:Wolfie alderon_ID:123-456-789 rules_broken:"Chat Spam" ticket_ID:T-123 verdict:Strike player_informed:Yes`

- Retrieve infractions
`/callinfractions alderon_name:Wolfie`

