# ══════════════════════════════════════════════════════
#  cogs/doubts.py  —  Doubt Tagging and Tracking System
# ══════════════════════════════════════════════════════

import discord
from discord.ext import commands
import database as db
from datetime import datetime, timezone, timedelta
from cogs.economy import award_xp_and_coins

IST = timezone(timedelta(hours=5, minutes=30))


class Doubts(commands.Cog):
    """Cog for managing student doubts, tracking resolved statuses, and rewarding helpers."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def get_doubts_log_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        """Find or create the doubts-log channel on the server."""
        ch = discord.utils.get(guild.text_channels, name="doubts-log")
        if not ch:
            try:
                from config import SETUP_CATEGORY
                cat = discord.utils.get(guild.categories, name=SETUP_CATEGORY)
                ch = await guild.create_text_channel(
                    "doubts-log",
                    category=cat,
                    reason="Auto-created doubts-log channel"
                )
            except Exception:
                try:
                    ch = await guild.create_text_channel(
                        "doubts-log",
                        reason="Auto-created doubts-log channel"
                    )
                except Exception:
                    pass
        return ch

    # ── Commands ───────────────────────────────────────

    @commands.command(name="doubt")
    @commands.guild_only()
    async def create_doubt(self, ctx: commands.Context, *, topic: str) -> None:
        """Create a new doubt thread from your message."""
        user_id = ctx.author.id
        guild_id = ctx.guild.id
        now_ist = datetime.now(IST).isoformat()

        # Create thread
        try:
            thread_name = f"Doubt: {topic[:50]}"
            thread = await ctx.message.create_thread(name=thread_name, auto_archive_duration=1440)
        except discord.Forbidden:
            await ctx.reply("❌ I do not have permission to create threads in this channel!")
            return
        except Exception as e:
            await ctx.reply(f"❌ Failed to create thread: {e}")
            return

        # Save to database
        with db._connect() as con:
            con.execute(
                """
                INSERT INTO doubts (thread_id, guild_id, user_id, topic, status, created_at)
                VALUES (?, ?, ?, ?, 'open', ?)
                """,
                (thread.id, guild_id, user_id, topic, now_ist)
            )

        # Notify inside thread
        embed_thread = discord.Embed(
            title=f"❓ New Doubt Raised: {topic}",
            description=(
                f"**Author:** {ctx.author.mention}\n"
                f"**Status:** `OPEN` 🔴\n\n"
                f"Once your doubt is solved, please run `!solved @helper` inside this thread to close it and award XP! 🦾"
            ),
            color=0xE74C3C
        )
        embed_thread.set_footer(text="AGNoobies Doubt Desk")
        await thread.send(embed=embed_thread)

        # Post in doubts-log
        log_ch = await self.get_doubts_log_channel(ctx.guild)
        if log_ch:
            embed_log = discord.Embed(
                title="🔴 Doubt Created",
                description=(
                    f"**Topic:** {topic}\n"
                    f"**By:** {ctx.author.mention}\n"
                    f"**Thread Link:** {thread.mention}\n"
                    f"**Time:** `{datetime.now(IST).strftime('%I:%M %p IST')}`"
                ),
                color=0xE74C3C
            )
            await log_ch.send(embed=embed_log)

        await ctx.reply(f"✅ Doubt thread created successfully! Check {thread.mention} 🚀")

    @commands.command(name="solved")
    @commands.guild_only()
    async def resolve_doubt(self, ctx: commands.Context, helper: discord.Member = None) -> None:
        """Mark the active doubt thread as resolved, rewarding the helper."""
        if not isinstance(ctx.channel, discord.Thread):
            await ctx.reply("❌ This command must be run INSIDE an active doubt thread!")
            return

        thread_id = ctx.channel.id
        guild_id = ctx.guild.id

        # Verify doubt exists in db
        with db._connect() as con:
            doubt = con.execute("SELECT * FROM doubts WHERE thread_id = ?", (thread_id,)).fetchone()

        if not doubt:
            await ctx.reply("❌ This thread is not registered as a doubt in the database!")
            return

        if doubt["status"] == "resolved":
            await ctx.reply("ℹ️ This doubt is already marked as resolved! ✅")
            return

        now_ist = datetime.now(IST).isoformat()
        helper_id = helper.id if helper else None
        helper_mention = helper.mention if helper else "None"

        # Update DB
        with db._connect() as con:
            con.execute(
                """
                UPDATE doubts 
                SET status = 'resolved', resolved_at = ?, resolved_by = ? 
                WHERE thread_id = ?
                """,
                (now_ist, helper_id, thread_id)
            )

        # Award XP and coins to helper if present
        reward_msg = ""
        if helper:
            # helper gets +30 XP and +15 coins (roughly half XP)
            await award_xp_and_coins(self.bot, ctx.guild, helper.id, 30, 15, reason="helped_doubt")
            reward_msg = f"\n\n🎖️ **{helper.mention}** has been awarded **+30 XP** and **+15 coins** for helping! 🪙"

        # Send goodbye in thread
        embed_thread = discord.Embed(
            title="🟢 Doubt Resolved!",
            description=(
                f"This doubt has been successfully closed! 🚀\n"
                f"**Helper:** {helper_mention}{reward_msg}\n\n"
                f"Thank you for helping keep the grind alive! 💪"
            ),
            color=0x2ECC71
        )
        embed_thread.set_footer(text="AGNoobies Doubt Desk")
        await ctx.channel.send(embed=embed_thread)

        # Post in doubts-log
        log_ch = await self.get_doubts_log_channel(ctx.guild)
        if log_ch:
            embed_log = discord.Embed(
                title="🟢 Doubt Resolved",
                description=(
                    f"**Topic:** {doubt['topic']}\n"
                    f"**Raised by:** <@{doubt['user_id']}>\n"
                    f"**Resolved by:** {helper_mention}\n"
                    f"**Thread Link:** {ctx.channel.mention}"
                ),
                color=0x2ECC71
            )
            await log_ch.send(embed=embed_log)

        # Close/Archive thread
        try:
            await ctx.channel.edit(archived=True, locked=True, reason="Doubt resolved and closed")
        except discord.Forbidden:
            print(f"[Doubts] Failed to lock thread {ctx.channel.name} due to permissions.")

        # Trigger achievements check
        try:
            ach_cog = self.bot.get_cog("Achievements")
            if ach_cog:
                # Check for both author and helper
                await ach_cog.check_achievements(ctx.guild, doubt["user_id"])
                if helper_id:
                    await ach_cog.check_achievements(ctx.guild, helper_id)
        except Exception as e:
            print(f"[Doubts Achievements] Error: {e}")

    @commands.command(name="opendoubts")
    @commands.guild_only()
    async def open_doubts(self, ctx: commands.Context) -> None:
        """Display all currently unresolved doubts on the server."""
        guild_id = ctx.guild.id

        with db._connect() as con:
            rows = con.execute(
                "SELECT * FROM doubts WHERE guild_id = ? AND status = 'open' ORDER BY created_at DESC",
                (guild_id,)
            ).fetchall()

        if not rows:
            await ctx.reply("🎉 **Zero open doubts!** All problems have been successfully solved! Keep up the brilliant consistency! 🦾")
            return

        embed = discord.Embed(
            title="🔴 Unresolved doubts list",
            color=0xE74C3C,
            description="Here are the active doubts that need helpers! Jump in and solve them: ⚔️"
        )

        for row in rows[:15]: # Show top 15
            creator = ctx.guild.get_member(row["user_id"])
            creator_str = creator.mention if creator else f"User {row['user_id']}"
            created_dt = datetime.fromisoformat(row["created_at"])
            time_str = created_dt.strftime("%d %b, %I:%M %p")
            
            embed.add_field(
                name=f"❓ {row['topic'][:60]}",
                value=(
                    f"👤 **By:** {creator_str}\n"
                    f"📅 **Raised:** `{time_str}`\n"
                    f"🔗 **Thread:** <#{row['thread_id']}>"
                ),
                inline=False
            )

        embed.set_footer(text=f"Showing {min(len(rows), 15)} of {len(rows)} open doubts")
        await ctx.reply(embed=embed)

    @commands.command(name="mydoubts")
    @commands.guild_only()
    async def my_doubts(self, ctx: commands.Context) -> None:
        """Show your personal doubts history (resolved and open)."""
        user_id = ctx.author.id
        guild_id = ctx.guild.id

        with db._connect() as con:
            rows = con.execute(
                "SELECT * FROM doubts WHERE user_id = ? AND guild_id = ? ORDER BY created_at DESC",
                (user_id, guild_id)
            ).fetchall()

        if not rows:
            await ctx.reply("ℹ️ You haven't raised any doubts yet! Keep working hard!")
            return

        open_cnt = sum(1 for r in rows if r["status"] == "open")
        resolved_cnt = sum(1 for r in rows if r["status"] == "resolved")

        embed = discord.Embed(
            title=f"❓ Doubt History — {ctx.author.display_name}",
            description=f"🔴 **Open:** `{open_cnt}`  |  🟢 **Resolved:** `{resolved_cnt}`",
            color=0x3498DB
        )

        for row in rows[:10]: # limit to 10
            status_emoji = "🔴" if row["status"] == "open" else "🟢"
            resolved_by_str = ""
            if row["status"] == "resolved" and row["resolved_by"]:
                resolved_by_str = f"\n✅ **Helper:** <@{row['resolved_by']}>"
                
            embed.add_field(
                name=f"{status_emoji} Topic: {row['topic'][:60]}",
                value=(
                    f"🔗 **Thread:** <#{row['thread_id']}>\n"
                    f"📅 **Date:** `{row['created_at'][:10]}`{resolved_by_str}"
                ),
                inline=False
            )

        embed.set_footer(text="AGNoobies Doubt Tracking System")
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Doubts(bot))
