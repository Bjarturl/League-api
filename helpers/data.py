import urllib.request
import json
from bs4 import BeautifulSoup as bs
from main.models import *


def getParse(url): #Send request to url and receive html
    page = urllib.request.urlopen(url)
    return bs(page, 'lxml')


def getTeams(url): #Get team name, info and players
    parse = getParse(url)
    teams = {}
    player_tables = parse.findAll("div", {"class": "wide-content-scroll"})
    index = 0
    for team in parse.findAll("span", {"class": "team"}): #For each team
        name = team.text.strip().replace("\u2060", "")
        logo = team.find("img")['src'].split(".png")[0]+".png"
        players = []
        for p in player_tables[index].findAll("tr")[1:]: #For each player in each team
            if p:
                player = {
                    "ign": getAttrIfExists(p, "td", "extended-rosters-id"),
                    "name": getAttrIfExists(p, "td", "extended-rosters-name"),
                    "country": getAttrIfExists(getAttrIfExists(p, "td", "extended-rosters-country", False), "span", None, False, 'title'),
                    "roles": [],
                }
                role = getAttrIfExists(getAttrIfExists(p, "td", "extended-rosters-role", False), "span", None, False, 'title')
                if role: #Remove 'laner' from text
                    role = role.split(" ")[0]
                    if player["ign"]: #If player has ign add role to list 
                        player["roles"].append(role)
                    else: #Else add to previous player list
                        players[-1]["roles"].append(role)
                if player["ign"]: #Only add player if they have IGN
                    players.append(player)
        index += 1
        teams[name] = {
            "logo": logo,
            "players": players
        }
    return teams


def getTournament(teams_url, season):
    tourney, _ = Tournament.objects.get_or_create(name="Icelandic Esports League", season=season)
    teams = getTeams(teams_url)
    for t in teams:
        team, _ = Team.objects.get_or_create(name=t)
        team.logo = teams[t]['logo']
        team.save()
        for p in teams[t]['players']:
            secondary = None
            if len(p["roles"]) > 1:
                secondary = p["roles"][1]
            player, _ = Player.objects.get_or_create(
                name=p["name"],
                ign=p["ign"],
                nationality=p["country"],
                team=team,
                main_role=p["roles"][0],
                secondary_role=secondary,
            )
            player.save()
        tourney.teams.add(team)
    return tourney

def getAttrIfExists(parse, tag, className=None, text=True, key=None): #Useful function for parsing unknown tags
    try:
        if className:
            val = parse.find(tag, {"class": className})
        else:
            val = parse.find(tag
            )
        if text:
            return val.text
        elif key:
            return val[key]
        else:
            return val
    except:
        return None


def deleteAll(): #Clear database
    Team.objects.all().delete()
    Player.objects.all().delete()
    Tournament.objects.all().delete()
    Champion.objects.all().delete()
    PlayerStats.objects.all().delete()
    GameStats.objects.all().delete()
    Game.objects.all().delete()

