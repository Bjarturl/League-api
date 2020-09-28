from django.urls import include, path
from rest_framework import routers
from . import views
router = routers.DefaultRouter()
router.register(r'teams', views.TeamViewSet)
router.register(r'players', views.PlayerViewSet)
router.register(r'tournaments', views.TournamentViewSet)
router.register(r'champions', views.ChampionViewSet)
router.register(r'playerStats', views.PlayerStatsViewSet)
router.register(r'gameStats', views.GameStatsViewSet)
router.register(r'games', views.GameViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('question/', views.get_question),
    path('secret/', views.get_secret_key),
    path('add_high_score/', views.add_high_score),
    path('get_high_scores/', views.get_high_scores),
    path('new_question', views.get_new_question),
    path('answer/<int:id>', views.get_answer),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]