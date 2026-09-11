import os
import threading
from flask import Flask
import discord
from discord import app_commands
from discord.ext import commands

# --- Web Server to Keep Render Awake ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_web_server():
    # Render automatically assigns a PORT variable; falls back to 10000 locally
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_web_server)
    t.daemon = True
    t.start()

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuration IDs
CONFIG = {
    "ADMIN_ROLE": 1547959429679292456,
    "PARTNER_ROLE": 1547961683178160189,
    "PARTNER_AD_CHANNEL": 1547665434587828225,
    "CATEGORIES": {
        "PARTNER": 1547965675165720606,
        "APPLY": 1547965741054034011,
        "CONCERNS": 1547965793315332187,
    },
    "COLOR": discord.Color.from_rgb(128, 128, 128)  # Gray
}

# Helper function to create ticket channels with permissions
async def create_ticket_channel(guild: discord.Guild, user: discord.Member, category_id: int):
    category = guild.get_channel(category_id)
    admin_role = guild.get_role(CONFIG["ADMIN_ROLE"])
    
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(
            view_channel=True, 
            send_messages=True, 
            attach_files=True, 
            embed_links=True
        ),
    }
    
    if admin_role:
        overwrites[admin_role] = discord.PermissionOverwrite(
            view_channel=True, 
            send_messages=True, 
            attach_files=True, 
            embed_links=True
        )

    return await guild.create_text_channel(
        name=f"ticket-{user.name}",
        category=category,
        overwrites=overwrites
    )

# --- Modals (Forms) ---
class PartnerForm(discord.ui.Modal, title="Partner Application"):
    ad = discord.ui.TextInput(
        label="Server Ad (No @everyone/@here)",
        style=discord.TextStyle.paragraph,
        required=True
    )
    rep2 = discord.ui.TextInput(
        label="2nd Rep Username (if sub 200 members)",
        style=discord.TextStyle.short,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        ad_text = self.ad.value
        if "@everyone" in ad_text or "@here" in ad_text:
            await interaction.response.send_message(
                "Invalid server ad! Hidden or explicit `@everyone` / `@here` pings are not allowed.",
                ephemeral=True
            )
            return

        ad_channel = interaction.guild.get_channel(CONFIG["PARTNER_AD_CHANNEL"])
        if ad_channel:
            await ad_channel.send(ad_text)

        partner_role = interaction.guild.get_role(CONFIG["PARTNER_ROLE"])
        if partner_role:
            await interaction.user.add_roles(partner_role)

        await interaction.response.send_message("Server ad successfully submitted and role granted!", ephemeral=True)

class NetworkForm(discord.ui.Modal, title="Network Application"):
    link = discord.ui.TextInput(
        label="Server Link",
        style=discord.TextStyle.short,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        admin_role = CONFIG["ADMIN_ROLE"]
        await interaction.response.send_message(
            f"<@&{admin_role}> check for network.\nkindly wαit pαtiently. thank you sm !"
        )

# --- Requirement Buttons ---
class PartnerReqsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="reqs αre met !", style=discord.ButtonStyle.secondary, custom_id="btn_partner_modal")
    async def reqs_met(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PartnerForm())

class NetworkReqsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="reqs αre met !", style=discord.ButtonStyle.secondary, custom_id="btn_network_modal")
    async def reqs_met(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NetworkForm())

# --- Option Selection Buttons ---
class OptionButtonsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="pαrtner", style=discord.ButtonStyle.secondary, custom_id="btn_partner_reqs")
    async def partner_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description=(
                "_ _\n   ` pαrtner reqs ; `\n_ _\n"
                "                **for the community**\n"
                "> <:w_dot:1534807724947406909>sfw, ssfw, ntox, stox only \n"
                "> <:w_dot:1534807724947406909> must follow discord tos\n"
                "> <:w_dot:1534807724947406909>must not engαge in αny,\n       nuking, doxxing, or rαids\n_ _\n"
                "                **for the retαils**\n"
                "> <:w_dot:1534807724947406909>must hαve α  vouch  channel\n"
                "> <:w_dot:1534807724947406909>at leαst 30 dαys old / serving\n"
                "> <:w_dot:1534807724947406909>must show rules & legitimacy\n_ _ \n"
                "~~                                                                                ~~\n"
                "> <:w_dot:1534807724947406909> one - two rep(s) per sv, must\n"
                "     must not hαve  <@&1547961683178160189> role \n"
                "> <:w_dot:1534807724947406909> remove hidden pings. thank u!\n_ _"
            ),
            color=CONFIG["COLOR"]
        )
        await interaction.response.send_message(embed=embed, view=PartnerReqsView())

    @discord.ui.button(label="network", style=discord.ButtonStyle.secondary, custom_id="btn_network_reqs")
    async def network_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description=(
                "_ _\n   ` network reqs ; `\n_ _\n"
                "                **for the community**\n"
                "> <:w_dot:1534807724947406909>sfw, ssfw, ntox, stox only \n"
                "> <:w_dot:1534807724947406909> must follow discord tos\n"
                "> <:w_dot:1534807724947406909>must not engαge in αny,\n       nuking, doxxing, or rαids\n_ _\n"
                "~~                                                                                ~~\n_ _"
            ),
            color=CONFIG["COLOR"]
        )
        await interaction.response.send_message(embed=embed, view=NetworkReqsView())

# --- Main Select Menu Panel ---
class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="ps / net", description="partner with gg.weeknd", value="partner"),
            discord.SelectOption(label="apply", description="be pαrt of our teαm !", value="apply"),
            discord.SelectOption(label="concerns", description="diαl for αssistαnce !", value="concerns"),
        ]
        super().__init__(placeholder="Choose ticket type...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "give us 5 seconds to create your ticket! <a:loading_bg:953333008130244678>", 
            ephemeral=True
        )

        val = self.values[0]
        cat_id = CONFIG["CATEGORIES"]["PARTNER"]
        if val == "apply":
            cat_id = CONFIG["CATEGORIES"]["APPLY"]
        elif val == "concerns":
            cat_id = CONFIG["CATEGORIES"]["CONCERNS"]

        channel = await create_ticket_channel(interaction.guild, interaction.user, cat_id)

        if val == "partner":
            embed = discord.Embed(
                description=(
                    "_ _\n            tickette booth . . .\n"
                    "> reαdy to be pαrtners with **gg.weeknd?**\n"
                    "> click on the respective buttons to continue!\n_ _"
                ),
                color=CONFIG["COLOR"]
            )
            await channel.send(embed=embed, view=OptionButtonsView())
        else:
            embed = discord.Embed(
                description=(
                    "_ _\n     thαnk you for contαcting us !\n"
                    "     kindly  wαit  for our stαffs  to\n"
                    "     αssist  you  with  this  mαtter\n_ _\n"
                    "> use .ping after 2 hrs w no response"
                ),
                color=CONFIG["COLOR"]
            )
            await channel.send(embed=embed)

class TicketSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

# --- Slash Command ---
@bot.tree.command(name="ticket-setup", description="Setup the ticket panel")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Ticket Support",
        description="Select an option below to open a ticket.",
        color=CONFIG["COLOR"]
    )
    await interaction.response.send_message(embed=embed, view=TicketSelectView())

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# Start background web server & run bot
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