def getGameStats(scoreboard_url, teams_url, season):
    parse = getParse(scoreboard_url)
    games = parse.findAll("div", {"class": "inline-content"})
    tourney = getTournament(teams_url, season)
    for g in games:
        blueGameStats, _ = GameStats.objects.get_or_create( #Create blue team game stats
            team=Team.objects.get(name__contains=g.findAll("span", {"class": "teamname"})[0].find("a").text),
            side="blue",
            winner= False if g.find("th", {"class": "sb-score-winner"})['class'][0].split("-")[1] == "red" else True,
            gold=int(float(g.findAll("div", {"class": "sb-header"})[0].text.split(" ")[1].replace("k",""))*1000),
            date="-".join(g.find("div", {"class": "sb-datetime"}).find("span").text.split(",")[0:3]),
            towers=int(g.findAll("div", {"title": "Towers"})[0].text),
            inhibs=int(g.findAll("div", {"title": "Inhibitors"})[0].text),
            dragons=int(g.findAll("div", {"title": "Dragons"})[0].text),
            barons=int(g.findAll("div", {"title": "Barons"})[0].text),
            heralds=int(g.findAll("div", {"title": "Rift Heralds"})[0].text),
        )
        blue_bans = [span['title'] for span in g.findAll("div", {"class": "sb-footer-bans"})[0].findAll("span")]
        for b in blue_bans: #Add bans for blue team
            champ, _ = Champion.objects.get_or_create(name=b)
            blueGameStats.bans.add(champ)
        redGameStats, _ = GameStats.objects.get_or_create( #Create red team game stats
            team=Team.objects.get(name__contains=g.findAll("span", {"class": "teamname"})[1].find("a").text),
            side="red",
            winner= True if g.find("th", {"class": "sb-score-winner"})['class'][0].split("-")[1] == "red" else False,
            gold=int(float(g.findAll("div", {"class": "sb-header"})[1].text.split(" ")[1].replace("k",""))*1000),
            date="-".join(g.find("div", {"class": "sb-datetime"}).find("span").text.split(",")[0:3]),
            towers=int(g.findAll("div", {"title": "Towers"})[1].text),
            inhibs=int(g.findAll("div", {"title": "Inhibitors"})[1].text),
            dragons=int(g.findAll("div", {"title": "Dragons"})[1].text),
            barons=int(g.findAll("div", {"title": "Barons"})[1].text),
            heralds=int(g.findAll("div", {"title": "Rift Heralds"})[1].text),
        )
        red_bans = [span['title'] for span in g.findAll("div", {"class": "sb-footer-bans"})[2].findAll("span")]
        for b in red_bans: #Add bans for red team
            champ, _ = Champion.objects.get_or_create(name=b)
            redGameStats.bans.add(champ)
        duration = "00:" + g.find("tr", {"class": "sb-allw"}).findAll("th")[1].text
        roles = ["Top", "Jungler", "Mid", "Bot", "Support"]
        #Get player stats for each player
        for p in g.find("td", {"class": "side-blue"}).findAll("div", {"class": "sb-p"}):
            champ, _ = Champion.objects.get_or_create(name=p.find("div", {"class": "sb-p-champion"}).find("span")['title'])
            kda = p.find("div", {"class": "sb-p-stats"}).findAll("div")[0].text.split("/")
            playerStats, _ = PlayerStats.objects.get_or_create(
                player=Player.objects.get(ign=p.find("div", {"class": "sb-p-info"}).findAll("a")[0].text),
                champion=champ,
                summoner_d=p.find("div", {"class": "sb-p-summoners"}).findAll("span")[0]['title'],
                summoner_f=p.find("div", {"class": "sb-p-summoners"}).findAll("span")[1]['title'],
                kills=kda[0],
                deaths=kda[1],
                role=roles.pop(0),
                assists=kda[2],
                cs=int(p.find("div", {"class": "sb-p-stats"}).findAll("div")[1].text),
                game_stats=blueGameStats,
                gold=int(float(p.find("div", {"class": "sb-p-stats"}).findAll("div")[2].text.replace("k", ""))*1000),
            )
            blueGameStats.player_stats.add(playerStats)
        roles = ["Top", "Jungler", "Mid", "Bot", "Support"]
        for p in g.find("td", {"class": "side-red"}).findAll("div", {"class": "sb-p"}):
            champ, _ = Champion.objects.get_or_create(name=p.find("div", {"class": "sb-p-champion"}).find("span")['title'])
            kda = p.find("div", {"class": "sb-p-stats"}).findAll("div")[0].text.split("/")
            playerStats, _ = PlayerStats.objects.get_or_create(
                player=Player.objects.get(ign=p.find("div", {"class": "sb-p-info"}).findAll("a")[0].text),
                champion=champ,
                summoner_d=p.find("div", {"class": "sb-p-summoners"}).findAll("span")[0]['title'],
                summoner_f=p.find("div", {"class": "sb-p-summoners"}).findAll("span")[1]['title'],
                kills=kda[0],
                deaths=kda[1],
                role=roles.pop(0),
                assists=kda[2],
                cs=int(p.find("div", {"class": "sb-p-stats"}).findAll("div")[1].text),
                game_stats=redGameStats,
                gold=int(float(p.find("div", {"class": "sb-p-stats"}).findAll("div")[2].text.replace("k", ""))*1000),
            )
            redGameStats.player_stats.add(playerStats)
        game, _ = Game.objects.get_or_create( #Create game from stats
            tournament=tourney,
            blue_team_stats=blueGameStats,
            red_team_stats=redGameStats,
            duration=duration,
            date="-".join(g.find("div", {"class": "sb-datetime"}).find("span").text.split(",")[0:3]),
        )

#python manage.py shell < helpers/data.py 
# deleteAll()
scoreboard_urls = [
    "https://lol.gamepedia.com/Icelandic_Esports_League/Season_4/Scoreboards",
    "https://lol.gamepedia.com/Icelandic_Esports_League/Season_4/Scoreboards/Week_2",
    "https://lol.gamepedia.com/Icelandic_Esports_League/Season_4/Scoreboards/Week_3",
] 
teams_url = "https://lol.gamepedia.com/Icelandic_Esports_League/Season_4/Team_Rosters"

for s_url in scoreboard_urls:  
    getGameStats(s_url, teams_url, "Season 4")

# for i in range(10):
#     HighScore.objects.create(name="Unknown", score=0)