## NFL Survivor Pool Optimization

When my partner asked me to finally join the boys in a football pool, I knew this was my chance to shine, leveraging data analytics on my side. While he opted for a Monte Carlo simulation approach, I chose the reliable path of optimization—it has never failed me to date.

The concept here was straightforward: each week, select the best matchup that you think is most likely to win while also being forward-thinking. This means analyzing future games to ensure your odds remain strong and that you still have favorable matchups in later weeks. By pulling weekly odds, this tool allows you to reoptimize each week to ensure you’re working with the most up-to-date and relevant information.

**Spoiler**: Neither of us won the survivor pool. It turns out sports gambling is very unpredictable.

### Rules of a Survivor Pool
1. Each week, participants select one NFL team they believe will win their matchup.
2. A team can only be selected once for the entire season.
3. Once you have selected a team, you cannot pick them again for any future week.
4. If your chosen team loses, you’re eliminated.
5. The last person standing wins (or the pool ends with multiple winners if no one survives all the weeks)

### What Does This Code Do?
This Python script helps you make smarter survivor pool picks by:
1. Fetching game odds from The Odds API for each week of the NFL season.
2. Calculating probabilities for each team to win.
3. Using optimization (Mixed-Integer Linear Programming) to select the best team each week, maximizing your chances of surviving.
4. Allowing weekly reoptimization based on updated odds and previously selected teams.

### Key Features
- **Weekly Odds Fetching**: Pulls real-time game odds from The Odds API.
- **Probability Calculation**: Converts moneyline odds into probabilities.
- **Optimization**: Uses pulp to ensure you pick the best possible team for each week, considering restrictions and maximizing survival chances.
- **Reoptimization**: Adjusts selections each week based on new odds and teams already picked.

### How to Use
1. Clone the repository: git clone https://github.com/yourusername/nfl-survivor-pool-optimizer.git
2. Install the required Python packages: pip install requests pandas pulp
3. Replace your_api_key in the script with your API key from The Odds API.
4. Run the script: python nfl_survivor_pool_optimizer.py
5. Review the optimized picks printed to the console.

### Notes
- The optimization assumes that survivor pools usually don’t last all 18 weeks. However, you can adjust the duration as needed.
- Real-world gambling is highly unpredictable. This tool maximizes statistical chances but cannot guarantee success.
