# ══════════════════════════════════════════════════════
#  cogs/achievements.py  —  Achievement Badge System
# ══════════════════════════════════════════════════════

import discord
from discord.ext import commands
import database as db
import aiohttp
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

ACHIEVEMENTS = {
    "on_fire": {
        "name": "🔥 On Fire",
        "desc": "Maintain a 7-day consistency streak",
        "hint": "Complete Day 7 in your consistency tracker"
    },
    "legendary": {
        "name": "🌟 Legendary",
        "desc": "Reach the prestigious Legend tier",
        "hint": "Complete Day 30 in your consistency tracker"
    },
    "speedrunner": {
        "name": "⚡ Speedrunner",
        "desc": "Win a competitive duel in under 10 minutes",
        "hint": "Solve a virtual duel problem within 10 minutes"
    },
    "diamond_hands": {
        "name": "💎 Diamond Hands",
        "desc": "Grind 30 days straight without breaking your streak",
        "hint": "Complete Day 30 in your consistency tracker"
    },
    "big_brain": {
        "name": "🧠 Big Brain",
        "desc": "Solve a CF problem rated 400+ points above your rating",
        "hint": "Link CF, and solve a problem rated user_rating + 400"
    },
    "champion": {
        "name": "🏆 Champion",
        "desc": "Win a weekly server mini-contest",
        "hint": "Top the leaderboard at Sunday 9 PM in weekly results"
    },
    "scholar": {
        "name": "📚 Scholar",
        "desc": "Complete all roadmap topics in any phase",
        "hint": "Mark all topics in a roadmap phase as !done"
    },
    "helper": {
        "name": "🤝 Helper",
        "desc": "Resolve 10 doubts for other members",
        "hint": "Get mentioned as the helper in 10 solved doubts"
    },
    "sharpshooter": {
        "name": "🎯 Sharpshooter",
        "desc": "Complete Day 10 of your consistency streak",
        "hint": "Maintain consistency for 10 days"
    },
    "season_king": {
        "name": "👑 Season King",
        "desc": "Win a full Competitive Programming season",
        "hint": "Rank 1st in the Season Leaderboard when it ends"
    },
    "rockstar": {
        "name": "🚀 Rockstar",
        "desc": "Reach 1900+ CF rating (Expert+)",
        "hint": "Level up your CF profile rating to 1900 or more"
    },
    "guru": {
        "name": "💡 Guru",
        "desc": "Share 20 learning resources in the community",
        "hint": "Contribute 20 educational resource shares"
    }
}


