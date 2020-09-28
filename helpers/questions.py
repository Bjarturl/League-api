from main.models import *
from django.db.models import Avg, Count, Max, Q
import datetime
from collections import Counter
import random
# python manage.py shell < helpers/questions.py 

print()
def getRandomTeam():
    return Team.objects.order_by('?').first()

def getRandomPlayer():
    return Player.objects.order_by('?').first()


def getAverageTime(durations):
    total = 0
    for d in durations:
        split = str(d).split(":")
        total += (int(split[1]) * 60) + (int(split[2]))
    total /= len(durations)
    return str(int(total / 60)) + ":" + str(int(total % 60))

def getRandomDuration(dur):
    minutes, seconds = dur.split(":")
    if len(seconds) == 1:
        seconds = "0" + seconds
    ops = ["+", "-"]
    times = []
    newTime = minutes + ":" + seconds
    while newTime not in times and len(times) != 4:
        times.append(newTime)
        newTime = str(eval(minutes + random.choice(ops) + str(random.randint(-8, 8)))) + ":" + seconds
    return times

# Hvað eru leikir hjá [team] langir að meðaltali?
def getAverageGameLengthQuestion():
    team = getRandomTeam()
    gameStats = list(GameStats.objects.filter(team=team).values_list("pk", flat=True))
    durations = list(Game.objects.filter(Q(blue_team_stats_id__in=gameStats) | Q(red_team_stats_id__in=gameStats)).values_list("duration", flat=True))
    answers = getRandomDuration(getAverageTime(durations))
    random.shuffle(answers)
    return ("Hvað eru leikir hjá " + team.name + " langir að meðaltali?", answers[0], answers)


# Hver er mest bannaði champinn í deildinni?
def getMostBannedChampQuestion():
    bans = list(GameStats.objects.all().values_list("bans", flat=True))
    most_common = Counter(bans).most_common()
    possibilities = []
    curr = ""
    curr_count = 0
    for c in most_common:
        if len(possibilities) == 5:
            break
        champ = Champion.objects.get(id=c[0]).name
        if c[1] != curr_count:
            possibilities.append((curr, str(int(curr_count / Game.objects.all().count() * 100)) + "% leikja"))
            curr = ""
        if curr != "":
            curr += ", "
        curr += champ
        curr_count = c[1]
    most = possibilities[1][0].split(", ")
    other = [most[0]]
    while len(other) != 4: 
        champ = Champion.objects.exclude(name__in=most).order_by('?').first()
        if champ.name not in other:
            other.append(champ.name)
    random.shuffle(other)
    return ("Hver af þessum champs er oftast bannaður í deildinni?", most[0] + ", " + possibilities[1][1], other)


# Hvað heitir [player_ign] í raun og veru?
def getRandomPlayerNameQuestion():
    players = []
    while len(players) != 4:
        player = getRandomPlayer()
        if (player.ign and player.name) and (player.ign, player.name) not in players:
            players.append((player.ign, player.name))
    poss = [p[1] for p in players]
    random.shuffle(poss)
    return ("Hvað heitir " + players[0][0] + " í raun og veru?", players[0][1], poss)


# Hvað hafa margir champions verið picked so far í deildinni?
def getNumChampionsQuestion():
    ans = Champion.objects.all().count() - 1
    possibilities = [ans]
    while len(possibilities) != 4:
        op =  random.choice(["+", "-"]) 
        num = eval(str(ans) + op + str(random.randint(-50, 30)))
        if num not in possibilities:
            possibilities.append(num)
    random.shuffle(possibilities)
    return ("Hvað hafa margir champions verið picked/banned samtals hingað til í deildinni?", ans, possibilities)


