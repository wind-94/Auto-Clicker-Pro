import asyncio
import threading
import time
import datetime
import discord
from discord.ext import commands

class DiscordRemoteBot(threading.Thread):
    def __init__(self, token, auth_id, channel_id, app_instance):
        super().__init__(daemon=True)
        self.token = token
        self.auth_id = str(auth_id)
        self.channel_id = str(channel_id) if channel_id else None
        self.app = app_instance

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        intents = discord.Intents.default()
        intents.message_content = True
        bot = commands.Bot(command_prefix="?", intents=intents)

        @bot.event
        async def on_ready():
            try:
                synced = await bot.tree.sync()
                print(f"[Remote] Authenticated as {bot.user}. Synced {len(synced)} slash commands.")
            except Exception as e:
                print(f"[Remote] Failed to sync slash commands: {e}")

        # ── SLASH COMMAND: /setchannel ──
        @bot.tree.command(name="setchannel", description="Lock the auto-clicker commands to this specific channel.")
        async def set_channel(interaction: discord.Interaction):
            if str(interaction.user.id) != self.auth_id:
                await interaction.response.send_message("❌ **Unauthorized:** You do not have permission to configure this bot.", ephemeral=True)
                return
            
            self.channel_id = str(interaction.channel_id)
            self.app.update_channel_signal.emit(self.channel_id)
            await interaction.response.send_message(f"✅ **Channel Locked!** Commands will now only be accepted in <#{self.channel_id}>.")

        # ── SLASH COMMAND: /start ──
        @bot.tree.command(name="start", description="Remotely start the Auto-Clicker.")
        async def start_clicker(interaction: discord.Interaction):
            if self.channel_id and str(interaction.channel_id) != self.channel_id:
                await interaction.response.send_message(f"❌ Commands are locked to <#{self.channel_id}>.", ephemeral=True)
                return 
                
            if str(interaction.user.id) != self.auth_id:
                await interaction.response.send_message("❌ **Unauthorized:** You do not have permission to start this machine.", ephemeral=True)
                return

            if self.app.is_running:
                await interaction.response.send_message("ℹ️ Auto-Clicker is **already running**.", ephemeral=True)
                return

            # Check if the host PC has actually been set up correctly
            if not self.app.watch_region or not self.app.click_pos:
                await interaction.response.send_message("❌ **Cannot Start:** Watch Region or Click Position is not set on the host PC.", ephemeral=True)
                return
                
            try:
                int(self.app.main_pg.target.text())
                float(self.app.main_pg.interval.text())
            except ValueError:
                await interaction.response.send_message("❌ **Cannot Start:** Invalid target or interval values on the host PC.", ephemeral=True)
                return

            # Send signal to safely start the UI
            self.app.start_signal.emit()
            await interaction.response.send_message("🚀 **Auto-Clicker has been successfully started!**")

        # ── SLASH COMMAND: /stop ──
        @bot.tree.command(name="stop", description="Forcefully halt the Auto-Clicker machine.")
        async def stop_clicker(interaction: discord.Interaction):
            if self.channel_id and str(interaction.channel_id) != self.channel_id:
                await interaction.response.send_message(f"❌ Commands are locked to <#{self.channel_id}>.", ephemeral=True)
                return 
                
            if str(interaction.user.id) != self.auth_id:
                await interaction.response.send_message("❌ **Unauthorized:** You do not have permission to stop this machine.", ephemeral=True)
                return
            
            if self.app.is_running:
                self.app.stop_signal.emit()
                await interaction.response.send_message("🛑 **Auto-Clicker has been successfully halted.**")
            else:
                await interaction.response.send_message("ℹ️ Auto-Clicker is already idle.", ephemeral=True)

        # ── SLASH COMMAND: /time ──
        @bot.tree.command(name="time", description="Check how long the Auto-Clicker has been running.")
        async def check_time(interaction: discord.Interaction):
            if self.channel_id and str(interaction.channel_id) != self.channel_id:
                await interaction.response.send_message(f"❌ Commands are locked to <#{self.channel_id}>.", ephemeral=True)
                return 
                
            if str(interaction.user.id) != self.auth_id:
                await interaction.response.send_message("❌ **Unauthorized.**", ephemeral=True)
                return

            if not self.app.is_running or not self.app.bot_start:
                await interaction.response.send_message("⏸️ The Auto-Clicker is currently **offline/idle**.")
            else:
                uptime_seconds = int(time.time() - self.app.bot_start)
                uptime_str = str(datetime.timedelta(seconds=uptime_seconds))
                start_ts = int(self.app.bot_start)
                
                await interaction.response.send_message(
                    f"⏱️ **Status: RUNNING**\n"
                    f"Started: <t:{start_ts}:R>\n"
                    f"Uptime: `{uptime_str}`"
                )

        try:
            loop.run_until_complete(bot.start(self.token))
        except Exception as e:
            print(f"[Remote] Failed to start listener: {e}")