from manifoldpy import api
import time

key = open("apikey.txt").read().strip()

wrapper = api.APIWrapper(key)

def get_answerID(market: api.Market, answerText: str):
    if market.outcomeType == "MULTIPLE_CHOICE":
        for answer in market.answers:
            if answer.get('text') == answerText:
                return answer.get('id')
def get_multi_prob(market: api.Market, answerText: str):
    if market.outcomeType == "MULTIPLE_CHOICE":
        for answer in market.answers:
            if answer.get('text') == answerText:
                return answer.get('probability')
def avg_prob(markets) -> float:
    total = 0.0
    for marketTuple in markets:
        marketFromSlug = api.get_slug(marketTuple[0])
        market = api.get_full_market(marketFromSlug.id)
        if market.closeTime < time.time_ns() // 1000000:
            continue
        if market.outcomeType == "MULTIPLE_CHOICE":
            prob = get_multi_prob(market, marketTuple[2])
        elif market.outcomeType == "FREE_RESPONSE":
            print(marketTuple[0])
            raise Exception
        else:
            prob = market.final_probability()
        if not marketTuple[1]:
            prob = 1.0 - prob
        if not prob:
            print(marketTuple[2])
        total += prob
    return total / len(markets)


def bet(market: api.Market, outcome: str, limitProb: float, amount: int, answerId=None):

    unixTime = time.time_ns() // 1000000
    seconds = 0
    offset = 60000
    endTime = unixTime + seconds * 1000 + offset
    print(endTime)
    betResult = wrapper.make_bet(amount=amount, contractId=market.id, outcome=outcome, limitProb=limitProb,
                                 expiresAt=endTime, answerId=answerId)

    print(betResult.text)
    print(int(time.time_ns() // 1000000))

# TODO calculate spent + payout

def arb(markets, realprob, bet_amount, trade=False, spread=0.02):
    for marketTuple in markets:
        marketFromSlug = api.get_slug(marketTuple[0])
        market = api.get_full_market(marketFromSlug.id)
        if market.closeTime < (time.time_ns() // 1000000):
            print("Nonoon")
            return

        if market.outcomeType == "MULTIPLE_CHOICE":
            prob = get_multi_prob(market, marketTuple[2])
        else:
            prob = market.final_probability()

        if not marketTuple[1]:
            prob = 1.0 - prob
        # print(prob)
        if prob - spread > realprob:
            realprob = round(realprob, 2)
            if not marketTuple[1]:
                prob = 1.0 - prob
            if marketTuple[1]:
                amt = int(bet_amount * (1.0 - realprob))
                print(f'{market.question} has prob {prob}, real prob is {realprob} bet {amt} NO')
                if trade:
                    if market.outcomeType == "MULTIPLE_CHOICE":
                        bet(market, "NO", realprob, amt, get_answerID(market, marketTuple[2]))
                    else:
                        bet(market, "NO", realprob, amt)
            else:
                amt = int(bet_amount * (1.0 - realprob))
                print(f'{market.question} has prob {prob}, real prob is {1.0 - realprob} bet {amt} YES')
                if trade:
                    if market.outcomeType == "MULTIPLE_CHOICE":
                        bet(market, "YES", 1.0 - realprob, amt, get_answerID(market, marketTuple[2]))
                    else:
                        bet(market, "YES", 1.0 - realprob, amt)

        elif prob + spread < realprob:
            realprob = round(realprob, 2)
            if not marketTuple[1]:
                prob = 1.0 - prob
            if marketTuple[1]:
                amt = int(bet_amount * realprob)
                print(f'{market.question} has prob {prob}, real prob is {realprob} bet {amt} YES')
                if trade:
                    if market.outcomeType == "MULTIPLE_CHOICE":
                        bet(market, "YES", realprob, amt, get_answerID(market, marketTuple[2]))
                    else:
                        bet(market, "YES", realprob, amt)
            else:
                amt = int(bet_amount * realprob)
                print(f'{market.question} has prob {prob}, real prob is {1.0 - realprob} bet {amt} NO')
                if trade:
                    if market.outcomeType == "MULTIPLE_CHOICE":
                        bet(market, "NO", 1.0 - realprob, amt, get_answerID(market, marketTuple[2]))
                    else:
                        bet(market, "NO", 1.0 - realprob, amt)

        #marketFromSlug = api.get_slug(marketTuple[0])
        #market = api.get_full_market(marketFromSlug.id)
        #prob = market.final_probability()
        #print(prob)

def autoArb(marketSlug, correctProbSum, bet_size, shouldBet=False):
    marketFromSlug = api.get_slug(marketSlug)
    market = api.get_full_market(marketFromSlug.id)
    sum_prob = 0.0
    for answer in market.answers:
        sum_prob += answer.get("probability")
    if 100 * (sum_prob - correctProbSum) > len(market.answers):
        print(int((100 * (sum_prob - correctProbSum)) / len(market.answers)))
        if int((100 * (sum_prob - correctProbSum)) / len(market.answers)) - 1 >= 1:
            percent_to_bet = int((100 * (sum_prob - correctProbSum)) / len(market.answers)) - 1
            print(f'Bet! {percent_to_bet} down!')
            for answer in market.answers:
                amt = (int(1 / answer.get("probability")) * bet_size) + 5
                real_prob = max(0.01, round(answer.get("probability") - (percent_to_bet)/100.0, 2))
                print(f'{market.question} has prob {answer.get("probability")}, real prob is {real_prob} bet {amt} NO')
                if shouldBet:
                    bet(market, "NO", real_prob, amt, answer.get("id"))


arbMarket = "which-video-games-confirmed-for-rel"
autoArb(arbMarket, 1.0, 2, True)

arbmarket2 = "lesswrong-2022-review-top-5-posts"
autoArb(arbMarket, 5.0, 1)

relegMarket = "which-teams-will-be-relegated-in-20"
autoArb(relegMarket, 4.0, 5, True)

botMarket = "battle-of-the-bots-who-will-finish-a45a4bdc1dd2"
autoArb(botMarket, 5.0, 5, True)

botMarket = "which-three-countries-will-win-the"
autoArb(botMarket, 3.0, 20)

#bottom10market = "what-logos-will-be-on-the-agencys-f"
#autoArb(bottom10market, 13.0, 5, True)


oldBronze = 0.0
oldYes = 0.0
old50 = 0.0

while True:
    try:
        imoBronzeMarkets = [("will-ai-get-at-least-bronze-on-the", True),
                           ("will-an-ai-get-bronze-or-silver-on", True)]
        imoBronzeProb = avg_prob(imoBronzeMarkets)
        arb(imoBronzeMarkets, imoBronzeProb, 100)
        print(f"avg prob bronze \t{imoBronzeProb}")

        threadsMarkets = [("will-threads-overtake-x-in-daily-ac", True),
                          ("will-threads-have-more-daily-active", True)]
        threadProb = avg_prob(threadsMarkets)
        arb(threadsMarkets, threadProb, 100)
        print(f"avg prob thread \t{threadsMarkets}")

        eliezer = [("will-eliezer-yudkowsky-tweet-the-wo", True),
                   ("will-eliezer-yudkowsky-write-a-twee", True)]
        elizerprob = avg_prob(eliezer)
        arb(eliezer, elizerprob, 50, True, spread=0.01)
        print(f"avg prob eliezer \t{elizerprob}")

    except Exception as e:
        pass