# Hvað er algengasta bannið á móti [team]?
def getMostCommonBanVsTeamQuestion():
    team = getRandomTeam()
    games = list(Game.objects.filter(red_team_stats__team=team).values_list("blue_team_stats", flat=True)) + \
            list(Game.objects.filter(blue_team_stats__team=team).values_list("red_team_stats", flat=True))
    bans = list(GameStats.objects.filter(pk__in=games).values_list("bans", flat=True))
    most_common = Counter(bans).most_common()
    possibilities = []
    curr = ""
    curr_count = 0
    for c in most_common:
        if len(possibilities) == 5:
            break
        champ = Champion.objects.get(id=c[0]).name
        if c[1] != curr_count:
            possibilities.append((curr, str(int(curr_count / len(games) * 100)) + "% leikja"))
            curr = ""
        if curr != "":
            curr += ", "
        curr += champ
        curr_count = c[1]
    if curr != "" and len(possibilities) != 5:
        possibilities.append((curr, str(int(curr_count / len(games) * 100)) + "% leikja"))
    most = possibilities[1][0].split(", ")
    other = [most[0]]
    while len(other) != 4: 
        champ = Champion.objects.exclude(name__in=most).order_by('?').first()
        if champ.name not in other:
            other.append(champ.name)
    random.shuffle(other)
    return ("Hver af þessum champs er algengasta bannið á móti " + team.name + "?", most[0] + ", " + possibilities[1][1], other)


# Hver er með mesta [kill, deaths, assists] að meðaltali í deildinni?
def getMostKDAInLeagueQuestion():
    kda = ["kills", "deaths", "assists"]
    field = random.choice(kda)
    op = random.choice(["-", ""])
    stats = list(PlayerStats.objects.values("player__ign").annotate(avg_score=Avg(field)).order_by(op+'avg_score')[0:5])
    question = "Hvaða spilari er með "
    if op == "-":
        question += "flestu "
    else:
        question += "fæstu "
    question += field + " að meðaltali í deildinni?"
    poss = [stats[0]["player__ign"]]
    equals = [s['player__ign'] for s in list(filter(lambda s: s['avg_score'] == stats[0]["avg_score"], stats))]
    for p in Player.objects.all().order_by('?'):
        if p.ign not in poss and len(poss) != 4 and p.ign not in equals:
            poss.append(p.ign)
    random.shuffle(poss)
    return (question, str(stats[0]["player__ign"]) + ", með " + str(stats[0]["avg_score"]) + " " + field, poss)


# Hver er með mesta [kill, deaths, assists] að meðaltali í [team]?
def getMostKDAInTeamQuestion():
    kda = ["kills", "deaths", "assists", "cs"]
    field = random.choice(kda)
    op = random.choice(["-", ""])
    team = getRandomTeam()
    stats = list(PlayerStats.objects.filter(game_stats__team=team).values("player__ign").annotate(avg_score=Avg(field)).order_by(op+'avg_score')[0:5])
    question = "Hvaða spilari er með "
    if op == "-":
        question += "flestu "
    else:
        question += "fæstu "
    question += field + " að meðaltali í " + team.name + "?"
    poss = [stats[0]["player__ign"]]
    for p in Player.objects.filter(team=team).order_by('?'):
        if p.ign not in poss and len(poss) != 4:
            poss.append(p.ign)
    random.shuffle(poss)
    return (question, stats[0]["player__ign"] + ", með " + str(stats[0]["avg_score"]) + " " + field, poss)


# Hvaða lið tekur flesta/fæsta [dreka, heralds, barons, inhibs] í deildinni?
def getTeamWithMostObjs():
    objs = ["dragons", "barons", "heralds", "towers", "inhibs"]
    field = random.choice(objs)
    op = random.choice(["-", ""])
    stats = list(GameStats.objects.values("team__name").annotate(avg_score=Avg(field)).order_by(op+'avg_score'))
    question = "Hvert af þessum liðum er með "
    if op == "-":
        question += "flestu "
    else:
        question += "fæstu "
    question += field + " að meðaltali í deildinni?"
    poss = [stats[0]["team__name"]]
    for t in Team.objects.exclude(name__in=[s['team__name'] for s in stats if s == stats[0]["avg_score"]]).order_by('?'):
        if t.name not in poss and len(poss) != 4:
            poss.append(t.name)
    random.shuffle(poss)
    return (question, stats[0]["team__name"] + ", með " + str(stats[0]["avg_score"]) + " " + field, poss)


