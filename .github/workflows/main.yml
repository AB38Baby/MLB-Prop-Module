import pandas as pd
import requests
from datetime import datetime

# =====================================
# TODAY'S MLB SCHEDULE
# =====================================

def get_todays_games():
    today = datetime.today().strftime("%Y-%m-%d")

    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"

    data = requests.get(url, timeout=30).json()

    games = []

    for date in data.get("dates", []):
        for game in date.get("games", []):

            away_team = game["teams"]["away"]["team"]["name"]
            home_team = game["teams"]["home"]["team"]["name"]

            away_pitcher = (
                game["teams"]["away"]
                .get("probablePitcher", {})
                .get("fullName", "TBD")
            )

            home_pitcher = (
                game["teams"]["home"]
                .get("probablePitcher", {})
                .get("fullName", "TBD")
            )

            games.append([
                away_team,
                home_team,
                away_pitcher,
                home_pitcher
            ])

    return pd.DataFrame(
        games,
        columns=[
            "Away Team",
            "Home Team",
            "Away Pitcher",
            "Home Pitcher"
        ]
    )

# =====================================
# MLB HITTING STATS
# =====================================

def get_hitters():

    url = (
        "https://statsapi.mlb.com/api/v1/stats"
        "?stats=season"
        "&group=hitting"
        "&playerPool=ALL"
        "&limit=500"
        "&sportIds=1"
    )

    data = requests.get(url, timeout=30).json()

    players = []

    for row in data["stats"][0]["splits"]:

        try:
            player = row["player"]["fullName"]
            stat = row["stat"]

            avg = float(stat.get("avg", ".000"))
            slg = float(stat.get("slg", ".000"))
            hr = int(stat.get("homeRuns", 0))
            hits = int(stat.get("hits", 0))
            ab = int(stat.get("atBats", 0))
            pa = int(stat.get("plateAppearances", 0))

            if ab < 50:
                continue

            players.append([
                player,
                avg,
                slg,
                hr,
                hits,
                ab,
                pa
            ])

        except Exception:
            continue

    return pd.DataFrame(
        players,
        columns=[
            "Player",
            "AVG",
            "SLG",
            "HR",
            "Hits",
            "AB",
            "PA"
        ]
    )

# =====================================
# HIT PROBABILITY
# =====================================

def hit_probability(avg, expected_ab=4):
    probability = 1 - ((1 - avg) ** expected_ab)
    return round(probability * 100, 1)

# =====================================
# TWO HIT PROBABILITY
# =====================================

def two_hit_probability(avg, expected_ab=4):

    p = avg

    p0 = (1 - p) ** expected_ab

    p1 = expected_ab * p * ((1 - p) ** (expected_ab - 1))

    return round((1 - p0 - p1) * 100, 1)

# =====================================
# HR PROBABILITY
# =====================================

def hr_probability(hr, pa, slg):

    if pa == 0:
        return 0

    hr_rate = hr / pa

    score = (hr_rate * 4.5) + (slg * 0.15)

    return round(min(score, 0.40) * 100, 1)

# =====================================
# MAIN
# =====================================

if __name__ == "__main__":

    print("Loading today's schedule...")

    schedule = get_todays_games()

    print("Loading hitter stats...")

    hitters = get_hitters()

    hitters["Hit_Prob"] = hitters["AVG"].apply(hit_probability)

    hitters["TwoHit_Prob"] = hitters["AVG"].apply(two_hit_probability)

    hitters["HR_Prob"] = hitters.apply(
        lambda x: hr_probability(
            x["HR"],
            x["PA"],
            x["SLG"]
        ),
        axis=1
    )

    hitters = hitters.sort_values(
        "Hit_Prob",
        ascending=False
    )

    today = datetime.today().strftime("%Y-%m-%d")

    schedule_file = f"TODAYS_GAMES_{today}.csv"
    props_file = f"HIT_PROPS_{today}.csv"

    schedule.to_csv(schedule_file, index=False)
    hitters.to_csv(props_file, index=False)

    print("\n===== TODAY'S GAMES =====\n")
    print(schedule)

    print("\n===== TOP 25 HIT PROPS =====\n")

    print(
        hitters[
            [
                "Player",
                "AVG",
                "Hit_Prob",
                "TwoHit_Prob",
                "HR_Prob"
            ]
        ].head(25)
    )

    print(f"\nSaved: {schedule_file}")
    print(f"Saved: {props_file}")
