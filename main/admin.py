from django.contrib import admin
from main.models import *
# Register your models here.
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Tournament)
admin.site.register(Champion)
admin.site.register(PlayerStats)
admin.site.register(GameStats)
admin.site.register(Game)
admin.site.register(HighScore)