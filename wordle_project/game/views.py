from django.shortcuts import render, redirect
import random
from django.http import JsonResponse, HttpResponseBadRequest,HttpResponseForbidden
import json
import datetime
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import F,Sum,Count
from .models import CustomUser, WordList, UserGuessHistory, DailyStats
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import user_passes_test


def index(request):

    if request.user.is_authenticated:

        user = request.user
        today = datetime.date.today()

        if user.last_guess_date != today:
            user.correct_guesses_today = 0
            user.last_guess_date = today
            user.words_played_today = 0 
            user.current_puzzle = None
            user.save()
        
        is_limit_reached = user.words_played_today >= 3 

        if is_limit_reached:
            request.session['secret_word'] = 'DAILYLIMITREACHED'
            return render(request, 'game/index.html') 
        
        current_game_in_session = request.session.get("word_date") == str(today)

        if user.current_puzzle and not current_game_in_session:
            request.session['secret_word'] = user.current_puzzle.word.upper()
            request.session['word_date'] = str(today)
            request.session.save()
            return render(request, 'game/index.html')  
              
        if not current_game_in_session and not is_limit_reached:

            played_words_today_ids = UserGuessHistory.objects.filter(
            user=user, date=today
            ).values_list("word_to_guess_id", flat=True)

            available_words = WordList.objects.exclude(id__in=played_words_today_ids)

            if available_words.exists():
                random_word = available_words.order_by("?").first()

                request.session["secret_word"] = random_word.word.upper()
                request.session["word_date"] = str(today)
                user.current_puzzle = random_word
                user.save()
                UserGuessHistory.objects.get_or_create(
                    user=user, word_to_guess=random_word, date=today
                )
                request.session.save()

    return render(request, "game/index.html")


def signup_view(request):
    """Handles user registration and automatic login."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():

            user = form.save()
            login(request, user)

            messages.success(request, f"Account created for {user.username}! Welcome.")
            return redirect("index")

    else:
        form = CustomUserCreationForm()

    # Render the sign-up page template with the form
    return render(request, "game/signup.html", {"form": form})


def check_guess(request):
    """
    Handles the AJAX request to check a user's guess and update game state.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method.")

    if not request.user.is_authenticated:
        return JsonResponse({"message": "You must be logged in to play."})

    user = request.user
    today = datetime.date.today()

    if user.words_played_today >= 3:
        return JsonResponse(
            {"message": "You've reached your daily limit of 3 correct guesses."}
        )

    try:
        current_word_instance = WordList.objects.get(
            word=request.session.get("secret_word")
        )
        history = UserGuessHistory.objects.get(
            user=user, word_to_guess=current_word_instance, date=today
        )
    except (WordList.DoesNotExist, UserGuessHistory.DoesNotExist):
        return HttpResponseBadRequest("Game state not found. Please refresh.")

    try:
        data = json.loads(request.body)
        guess = data.get("guess", "").upper()
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON.")
  
    if len(guess) != 5:
        return HttpResponseBadRequest("Guess must be 5 letters long.")

    secret_word = request.session.get("secret_word", "").upper()
    results = []
    secret_word_letters = list(secret_word)

    for i in range(5):
        if guess[i] == secret_word[i]:
            results.append("correct")
            secret_word_letters[i] = None
        else:
            results.append(None)

    # Second pass: find correct letters in the wrong position (yellow) and wrong letters (grey).
    for i in range(5):
        if results[i] is None:
            if guess[i] in secret_word_letters:
                results[i] = "misplaced"
                secret_word_letters[secret_word_letters.index(guess[i])] = None
            else:
                results[i] = "wrong"

    daily_stats, created = DailyStats.objects.get_or_create(
        user=user,
        date=today,
    )

    daily_stats.words_tried = F("words_tried") + 1
    daily_stats.save()

    is_correct_guess = guess == secret_word

    history.guesses.append(guess)
    history.is_solved = is_correct_guess
    history.save()

    if is_correct_guess:
        user.correct_guesses_today = F("correct_guesses_today") + 1
        daily_stats.words_solved = F('words_solved') + 1
        daily_stats.save()
        user.save()
    game_over = is_correct_guess or len(history.guesses) >= 5

    if game_over:
        user.words_played_today = F('words_played_today') + 1 
        user.current_puzzle = None 
        user.save()
        if "secret_word" in request.session:
            del request.session["secret_word"]
        if "word_date" in request.session:
            del request.session["word_date"]

    if not is_correct_guess and len(history.guesses) >= 5:
        return JsonResponse(
            {
                "results": results,
                "is_correct": False,
                "guesses": history.guesses,
            }
        )

    return JsonResponse(
        {
            "results": results, 
            "is_correct": is_correct_guess, 
            "guesses": history.guesses
        }
    )

