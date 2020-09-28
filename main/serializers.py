from rest_framework import serializers

from .models import Team, Player, Tournament, Champion, PlayerStats, GameStats, Game, HighScore

class TeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Team
        fields = ('id','name','logo')
        depth = 1

class HighScoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HighScore
        fields = ('id','name','score','created_at')


class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Player
        fields = ('id','name','ign','nationality','team','main_role','secondary_role')
        depth = 1


class TournamentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tournament
        fields = ('id','name','season','teams')
        depth = 1


class ChampionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Champion
        fields = ('id','name','photo')
        depth = 1


class PlayerStatsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PlayerStats
        fields = ('id','player','champion','game_stats','summoner_d','summoner_f','role','kills','deaths','assists','cs','gold')
        depth = 1

class GameStatsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GameStats
        fields = ('id','team','side','winner','gold','date','towers','inhibs','dragons','barons','heralds','bans', 'player_stats')
        depth = 1

class GameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Game
        fields = ('id','tournament','blue_team_stats','red_team_stats','duration','date')
        depth = 1
