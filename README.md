# chooterbot-minusone
## A simple Manifold bot

This is the original chooterbot, circa November 2023. chooterbot 2.0, not included here, is much cooler, runs much quicker, and does far more smarter things, like concurrency the smart way.

chooterbot 1.0 arbitrages between selected markets if the (manually adjustable) spread is too big. It even arbitrages markets that sum to more than a specified amount (independent multichoice, not sumToOne), for example 1000% for a top 10 list market. 

However, due to newly added market taker fees (between 7% and 0%, using the formula 0.07 * prob * (1 - prob) * shares) pure arbitrage is unprofitable in nearly all cases. Except when the markets are low liquidity and highly volatile, such as sports betting or whatever Sam Altman is up to these days. However, Manifold's API caches too much to make this worthwhile.
For a quick example of why arbitrage is no longer profitable, see [N.C.Y.Bot's recent profit](https://manifold.markets/NcyBot)

This runs on a custom manifoldpy API version. Installation is self-explanatory if you've ever used python. If you're stuck check out [Official API](https://docs.manifold.markets/api) and [Manifoldpy](https://manifold-markets-python.readthedocs.io/en/latest/)
