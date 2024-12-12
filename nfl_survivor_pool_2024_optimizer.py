# NFL Survivor Pool Optimization

import requests
import datetime
import pandas as pd
import pulp

# Constants
API_KEY = 'your_api_key'  # Replace with your API key
BASE_URL = 'https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds'

# Function to get odds for a specific week


def get_weekly_odds(api_key, week_number):
    """
    Fetch odds for a specific NFL week.

    Args:
        api_key (str): API key for The Odds API.
        week_number (int): Week number to fetch odds for.

    Returns:
        list: JSON data containing odds for the week, or None if the request fails.
    """
    start_date = datetime.datetime(
        2024, 9, 5) + datetime.timedelta(weeks=week_number - 1)
    end_date = start_date + datetime.timedelta(days=7)

    params = {
        'apiKey': api_key,
        'regions': 'us',
        'markets': 'h2h,spreads,totals',
        'oddsFormat': 'decimal',
        'bookmakers': 'draftkings',
        'commenceTimeFrom': start_date.isoformat() + 'Z',
        'commenceTimeTo': end_date.isoformat() + 'Z'
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get data: {response.status_code}, {response.text}")
        return None

# Function to gather odds for all weeks


def get_all_weeks_odds_df(api_key):
    """
    Gather odds for all weeks of the NFL season.

    Args:
        api_key (str): API key for The Odds API.

    Returns:
        pd.DataFrame: DataFrame containing odds and probabilities for each game.
    """
    all_odds = []
    for week in range(1, 19):
        weekly_odds = get_weekly_odds(api_key, week)
        if weekly_odds:
            for game in weekly_odds:
                game_data = {
                    'Week': week,
                    'Home Team': game['home_team'],
                    'Away Team': game['away_team'],
                    'Commence Time': game['commence_time'],
                    'Home Team Moneyline': None,
                    'Away Team Moneyline': None
                }
                for bookmaker in game.get('bookmakers', []):
                    if bookmaker['key'] == 'draftkings':
                        for market in bookmaker.get('markets', []):
                            if market['key'] == 'h2h':
                                for outcome in market.get('outcomes', []):
                                    if outcome['name'] == game['home_team']:
                                        game_data['Home Team Moneyline'] = outcome['price']
                                    elif outcome['name'] == game['away_team']:
                                        game_data['Away Team Moneyline'] = outcome['price']
                all_odds.append(game_data)

    nfl_odds_df = pd.DataFrame(all_odds)
    nfl_odds_df['Home Probability'] = 1 / nfl_odds_df['Home Team Moneyline']
    nfl_odds_df['Away Probability'] = 1 / nfl_odds_df['Away Team Moneyline']
    return nfl_odds_df[['Week', 'Home Team', 'Home Probability', 'Away Team', 'Away Probability']]

# Optimization for survivor pool over multiple weeks


def optimize_survivor_pool(nfl_odds_df, current_week, selected_teams, optimization_duration):
    """
    Optimize survivor pool team selection over multiple weeks.

    Args:
        nfl_odds_df (pd.DataFrame): DataFrame with game odds and probabilities.
        current_week (int): Current week in the season.
        selected_teams (list): List of teams already selected.
        optimization_duration (int): Number of weeks to optimize for.

    Returns:
        pd.DataFrame: DataFrame with the optimized team selections.
    """
    weeks = nfl_odds_df['Week'].unique().tolist()
    end_week = min(current_week + optimization_duration - 1, max(weeks))
    remaining_weeks = [w for w in weeks if current_week <= w <= end_week]
    teams = list(
        set(nfl_odds_df['Home Team'].tolist() + nfl_odds_df['Away Team'].tolist()))
    available_teams = [t for t in teams if t not in selected_teams]

    prob = pulp.LpProblem("SurvivorPoolOptimization", pulp.LpMaximize)
    x = pulp.LpVariable.dicts(
        "x", [(w, t) for w in remaining_weeks for t in available_teams], cat="Binary")

    prob += pulp.lpSum([
        row['Home Probability'] * x[(row['Week'], row['Home Team'])] +
        row['Away Probability'] * x[(row['Week'], row['Away Team'])]
        for _, row in nfl_odds_df.iterrows()
        if row['Week'] in remaining_weeks and
        (row['Home Team'] in available_teams and (row['Week'], row['Home Team']) in x) and
        (row['Away Team'] in available_teams and (
            row['Week'], row['Away Team']) in x)
    ])

    for t in available_teams:
        prob += pulp.lpSum([x[(w, t)]
                           for w in remaining_weeks if (w, t) in x]) <= 1

    for w in remaining_weeks:
        prob += pulp.lpSum([x[(w, t)]
                           for t in available_teams if (w, t) in x]) == 1

    prob_status = prob.solve()

    if prob_status != pulp.LpStatusOptimal:
        print(
            f"Optimization problem did not solve to optimality. Status: {pulp.LpStatus[prob_status]}")

    metrics = []
    for w in remaining_weeks:
        for t in available_teams:
            if pulp.value(x[(w, t)]) == 1:
                selected_game = nfl_odds_df[
                    ((nfl_odds_df['Week'] == w) & (nfl_odds_df['Home Team'] == t)) |
                    ((nfl_odds_df['Week'] == w) &
                     (nfl_odds_df['Away Team'] == t))
                ].iloc[0]

                home_team = selected_game['Home Team']
                away_team = selected_game['Away Team']
                selected_team_probability = selected_game[
                    'Home Probability'] if t == home_team else selected_game['Away Probability']
                opponent_team_probability = selected_game[
                    'Away Probability'] if t == home_team else selected_game['Home Probability']

                metrics.append({
                    'Week': w,
                    'Selected Team': t,
                    'Opponent Team': away_team if t == home_team else home_team,
                    'Selected Team Probability': selected_team_probability,
                    'Opponent Team Probability': opponent_team_probability,
                    'Expected Value': selected_team_probability,
                    'Reason': f'Selected {t} due to higher probability of {selected_team_probability:.4f} compared to opponent\'s probability of {opponent_team_probability:.4f}'
                })

    return pd.DataFrame(metrics)


if __name__ == "__main__":
    # Example usage
    current_week = 1
    selected_teams = []  # Teams already selected
    optimization_duration = 14

    print("Fetching NFL odds...")
    nfl_odds_df = get_all_weeks_odds_df(API_KEY)

    print("Running optimization...")
    metrics_df = optimize_survivor_pool(
        nfl_odds_df, current_week, selected_teams, optimization_duration)

    print("Optimization Results:")
    print(metrics_df)
