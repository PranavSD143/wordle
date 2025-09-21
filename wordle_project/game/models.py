from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
        
    correct_guesses_today = models.IntegerField(default=0)
    last_guess_date = models.DateField(null=True, blank=True)
    words_played_today = models.IntegerField(default=0) 
    
    current_puzzle = models.ForeignKey(
        'WordList', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='current_solvers'
    )

class WordList(models.Model):

    word = models.CharField(max_length=5, unique=True)
        
    def __str__(self):
        return self.word
    
class UserGuessHistory(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    word_to_guess = models.ForeignKey(WordList, on_delete=models.CASCADE)
    guesses = models.JSONField(default=list)  # Stores a list of strings
    is_solved = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)
    
    class Meta:
        # Ensures a user can only have one history entry per word
        unique_together = ('user', 'word_to_guess', 'date')

    def __str__(self):
        return f'{self.user.username} to guess {self.word_to_guess.word}'


class DailyStats(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    date = models.DateField()
    words_tried = models.IntegerField(default=0)
    words_solved = models.IntegerField(default=0) 
    
    class Meta:
        unique_together = ('user', 'date')
        verbose_name_plural = "Daily Stats"
        
    def __str__(self):
        return f"{self.user.username}'s Stats on {self.date}"