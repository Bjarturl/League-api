from django.db import models

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=999, unique=True)
    logo = models.CharField(max_length=999)
    def __str__(self):
        return self.name

class HighScore(models.Model):
    name = models.CharField(max_length=999)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name + " - " + str(self.score) + " points"


class Secret(models.Model):
    secret = models.CharField(max_length=999)
    created_at = models.DateTimeField(auto_now_add=True)


class Question(models.Model):
    answer = models.CharField(max_length=999)
    def __str__(self):
        return self.answer

class Player(models.Model):
    name = models.CharField(max_length=999)
    ign = models.CharField(max_length=999)
    nationality = models.CharField(max_length=999)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    main_role = models.CharField(max_length=999)    
    secondary_role = models.CharField(max_length=999, null=True)    
    def __str__(self):
        return self.ign + " - " + self.team.name

class Tournament(models.Model):
    name = models.CharField(max_length=999)
    season = models.CharField(max_length=999, null=True)
    teams = models.ManyToManyField(Team)
    def __str__(self):
        return self.name

class Champion(models.Model):
    name = models.CharField(max_length=999)
    photo = models.CharField(max_length=999, null=True)
    def __str__(self):
        return self.name

class PlayerStats(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    champion = models.ForeignKey(Champion, on_delete=models.CASCADE)
    game_stats = models.ForeignKey('main.GameStats', on_delete=models.CASCADE, null=True)
    summoner_d = models.CharField(max_length=999)
    summoner_f = models.CharField(max_length=999)
    role = models.CharField(max_length=999, null=True)
    kills = models.IntegerField()
    deaths = models.IntegerField()
    assists = models.IntegerField()
    cs = models.IntegerField()
    gold = models.IntegerField()
    class Meta:
        verbose_name_plural = "player stats"
    def __str__(self):
        return self.player.ign

class GameStats(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    side = models.CharField(max_length=999)
    winner = models.BooleanField()
    gold = models.IntegerField()
    date = models.DateField()
    towers = models.IntegerField()
    inhibs = models.IntegerField()
    dragons = models.IntegerField()
    barons = models.IntegerField()
    heralds = models.IntegerField()
    bans = models.ManyToManyField(Champion)
    player_stats = models.ManyToManyField(PlayerStats)
    class Meta:
        verbose_name_plural = "game stats"
    def __str__(self):
        return self.team.name + (" (winner)" if self.winner else "")

class Game(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    blue_team_stats = models.ForeignKey(GameStats, on_delete=models.CASCADE, related_name="blue")
    red_team_stats = models.ForeignKey(GameStats, on_delete=models.CASCADE, related_name="red")
    duration = models.TimeField(null=True, blank=True)
    date = models.DateField(null=True)

    def getTitle(self):
        return self.blue_team_stats.team.name + " vs " + self.red_team_stats.team.name + " - " + str(self.date)
    
    def __str__(self):
        return self.getTitle()