#Handle this as on frontend each time it reloads this function is called so should handle all 3 states
def get_game_state_api(request):
    """
    Returns the user's current game state and history for frontend restoration.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not logged in'}, status=401)

    user = request.user
    today = datetime.date.today()
    secret_word = request.session.get('secret_word')
    
    # Check for game over states first
    if secret_word == 'DAILYLIMITREACHED':
        return JsonResponse({'status': secret_word})

    try:
        # Find the existing history object
        current_word_instance = WordList.objects.get(word=secret_word)
        history = UserGuessHistory.objects.get(
            user=user, 
            word_to_guess=current_word_instance, 
            date=today
        )
    except (WordList.DoesNotExist, UserGuessHistory.DoesNotExist):
        return JsonResponse({'error': 'Game not initialized'}, status=404)

    # Calculate results array for every guess in history
    restored_results = []
    
    # We must re-run the grading algorithm for each guess to get the color array back.
    # Note: This uses the complex logic from check_guess for each historical guess.
    
    for historical_guess in history.guesses:
        
        # --- RE-RUNNING THE GRADING ALGORITHM ---
        
        results = []
        secret_word_letters = list(secret_word) # Reset available letters for each new guess
        
        # Pass 1: Correct (Green)
        for i in range(5):
            if historical_guess[i] == secret_word[i]:
                results.append('correct')
                secret_word_letters[i] = None
            else:
                results.append(None)

        # Pass 2: Misplaced (Yellow) and Wrong (Gray)
        for i in range(5):
            if results[i] is None:
                if historical_guess[i] in secret_word_letters:
                    results[i] = 'misplaced'
                    # Consume the letter
                    secret_word_letters[secret_word_letters.index(historical_guess[i])] = None
                else:
                    results[i] = 'wrong'
        
        restored_results.append(results)
        
    return JsonResponse({
        'status': 'active',
        'guesses': history.guesses,
        'results_history': restored_results,
        'is_solved': history.is_solved,
        'current_row': len(history.guesses)
    })




def admin_homepage_view(request):
    """
    Renders the custom admin landing page, displaying immediate site metrics
    and historical statistics, overriding the standard /admin/ view.
    """
    
    if not request.user.is_staff:
         return HttpResponseForbidden("Access Denied: Must be staff.") 

    today = datetime.date.today()

    # --- Site Summary ---
    total_users_played = DailyStats.objects.filter(date=today).count()
    total_wins_today = DailyStats.objects.filter(date=today).aggregate(
        total_wins=Sum('words_solved')
    )['total_wins'] or 0

    # --- Historical Table ---
    # Groups by date to show the site-wide performance history
    historical_stats = DailyStats.objects.values('date').annotate(
        total_users=Count('user'),
        total_wins=Sum('words_solved')
    ).order_by('-date')

    # --- Fetch All Users (for linking) ---
    all_users = CustomUser.objects.all().order_by('username')
    daily_stats_detail = DailyStats.objects.select_related('user').order_by('-date', 'user__username')

    context = {
        'total_users_played': total_users_played,
        'total_wins_today': total_wins_today,
        'historical_stats': historical_stats,
        'daily_stats_detail': daily_stats_detail, 
        'all_users': all_users,
        'today_date': today,
        'site_title': 'Wordle Admin Home'
    }
    
    return render(request, 'admin/custom_index.html', context)
