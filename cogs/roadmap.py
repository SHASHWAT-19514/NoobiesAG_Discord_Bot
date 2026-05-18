# ══════════════════════════════════════════════════════
#  cogs/roadmap.py  —  Topic Roadmap Tracker
# ══════════════════════════════════════════════════════

import discord
from discord.ext import commands
import database as db
from datetime import datetime, timezone, timedelta
from cogs.economy import award_xp_and_coins

IST = timezone(timedelta(hours=5, minutes=30))

ROADMAP = {
    "Phase 1: Foundations": [
        "Arrays", "Strings", "Sorting", "Binary Search", "Two Pointers", "Sliding Window"
    ],
    "Phase 2: Intermediate": [
        "Recursion", "Backtracking", "Prefix Sums", "Hashing", "Stack", "Queue"
    ],
    "Phase 3: Advanced structures": [
        "Graphs", "BFS", "DFS", "Shortest Path", "Trees", "Binary Trees"
    ],
    "Phase 4: Expert CP topics": [
        "Dynamic Programming", "Greedy", "Segment Trees", "Fenwick Tree", "Trie"
    ]
}

ALL_TOPICS = []
for phase, topics in ROADMAP.items():
    ALL_TOPICS.extend(topics)


class Roadmap(commands.Cog):
    """Cog for tracking CP Topic learning roadmaps."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── Commands ───────────────────────────────────────

    @commands.command(name="roadmap")
    @commands.guild_only()
    async def view_roadmap(self, ctx: commands.Context) -> None:
        """Display the complete CP learning roadmap checklist."""
        user_id = ctx.author.id
        guild_id = ctx.guild.id

        with db._connect() as con:
            completed_rows = con.execute(
                "SELECT topic FROM roadmap_progress WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            ).fetchall()
        
        completed_topics = {r["topic"] for r in completed_rows}

        embed = discord.Embed(
            title="🎯 Competitive Programming Learning Roadmap",
            description="Grind these topics in order to build top-tier consistency and skill! 🚀",
            color=0x3498DB
        )

        for phase, topics in ROADMAP.items():
            checklist = []
            for t in topics:
                status = "✅" if t in completed_topics else "⬜"
                checklist.append(f"{status} **{t}**")
            
            embed.add_field(
                name=f"🏆 {phase}",
                value="\n".join(checklist),
                inline=False
            )

        embed.set_footer(text="AGNoobies CP Roadmap • Use !done <topic> to complete")
        await ctx.reply(embed=embed)

    @commands.command(name="done")
    @commands.guild_only()
    async def mark_done(self, ctx: commands.Context, *, topic_name: str) -> None:
        """Mark a roadmap topic as completed and earn XP/Coins."""
        user_id = ctx.author.id
        guild_id = ctx.guild.id

        # Normalize and match topic
        target = topic_name.strip().lower()
        matched_topic = None
        for t in ALL_TOPICS:
            if t.lower() == target or t.lower().replace(" ", "") == target.replace(" ", ""):
                matched_topic = t
                break

        if not matched_topic:
            # Let's list a few options
            await ctx.reply(
                f"❌ Topic **\"{topic_name}\"** not found in the roadmap!\n"
                f"Please ensure it matches one of the standard topics like `Binary Search` or `Graphs`."
            )
            return

        # Check if already completed
        with db._connect() as con:
            existing = con.execute(
                "SELECT * FROM roadmap_progress WHERE user_id = ? AND guild_id = ? AND topic = ?",
                (user_id, guild_id, matched_topic)
            ).fetchone()

        if existing:
            await ctx.reply(f"ℹ️ Topic **{matched_topic}** has already been completed! ✅ Keep up the grind!")
            return

        # Save to DB
        now_ist = datetime.now(IST).isoformat()
        with db._connect() as con:
            con.execute(
                "INSERT INTO roadmap_progress (user_id, guild_id, topic, completed_at) VALUES (?, ?, ?, ?)",
                (user_id, guild_id, matched_topic, now_ist)
            )

        # Give 50 XP and 10 coins
        await award_xp_and_coins(self.bot, ctx.guild, user_id, 50, 10, reason="roadmap_done")

        embed = discord.Embed(
            title="🎯 Topic Completed!",
            description=(
                f"🎉 **Congratulations!** You've conquered **{matched_topic}**!\n\n"
                f"> ⭐ **XP Gained:** `+50 XP` (Boosts apply)\n"
                f"> 🪙 **Coins Gained:** `+10 coins`"
            ),
            color=0x2ECC71
        )
        embed.set_footer(text="AGNoobies CP Roadmap")
        await ctx.reply(embed=embed)

        # Trigger achievements check
        try:
            ach_cog = self.bot.get_cog("Achievements")
            if ach_cog:
                await ach_cog.check_achievements(ctx.guild, user_id)
        except Exception as e:
            print(f"[Roadmap Achievements] Error checking: {e}")

    @commands.command(name="mytopics")
    @commands.guild_only()
    async def view_my_topics(self, ctx: commands.Context) -> None:
        """Show your roadmap completion progress statistics."""
        user_id = ctx.author.id
        guild_id = ctx.guild.id

        with db._connect() as con:
            completed_rows = con.execute(
                "SELECT topic FROM roadmap_progress WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            ).fetchall()

        completed_topics = {r["topic"] for r in completed_rows}
        
        embed = discord.Embed(
            title=f"📊 Roadmap Progress — {ctx.author.display_name}",
            color=0x9B59B6
        )

        total_done = 0
        total_topics = len(ALL_TOPICS)

        for phase, topics in ROADMAP.items():
            done = sum(1 for t in topics if t in completed_topics)
            total_done += done
            
            from utils.helpers import progress_bar
            bar = progress_bar(done, len(topics), length=10)
            embed.add_field(
                name=f"🏆 {phase}",
                value=f"`{bar}` ({done}/{len(topics)} completed)",
                inline=False
            )

        percentage = round((total_done / total_topics) * 100) if total_topics > 0 else 100
        overall_bar = progress_bar(total_done, total_topics, length=12)
        
        embed.description = (
            f"💪 **Overall Roadmap Progress:**\n"
            f"`{overall_bar}` **{percentage}%** ({total_done}/{total_topics} topics done)"
        )
        embed.set_footer(text="AGNoobies CP Roadmap Tracker")
        await ctx.reply(embed=embed)

    @commands.command(name="tplearnors", aliases=["toplearners"])
    @commands.guild_only()
    async def top_learners(self, ctx: commands.Context) -> None:
        """Show top 5 users on the server by roadmap topics completed."""
        with db._connect() as con:
            rows = con.execute(
                """
                SELECT user_id, COUNT(topic) as count 
                FROM roadmap_progress 
                WHERE guild_id = ? 
                GROUP BY user_id 
                ORDER BY count DESC 
                LIMIT 5
                """,
                (ctx.guild.id,)
            ).fetchall()

        if not rows:
            await ctx.reply("No roadmap topic progress recorded on this server yet.")
            return

        embed = discord.Embed(
            title="📚 TOP LEARNERS LEADERBOARD",
            color=0xF1C40F,
            description="```\n#   Name                 Completed Topics\n" + "─" * 40 + "```"
        )

        lines = []
        medals = ["🥇", "🥈", "🥉"]
        for idx, row in enumerate(rows):
            medal = medals[idx] if idx < 3 else f"`{idx + 1:2d}.`"
            member = ctx.guild.get_member(row["user_id"])
            name = member.display_name[:18] if member else f"User {row['user_id']}"
            lines.append(f"{medal}  **{name:<18}** — **{row['count']}/{len(ALL_TOPICS)}** completed")

        embed.add_field(name="\u200b", value="\n".join(lines), inline=False)
        embed.set_footer(text="AGNoobies CP Roadmap")
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Roadmap(bot))
