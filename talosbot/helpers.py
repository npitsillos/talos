def get_team_entry_from_leaderboard(leaderboard, team_name):
    team_record = None
    for team in leaderboard:
        name = getattr(team, "teamName")
        if team_name == name:
            team_record = team
            break
    return team_record


def slugify(name):
    name_items = name.split()
    words_in_name = filter(lambda x: len(x) > 1, name_items)
    return "-".join(words_in_name)