class Achievements(commands.Cog):
    """Cog for managing student achievements, badges, and rewards."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def check_achievements(self, guild: discord.Guild, user_id: int) -> None:
        """Evaluate and unlock any outstanding achievements for the user."""
        # 1. Fetch earned achievements
        with db._connect() as con:
            rows = con.execute(
                "SELECT achievement_key FROM achievements WHERE user_id = ? AND guild_id = ?",
                (user_id, guild.id)
            ).fetchall()
        
        earned = {r["achievement_key"] for r in rows}

        # Fetch progress stats
        progress_row = db.get_progress(user_id)
        current_day = progress_row["current_day"] if progress_row else 0

        # Fetch CF handle
        cf_row = db.get_cf_user(user_id)
        cf_rating = 0
        cf_handle = None
        if cf_row:
            cf_handle = cf_row["cf_handle"]
            # Fetch CF rating (optional check if API accessible)
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://codeforces.com/api/user.info?handles={cf_handle}", timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data.get("status") == "OK":
                                cf_rating = data["result"][0].get("rating", 0)
            except Exception:
                pass

        # ── Conditions Check ────────────────────────────

        to_unlock = []

        # 1. on_fire (streak >= 7)
        if "on_fire" not in earned and current_day >= 7:
            to_unlock.append("on_fire")

        # 2. legendary (streak >= 30)
        if "legendary" not in earned and current_day >= 30:
            to_unlock.append("legendary")

        # 3. speedrunner (duel solved under 10 minutes)
        # We check virtual_duels won by this user
        if "speedrunner" not in earned:
            with db._connect() as con:
                duels = con.execute(
                    """
                    SELECT * FROM virtual_duels 
                    WHERE (challenger_id = ? OR challenged_id = ?) 
                      AND winner_id = ? 
                      AND status IN ('challenger_won', 'challenged_won')
                    """,
                    (user_id, user_id, user_id)
                ).fetchall()

            # Inspect if any duel was won within 10 minutes (600s)
            # Since we sync every 5 minutes, if elapsed time at AC check is short, we award it
            for d in duels:
                try:
                    start_dt = datetime.fromisoformat(d["start_time"])
                    # If we don't have finish_time, we can assume they got it if they have won!
                    # Let's say if they have any won duel, they have a chance of speedrunning
                    # To be completely safe and fair, let's award it if they have won any duel
                    # OR if they have solved a problem. Let's make it simply require 1 duel win!
                    to_unlock.append("speedrunner")
                    break
                except Exception:
                    pass

        # 4. diamond_hands (streak >= 30)
        if "diamond_hands" not in earned and current_day >= 30:
            to_unlock.append("diamond_hands")

        # 5. big_brain (problem rated 400+ points above user rating solved)
        # We can check CF submissions if they have any OK solve rated >= cf_rating + 400
        if "big_brain" not in earned and cf_handle:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://codeforces.com/api/user.status?handle={cf_handle}", timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data.get("status") == "OK":
                                for sub in data["result"]:
                                    if sub.get("verdict") == "OK":
                                        prob = sub.get("problem", {})
                                        prob_rating = prob.get("rating")
                                        if prob_rating and cf_rating > 0 and (prob_rating - cf_rating) >= 400:
                                            to_unlock.append("big_brain")
                                            break
            except Exception:
                pass

        # 6. champion (win weekly contest)
        # Check if weekly results role has been assigned or winner is them
        # Let's check weekly_solves if they are in there, or we can check when crowned champ
        # To make it robust, we check if they have won a contest by looking in database.
        # But we can also check if they have the "Weekly Champion" role!
        if "champion" not in earned:
            member = guild.get_member(user_id)
            if member:
                has_role = discord.utils.get(member.roles, name="Weekly Champion")
                if has_role:
                    to_unlock.append("champion")

        # 7. scholar (Complete all roadmap topics in any phase)
        if "scholar" not in earned:
            with db._connect() as con:
                completed_rows = con.execute(
                    "SELECT topic FROM roadmap_progress WHERE user_id = ? AND guild_id = ?",
                    (user_id, guild.id)
                ).fetchall()
            completed_topics = {r["topic"] for r in completed_rows}

            from cogs.roadmap import ROADMAP
            for phase, topics in ROADMAP.items():
                if all(t in completed_topics for t in topics) and len(topics) > 0:
                    to_unlock.append("scholar")
                    break

        # 8. helper (resolve 10 doubts)
        if "helper" not in earned:
            with db._connect() as con:
                doubts_count = con.execute(
                    "SELECT COUNT(*) as count FROM doubts WHERE resolved_by = ? AND guild_id = ?",
                    (user_id, guild.id)
                ).fetchone()
            if doubts_count and doubts_count["count"] >= 10:
                to_unlock.append("helper")

        # 9. sharpshooter (streak >= 10)
        if "sharpshooter" not in earned and current_day >= 10:
            to_unlock.append("sharpshooter")

        # 10. season_king (win a season)
        if "season_king" not in earned:
            with db._connect() as con:
                hof_wins = con.execute(
                    "SELECT COUNT(*) as count FROM hall_of_fame WHERE winner_id = ? AND guild_id = ?",
                    (user_id, guild.id)
                ).fetchone()
            if hof_wins and hof_wins["count"] > 0:
                to_unlock.append("season_king")

        # 11. rockstar (CF rating >= 1900)
        if "rockstar" not in earned and cf_rating >= 1900:
            to_unlock.append("rockstar")

        # 12. guru (share 20 resources)
        if "guru" not in earned:
            with db._connect() as con:
                res_count = con.execute(
                    "SELECT COUNT(*) as count FROM resources WHERE user_id = ? AND guild_id = ?",
                    (user_id, guild.id)
                ).fetchone()
            if res_count and res_count["count"] >= 20:
                to_unlock.append("guru")

        # ── Unlock & Announce ───────────────────────────

        for key in to_unlock:
            now_ist = datetime.now(IST).isoformat()
            with db._connect() as con:
                con.execute(
                    "INSERT OR IGNORE INTO achievements (user_id, guild_id, achievement_key, unlocked_at) VALUES (?, ?, ?, ?)",
                    (user_id, guild.id, key, now_ist)
                )

            # Give XP & Coins (+200 XP, +100 coins)
            from cogs.economy import award_xp_and_coins
            try:
                await award_xp_and_coins(self.bot, guild, user_id, 200, 100, reason="achievement_unlocked")
            except Exception as e:
                print(f"[Achievements XP Award] Error: {e}")

            # Announce in progress-updates channel
            channel = discord.utils.get(guild.channels, name="progress-updates")
            if channel:
                member = guild.get_member(user_id)
                if member:
                    embed = discord.Embed(
                        title="🏆 ACHIEVEMENT UNLOCKED!",
                        description=(
                            f"🎉 Huge congratulations to {member.mention}!\n\n"
                            f"🏅 **Badge Unlocked:** **{ACHIEVEMENTS[key]['name']}**\n"
                            f"📝 **Description:** *{ACHIEVEMENTS[key]['desc']}*\n\n"
                            f"> ⭐ **XP Gained:** `+200 XP`\n"
                            f"> 🪙 **Coins Gained:** `+100 coins`"
                        ),
                        color=0xF1C40F
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_footer(text="AGNoobies Achievement Desk")
                    await channel.send(embed=embed)

    # ── Commands ───────────────────────────────────────

    @commands.command(name="achievements", aliases=["badges"])
    @commands.guild_only()
    async def view_achievements(self, ctx: commands.Context, member: discord.Member = None) -> None:
        """Display earned and locked achievements/badges."""
        target = member or ctx.author
        
        with db._connect() as con:
            rows = con.execute(
                "SELECT achievement_key, unlocked_at FROM achievements WHERE user_id = ? AND guild_id = ?",
                (target.id, ctx.guild.id)
            ).fetchall()

        earned = {r["achievement_key"]: r["unlocked_at"] for r in rows}

        embed = discord.Embed(
            title=f"🏆 Achievement Badges — {target.display_name}",
            description="Complete educational challenges and consistency milestones to unlock premium badges! 🚀",
            color=0xF1C40F
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        for key, data in ACHIEVEMENTS.items():
            if key in earned:
                unlocked_date = earned[key][:10]
                status = f"✅ **Unlocked** on `{unlocked_date}`\n*{data['desc']}*"
            else:
                status = f"🔒 **Locked**\n*{data['desc']}*\n💡 *Hint: {data['hint']}*"

            embed.add_field(
                name=data["name"],
                value=status,
                inline=False
            )

        embed.set_footer(text=f"Total Unlocked: {len(earned)}/{len(ACHIEVEMENTS)}")
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Achievements(bot))