# Hvað er algengasti champion sem [team] bannar?
def getMostCommonBanTeamQuestion():
    team = getRandomTeam()
    games = list(Game.objects.filter(red_team_stats__team=team).values_list("red_team_stats", flat=True)) + \
            list(Game.objects.filter(blue_team_stats__team=team).values_list("blue_team_stats", flat=True))
    bans = list(GameStats.objects.filter(pk__in=games).values_list("bans", flat=True))
    most_common = Counter(bans).most_common()
    possibilities = []
    curr = ""
    curr_count = 0
    for c in most_common:
        if len(possibilities) == 5:
            break
        champ = Champion.objects.get(id=c[0]).name
        if c[1] != curr_count:
            possibilities.append((curr, str(int(curr_count / len(games) * 100)) + "%"))
            curr = ""
        if curr != "":
            curr += ", "
        curr += champ
        curr_count = c[1]
    if curr != "" and len(possibilities) != 5:
        possibilities.append((curr, str(int(curr_count / len(games) * 100)) + "%"))
    most = possibilities[1][0].split(", ")
    other = [most[0]]
    while len(other) != 4: 
        champ = Champion.objects.exclude(name__in=most).order_by('?').first()
        if champ.name not in other:
            other.append(champ.name)
    random.shuffle(other)
    return ("Hver af þessum champs er uppáhalds bannið hjá " + team.name + "?", most[0] + ", " + possibilities[1][1], other)


# Hvert er hlutfallið milli flash á d/f í deildinni?
def getFlashRatioQuestion():
    stats = PlayerStats.objects.filter(Q(summoner_d="Flash") | Q(summoner_f="Flash"))
    flash_d = stats.filter(summoner_d="Flash").count()
    flash_f = stats.filter(summoner_f="Flash").count()
    ans = str(flash_d / stats.count() * 100)[0:4]
    possibs = [ans]
    while len(possibs) != 4:
        op =  random.choice(["+", "-"]) 
        num = eval(str(ans) + op + str(random.randint(-10, 10)))
        if num not in possibs:
            possibs.append(num)
    possibilities = []
    for p in possibs:
        possibilities.append(str(p)[0:4] + "% D / " + str(100 - float(p))[0:4] + "% F")
    ans = possibilities[0]
    random.shuffle(possibilities)
    return ("Hvert er hlutfallið á milli flash á D/F í deildinni?", ans, possibilities)

# Í hvaða liði er [player]?
def getPlayerInTeam():
    player = getRandomPlayer()
    corr_team = player.team.name
    possibilities = [corr_team]
    while len(possibilities) != 4:
        team = getRandomTeam()
        if team.name not in possibilities:
            possibilities.append(team.name)
    random.shuffle(possibilities)
    return ("Hvaða lið spilar " + player.ign + " fyrir?", corr_team, possibilities)


# def getMostPopularSummonerSpell():
#     d = list(PlayerStats.objects.exclude(summoner_d="Flash").values("summoner_d").annotate(total=Count("summoner_d")).order_by('-total')[0:5])
#     f = list(PlayerStats.objects.exclude(summoner_f="Flash").values("summoner_f").annotate(total=Count("summoner_f")).order_by('-total')[0:5])
#     print(list(filter(lambda spell: spell['summoner_d'] == "Ignite", d))[0]['total'] + list(filter(lambda spell: spell['summoner_f'] == "Ignite", f))[0]['total'], "Ignite")
#     print(list(filter(lambda spell: spell['summoner_d'] == "Teleport", d))[0]['total'] + list(filter(lambda spell: spell['summoner_f'] == "Teleport", f))[0]['total'], "Teleport")

# getMostPopularSummonerSpell()
# def whosDaBest():
#     return ("Hvert er besti " + , ans, possibilities)



def getRandomQuestion():
    question_funcs = [
        # getAverageGameLengthQuestion,
        getMostBannedChampQuestion,
        getRandomPlayerNameQuestion,
        getNumChampionsQuestion,
        getFlashRatioQuestion,
        getMostCommonBanVsTeamQuestion,
        getMostKDAInLeagueQuestion,
        getMostKDAInLeagueQuestion,
        getMostKDAInTeamQuestion,
        getMostKDAInTeamQuestion,
        getMostKDAInTeamQuestion,
        getMostKDAInTeamQuestion,
        getPlayerInTeam,
        getTeamWithMostObjs,
        getTeamWithMostObjs,
        getMostCommonBanTeamQuestion
    ]
    return random.choice(question_funcs)()

# Hvaða lið tekur lengstu/stystu leikina að meðaltali?
# Hver spilaði jungle ziggs í leik x vs y
# Hver er junglerinn/top laner/mid/... í [team]?
# Hvað er algengasti summoner spellinn fyrir utan flash?
# Hvaða champion pickar [player] oftast?