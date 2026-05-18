# ══════════════════════════════════════════════════════
#  utils/helpers.py  —  Shared helper utilities
# ══════════════════════════════════════════════════════

import random
import discord
from config import TIER_ROLES

# ── Tier emoji & color map ─────────────────────────────

TIER_EMOJI: dict[str, str] = {
    "Beginner":   "🔘",
    "Consistent": "🟢",
    "Dedicated":  "🔵",
    "Grinder":    "🟣",
    "Elite":      "🟠",
    "Legend":     "🌟",
}

# ── Congratulations pool (CP-themed) ──────────────────

_CONGRATS: list[str] = [
    "✅ **AC** — Day {day} accepted! {mention} keeps the streak alive! 🚀",
    "✅ **Accepted!** {mention} submitted Day {day} — clean solution, no penalties! 💪",
    "🟢 **AC on Day {day}!** {mention} just pushed to their consistency streak! 🔥",
    "⚡ **Correct!** {mention} — Day {day} verdict: **ACCEPTED**. Runtime: legendary! 🏆",
    "💥 {mention} solved Day {day}! No WA, no TLE — straight **AC**! 🎯",
    "🦾 Day {day} submitted and accepted! {mention} is running on all cylinders! 💡",
    "🏅 **Problem {day} — AC!** {mention} is absolutely unstoppable! 🙌",
    "🚀 **AC!** {mention} cleared Day {day}. Penalty: zero. Efficiency: max! ☄️",
    "💎 {mention} — Day {day} verdict: **ACCEPTED** with flying colors! ✨",
    "🎯 **Day {day} → AC!** {mention} is building something legendary! 🔐",
]


def congrats_message(mention: str, day: int) -> str:
    """Return a random CP-themed congratulations message."""
    return random.choice(_CONGRATS).format(mention=mention, day=day)


# ── Level-up pool (CP-themed) ─────────────────────────

_LEVELUP: list[str] = [
    "🎉 {mention} just ranked up to **{tier}** after {day} days — keep grinding! 🔥",
    "⬆️ **Rank Up!** {mention} has been promoted to **{tier}** on Day {day}! 🚀",
    "🏆 **{tier}** unlocked! {mention} — {day} days of pure dedication! 💪",
    "✨ New rank! {mention} is now **{tier}** — Day {day} strong! 👏",
    "🌟 {mention} leveled up to **{tier}** at Day {day}. The grind never stops! ⚡",
    "💥 **Rank cleared!** {mention} achieved **{tier}** status — Day {day}! 🎯",
    "🦾 {mention} earned the **{tier}** badge after {day} days. Nothing stops them! 🏅",
    "🔐 **New perks unlocked!** {mention} is officially **{tier}** — Day {day}! 💡",
]


def levelup_message(mention: str, tier: str, day: int) -> str:
    """Return a random CP-themed level-up message."""
    return random.choice(_LEVELUP).format(mention=mention, tier=tier, day=day)


# ── Progress bar ──────────────────────────────────────

def progress_bar(current: int, total: int, length: int = 10) -> str:
    """Return a visual bar like [████░░░░░░] 4/10."""
    if total <= 0:
        return f"[{'█' * length}] MAX"
    filled = min(round((current / total) * length), length)
    return f"[{'█' * filled}{'░' * (length - filled)}] {current}/{total}"


# ── Tier progress info ────────────────────────────────

def get_tier_progress(day: int) -> dict | None:
    """
    Return a dict describing the user's position within their current tier:
      current_tier, next_tier, days_into_tier, tier_len, days_to_next, bar
    Returns None if day is out of range.
    """
    for i, tier in enumerate(TIER_ROLES):
        if tier["min_day"] <= day <= tier["max_day"]:
            tier_len       = tier["max_day"] - tier["min_day"] + 1
            days_into_tier = day - tier["min_day"] + 1
            next_tier      = TIER_ROLES[i + 1] if i + 1 < len(TIER_ROLES) else None
            days_to_next   = (next_tier["min_day"] - day) if next_tier else 0
            bar = (
                progress_bar(days_into_tier, tier_len)
                if next_tier else
                f"[{'█' * 10}] MAX RANK"
            )
            return {
                "current_tier":  tier,
                "next_tier":     next_tier,
                "days_into_tier": days_into_tier,
                "tier_len":      tier_len,
                "days_to_next":  days_to_next,
                "bar":           bar,
            }
    return None


# ── Motivational messages per tier ────────────────────

_MOTIVATION: dict[str, str] = {
    "Beginner":   "Just getting started. **{days}** more days to **Consistent**! 🚀",
    "Consistent": "Showing up every day! **{days}** more days to **Dedicated**! 💪",
    "Dedicated":  "The grind is paying off. **{days}** more days to **Grinder**! 🔥",
    "Grinder":    "Pure dedication. **{days}** more days to **Elite**! ⚡",
    "Elite":      "Almost legendary. **{days}** more days to **Legend**! 👑",
    "Legend":     "**MAX RANK.** You've reached the pinnacle. You are a Legend! 🏆",
}


def motivation(tier_name: str, days_to_next: int) -> str:
    """Return a motivational string for the given tier."""
    return _MOTIVATION.get(tier_name, "Keep going!").format(days=days_to_next)


# ── Phase role boundary check ─────────────────────────

def get_phase_role_for_day(day: int, phase_roles: dict[int, str]) -> str | None:
    return phase_roles.get(day)


# ── Codeforces announcement embed ────────────────────

def cf_submission_embed(
    mention: str,
    cf_handle: str,
    problem_name: str,
    problem_url: str,
    contest_id: str | int,
    rating: int | None,
) -> discord.Embed:
    rating_str = f"⭐ {rating}" if rating else "Unrated"
    embed = discord.Embed(
        title="✅ New Accepted Submission!",
        description=(
            f"{mention} just solved **[{problem_name}]({problem_url})**! 🎯\n\n"
            f"> 📚 **Problem:** [{problem_name}]({problem_url})\n"
            f"> 🏟️ **Contest ID:** `{contest_id}`\n"
            f"> 📊 **Difficulty:** {rating_str}"
        ),
        color=discord.Color.from_rgb(67, 181, 129),
    )
    embed.set_footer(
        text=f"Codeforces • {cf_handle}",
        icon_url="https://codeforces.com/favicon.ico",
    )
    return embed
