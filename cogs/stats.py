# ══════════════════════════════════════════════════════
#  cogs/stats.py  —  Codeforces Statistics and Comparisons
# ══════════════════════════════════════════════════════

import aiohttp
import discord
from discord.ext import commands

import database as db


class Stats(commands.Cog):
    """Cog for viewing Codeforces stats and comparing participants."""

    CF_BASE = "https://codeforces.com/api"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._session: aiohttp.ClientSession | None = None

    async def cog_load(self) -> None:
        self._session = aiohttp.ClientSession()

    async def cog_unload(self) -> None:
        if self._session:
            await self._session.close()

    # ── CF API Helpers ──────────────────────────────────

    async def _fetch_json(self, url: str) -> dict | None:
        try:
            async with self._session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            print(f"[Stats API] Error fetching {url}: {e}")
        return None

    def _get_rating_color(self, rating: int) -> int:
        """Get tier color based on Codeforces rating."""
        if rating < 1200:
            return 0x95A5A6  # Gray (Newbie)
        elif rating < 1400:
            return 0x2ECC71  # Green (Pupil)
        elif rating < 1600:
            return 0x3498DB  # Blue (Specialist)
        elif rating < 1900:
            return 0x9B59B6  # Purple (Expert)
        elif rating < 2300:
            return 0xE67E22  # Orange (Candidate Master / Master)
        else:
            return 0xE74C3C  # Red (Grandmaster / Legendary Grandmaster)

    # ── Commands ───────────────────────────────────────

    @commands.command(name="cfstats", aliases=["cfprofile"])
    async def cf_stats(self, ctx: commands.Context, handle: str = None) -> None:
        """Show rich Codeforces statistics for a user."""
        if handle is None:
            row = db.get_cf_user(ctx.author.id)
            if row is None:
                await ctx.reply("❌ No handle linked. Use `!setcf <handle>` first.")
                return
            handle = row["cf_handle"]

        async with ctx.typing():
            # Fetch user info
            info_data = await self._fetch_json(f"{self.CF_BASE}/user.info?handles={handle}")
            if info_data is None or info_data.get("status") != "OK":
                await ctx.reply(f"❌ Could not fetch info for **{handle}**.")
                return

            info = info_data["result"][0]
            rating = info.get("rating", 0)
            max_rating = info.get("maxRating", 0)
            rank = info.get("rank", "unranked").title()
            avatar = info.get("titlePhoto", "")
            color_hex = self._get_rating_color(rating)

            # Fetch user status
            status_data = await self._fetch_json(f"{self.CF_BASE}/user.status?handle={handle}")
            solved_count = 0
            last_solved = []

            if status_data and status_data.get("status") == "OK":
                seen_problems = set()
                for sub in status_data["result"]:
                    if sub.get("verdict") == "OK":
                        prob = sub.get("problem", {})
                        c_id = prob.get("contestId")
                        idx = prob.get("index")
                        p_name = prob.get("name", "Unknown")
                        if c_id and idx:
                            key = f"{c_id}{idx}"
                            if key not in seen_problems:
                                seen_problems.add(key)
                                solved_count += 1
                                if len(last_solved) < 5:
                                    url = f"https://codeforces.com/contest/{c_id}/problem/{idx}"
                                    last_solved.append(f"• [{p_name}]({url})")

            last_solved_str = "\n".join(last_solved) if last_solved else "No solved problems found."

            embed = discord.Embed(
                title=f"📊 {handle} — Codeforces Stats",
                url=f"https://codeforces.com/profile/{handle}",
                color=color_hex
            )
            embed.add_field(name="Rating", value=f"`{rating}`", inline=True)
            embed.add_field(name="Max Rating", value=f"`{max_rating}`", inline=True)
            embed.add_field(name="Rank", value=f"`{rank}`", inline=True)
            embed.add_field(name="Problems Solved", value=f"`{solved_count}`", inline=True)
            embed.add_field(name="🛡️ Last 5 Solved Problems", value=last_solved_str, inline=False)

            if avatar:
                embed.set_thumbnail(url=f"https:{avatar}" if avatar.startswith("//") else avatar)

            embed.set_footer(text="AGNoobies CP Tracker")
            await ctx.reply(embed=embed)

    @commands.command(name="compare")
    async def compare_users(self, ctx: commands.Context, u1: discord.Member = None, u2: discord.Member = None) -> None:
        """Compare Codeforces statistics of two users side by side."""
        if u1 is None or u2 is None:
            await ctx.reply("❌ Usage: `!compare @user1 @user2`")
            return

        u1_cf = db.get_cf_user(u1.id)
        u2_cf = db.get_cf_user(u2.id)

        if not u1_cf:
            await ctx.reply(f"❌ {u1.display_name} has not linked their Codeforces handle yet!")
            return
        if not u2_cf:
            await ctx.reply(f"❌ {u2.display_name} has not linked their Codeforces handle yet!")
            return

        async with ctx.typing():
            h1 = u1_cf["cf_handle"]
            h2 = u2_cf["cf_handle"]

            info_h1 = await self._fetch_json(f"{self.CF_BASE}/user.info?handles={h1}")
            info_h2 = await self._fetch_json(f"{self.CF_BASE}/user.info?handles={h2}")

            if not info_h1 or info_h1.get("status") != "OK" or not info_h2 or info_h2.get("status") != "OK":
                await ctx.reply("❌ Failed to fetch user info from Codeforces API.")
                return

            i1 = info_h1["result"][0]
            i2 = info_h2["result"][0]

            r1, r2 = i1.get("rating", 0), i2.get("rating", 0)
            mr1, mr2 = i1.get("maxRating", 0), i2.get("maxRating", 0)

            # Get solves
            status_h1 = await self._fetch_json(f"{self.CF_BASE}/user.status?handle={h1}")
            status_h2 = await self._fetch_json(f"{self.CF_BASE}/user.status?handle={h2}")

            def get_stat_counts(status_data):
                solves = set()
                contests = set()
                best_rank = 999999
                if status_data and status_data.get("status") == "OK":
                    for sub in status_data["result"]:
                        prob = sub.get("problem", {})
                        c_id = prob.get("contestId")
                        idx = prob.get("index")
                        if c_id and idx:
                            contests.add(c_id)
                            if sub.get("verdict") == "OK":
                                solves.add(f"{c_id}{idx}")
                                # Approximate contest rank if available
                                rank = sub.get("author", {}).get("rank")
                                if rank and rank < best_rank:
                                    best_rank = rank
                return len(solves), len(contests), (best_rank if best_rank != 999999 else "N/A")

            s1, c1, b1 = get_stat_counts(status_h1)
            s2, c2, b2 = get_stat_counts(status_h2)

            # Scoring
            score1 = 0
            score2 = 0

            # Helper to apply crown
            def compare_vals(v1, v2, desc=False):
                nonlocal score1, score2
                if v1 == "N/A" and v2 == "N/A":
                    return f"`{v1}`", f"`{v2}`"
                if v1 == "N/A":
                    score2 += 1
                    return f"`{v1}`", f"`{v2}` 👑"
                if v2 == "N/A":
                    score1 += 1
                    return f"`{v1}` 👑", f"`{v2}`"

                if desc: # Lower is better (best rank)
                    if v1 < v2:
                        score1 += 1
                        return f"`{v1}` 👑", f"`{v2}`"
                    elif v2 < v1:
                        score2 += 1
                        return f"`{v1}`", f"`{v2}` 👑"
                else:
                    if v1 > v2:
                        score1 += 1
                        return f"`{v1}` 👑", f"`{v2}`"
                    elif v2 > v1:
                        score2 += 1
                        return f"`{v1}`", f"`{v2}` 👑"
                return f"`{v1}`", f"`{v2}`"

            disp_r1, disp_r2 = compare_vals(r1, r2)
            disp_mr1, disp_mr2 = compare_vals(mr1, mr2)
            disp_s1, disp_s2 = compare_vals(s1, s2)
            disp_c1, disp_c2 = compare_vals(c1, c2)
            disp_b1, disp_b2 = compare_vals(b1, b2, desc=True)

            overall_winner = ""
            if score1 > score2:
                overall_winner = f"🏆 **Winner:** {u1.mention} ({h1}) with `{score1}-{score2}`"
            elif score2 > score1:
                overall_winner = f"🏆 **Winner:** {u2.mention} ({h2}) with `{score2}-{score1}`"
            else:
                overall_winner = f"🤝 **Verdict:** It's a Tie! `{score1}-{score2}`"

            embed = discord.Embed(
                title="⚔️ Head-to-Head Comparison",
                description=f"**{u1.display_name}** vs **{u2.display_name}**",
                color=0x2C2F33
            )
            embed.add_field(name="👤 Participant 1", value=f"{u1.mention}\nHandle: **{h1}**", inline=True)
            embed.add_field(name="👤 Participant 2", value=f"{u2.mention}\nHandle: **{h2}**", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)

            embed.add_field(name="Rating", value=f"{disp_r1} vs {disp_r2}", inline=False)
            embed.add_field(name="Max Rating", value=f"{disp_mr1} vs {disp_mr2}", inline=False)
            embed.add_field(name="Problems Solved", value=f"{disp_s1} vs {disp_s2}", inline=False)
            embed.add_field(name="Contests Practiced", value=f"{disp_c1} vs {disp_c2}", inline=False)
            embed.add_field(name="Best Rank", value=f"{disp_b1} vs {disp_b2}", inline=False)

            embed.add_field(name="🏁 FINAL VERDICT", value=overall_winner, inline=False)
            embed.set_footer(text="AGNoobies Head-to-Head Arena")

            await ctx.reply(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Stats(bot))
