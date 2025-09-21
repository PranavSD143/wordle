from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, WordList, UserGuessHistory,DailyStats
from django.db.models import Sum, Count
from django.urls import path

class DailyStatsInline(admin.StackedInline):
    model = DailyStats
    extra = 0 
    readonly_fields = ('date', 'words_tried', 'words_solved')
    can_delete = False


class CustomUserAdmin(UserAdmin):

    list_display = ('username', 'email', 'is_staff') 
    inlines = [DailyStatsInline] 
    
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Wordle Stats', {
            'fields': (
                'correct_guesses_today',
                'last_guess_date',
                'words_played_today', 
            )
        }),
    )
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(DailyStats)  
admin.site.register(WordList)
admin.site.register(UserGuessHistory)