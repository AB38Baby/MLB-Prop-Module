import pandas as pd
import requests
from datetime import datetime

# ==========================
# ACTIVE HIT STREAKS
# ==========================

def get_hit_streaks():

    try:
        tables = pd.read_html(
            "https://www.baseballmusings.com/cgi-bin/CurStreak.py"
        )

        streaks = tables[0]

        streaks.columns = [
            "Player",
            "Games",
            "AB",
            "Runs",
            "Hits",
            "HR",
            "RBI",
            "BB",
            "SO",
            "AVG",
            "OBP",
            "SLG",
            "LastGame"
        ]

        return streaks[["Player", "Games"]]

    except Exception as e:

        print("Streak load error:", e)

        return pd.DataFrame(
            columns=["Player", "Games"]
        )

# ==========================
# MLB LEADERS
# ==========================

def get_mlb_hit_leaders():

    url = (
        "https://statsapi.mlb.com/api/v1/stats"
        "?stats=season"
        "&group=hitting"
        "&sortStat=hits"
        "&playerPool=ALL"
        "&limit=200"
        "&sportIds=1"
    )

    data = requests.get(url).json()

    players = []

    try:

        splits = data["stats"][0]["splits"]

        for row in splits:

            player = row["player"]["fullName"]

            stats = row["stat"]

            avg = float(
                stats.get("avg", ".000")
            )

            slg = float(
                stats.get("slg", ".000")
            )

            hr = int(
                stats.get("homeRuns", 0)
            )

            pa = int(
                stats.get("plateAppearances", 1)
            )

            players.append([
                player,
                avg,
                slg,
                hr,
                pa
            ])

    except Exception as e:

        print("MLB API error:", e)

    return pd.DataFrame(
        players,
        columns=[
            "Player",
            "AVG",
            "SLG",
            "HR",
            "PA"
        ]
    )

# ==========================
# HIT MODEL
# ==========================

def hit_probability(avg, streak):

    score = (
        avg * 0.85
        +
        min(streak * 0.01, 0.10)
    )

    return round(
        min(score, 0.95) * 100,
        1
    )

# ==========================
# HR MODEL
# ==========================

def hr_probability(hr, pa, slg):

    if pa <= 0:
        return 0

    hr_rate = hr / pa

    score = (
        hr_rate * 6
        +
        slg * 0.30
    )

    return round(
        min(score, 0.45) * 100,
        1
    )

# ==========================
# BUILD REPORT
# ==========================

def build_report():

    print("Loading MLB stats...")

    stats = get_mlb_hit_leaders()

    print("Loading streaks...")

    streaks = get_hit_streaks()

    df = stats.merge(
        streaks,
        on="Player",
        how="left"
    )

    df["Games"] = (
        df["Games"]
        .fillna(0)
        .astype(int)
    )

    df["Hit_Prob"] = df.apply(
        lambda x: hit_probability(
            x["AVG"],
            x["Games"]
        ),
        axis=1
    )

    df["HR_Prob"] = df.apply(
        lambda x: hr_probability(
            x["HR"],
            x["PA"],
            x["SLG"]
        ),
        axis=1
    )

    df = df.sort_values(
        "Hit_Prob",
        ascending=False
    )

    return df

# ==========================
# MAIN
# ==========================

if __name__ == "__main__":

    report = build_report()

    today = datetime.today().strftime(
        "%Y-%m-%d"
    )

    filename = (
        f"MLB_PROPS_{today}.csv"
    )

    report.to_csv(
        filename,
        index=False
    )

    print("\n===== TOP 25 HIT PROPS =====\n")

    print(
        report[
            [
                "Player",
                "Games",
                "Hit_Prob",
                "HR_Prob"
            ]
        ].head(25)
    )

    print(
        f"\nSaved to {filename}"
    )
