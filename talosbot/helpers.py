import discord
import logging

logger = logging.getLogger(__name__)

EMOJIS = {
    "description": ":question:",
    "reward": ":point_right:",
    "deadline": ":calendar:",
    "worried": ":worried:",
    "tada": ":tada:",
    "name": ":information_source:",
    "members": ":man_mage:",
}


def chunkify(text, limit):
    chunks = []
    while len(text) > limit:
        idx = text.index("\n", limit)
        chunks.append(text[:idx])
        text = text[idx:]
    chunks.append(text)
    return chunks


def get_competition_embed(comp, emp_desc_fields, title_field="ref"):

    if isinstance(comp, dict):
        title = comp.get(title_field)
        url = comp.get("url")
    else:
        title = getattr(comp, title_field)
        url = getattr(comp, "url")
    description = ""
    for field in emp_desc_fields:
        key = field
        if isinstance(comp, dict):
            value = comp.get(field)
        else:
            value = getattr(comp, field)
            if len(field.split("_")) > 1:
                field_strs = field.split("_")
                key = field_strs[1]
                field = " ".join(field_strs)
        description += f"{EMOJIS[key]}{field.title()}: {value}\n"
    emb = discord.Embed(title=" ".join(title.split("-")).title(), description=description, url=url, colour=4387968)
    return emb


def get_team_entry_from_leaderboard(leaderboard, team_name):
    team_record = None
    for team in leaderboard:
        name = getattr(team, "teamName")
        if team_name == name:
            team_record = team
            break
    return team_record
