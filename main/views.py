from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
# Create your views here.
from helpers.questions import getRandomQuestion
from rest_framework import viewsets
from rest_framework.response import Response
from django.core.management.utils import get_random_secret_key
from .serializers import TeamSerializer, PlayerSerializer, TournamentSerializer, ChampionSerializer, PlayerStatsSerializer, GameStatsSerializer, GameSerializer
from .models import Team, Player, Tournament, Champion, PlayerStats, GameStats, Game, Question, Secret, HighScore
from rest_framework.decorators import api_view
import json
from datetime import datetime
import pytz
@api_view(['GET'])
def get_secret_key(request):
    # print(get_random_secret_key())
    sec = Secret.objects.create(secret=get_random_secret_key())
    return Response({
        "secret": sec.secret,
    })

@api_view(['GET'])
def get_question(request):
    rand = getRandomQuestion()
    ans = Question.objects.create(answer=rand[1])
    return Response({
        "question": rand[0],
        "ans_id": ans.id,
        "possibilities": rand[2],
    })

@api_view(['POST'])
def get_new_question(request):
    i = 0
    questions = json.loads(request.body)["answered"]
    while i < 100:
        i += 1
        q = getRandomQuestion()
        if q[0] in questions:
            continue
        else:
            break
    ans = Question.objects.create(answer=q[1])
    return Response({
        "question": q[0],
        "ans_id": ans.id,
        "possibilities": q[2],
    })

@api_view(['POST'])
def add_high_score(request):
    scored = False
    try:
        res = json.loads(request.body)
        s = Secret.objects.get(secret=res["secret"])
        diff = datetime.now().replace(tzinfo=pytz.UTC) - s.created_at
        s.delete()
        if int(diff.total_seconds()) > 2:
            return Response({"scored": False})
        for i in reversed(HighScore.objects.all().order_by('-score')[0:10]):
            if int(res["highscore"]) >= i.score or HighScore.objects.all().count() < 10:
                HighScore.objects.create(name=res["name"], score=int(res["highscore"]))
                scored = True
                if HighScore.objects.all().count() > 10:
                    i.delete()
                break
        return Response({"scored": scored})
    except:
        return Response({{"scored": False}})

@api_view(['GET'])
def get_high_scores(request):
    return Response({"highscores": list(HighScore.objects.all().order_by('-score', '-created_at').values("name", "score", "created_at"))})

@api_view(['GET'])
def get_answer(request, id):
    try:
        ans = Question.objects.get(id=id)
        answer = ans.answer
        ans.delete()
        return Response({
            "answer": answer,
        })
    except:
        return Response({
            "answer": "Hey, bannað að svindla! :(",
        })
        
class HighScoreViewSet(viewsets.ModelViewSet):
    queryset = HighScore.objects.all().order_by('score')
    serializer_class = TeamSerializer
    http_method_names = ['get']

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all().order_by('name')
    serializer_class = TeamSerializer
    http_method_names = ['get']

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all().order_by('ign')
    serializer_class = PlayerSerializer
    http_method_names = ['get']

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all().order_by('name', 'season')
    serializer_class = TournamentSerializer
    http_method_names = ['get']

class ChampionViewSet(viewsets.ModelViewSet):
    queryset = Champion.objects.all().order_by('name')
    serializer_class = ChampionSerializer
    http_method_names = ['get']

class PlayerStatsViewSet(viewsets.ModelViewSet):
    queryset = PlayerStats.objects.all().order_by('player')
    serializer_class = PlayerStatsSerializer
    http_method_names = ['get']

class GameStatsViewSet(viewsets.ModelViewSet):
    queryset = GameStats.objects.all().order_by('team', 'date')
    serializer_class = GameStatsSerializer
    http_method_names = ['get']

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all().order_by('blue_team_stats', 'red_team_stats')
    serializer_class = GameSerializer
    http_method_names = ['get']

