import os
from django.core.management.base import BaseCommand
from game.models import WordList
from django.db import IntegrityError

# Define the path to your words file, which should be in the project root
FILE_PATH = 'words.txt'

class Command(BaseCommand):
    """
    A custom management command to populate the WordList model
    from the words.txt file.
    """
    help = 'Populates the WordList model with words from words.txt.'

    def handle(self, *args, **options):
        # 1. Check if the file exists
        if not os.path.exists(FILE_PATH):
            self.stdout.write(self.style.ERROR(f'File not found: {FILE_PATH}'))
            return
        
        self.stdout.write(self.style.SUCCESS('Starting WordList population...'))
        
        # 2. Read and filter words from the file
        with open(FILE_PATH, 'r') as f:
            # Reads lines, strips whitespace, converts to uppercase, and ensures word length is 5
            words = [line.strip().upper() for line in f if len(line.strip()) == 5][:20]

        created_count = 0
        total_words = len(words)

        # 3. Insert words into the database
        for word in words:
            try:
                # Tries to create the word
                WordList.objects.create(word=word)
                created_count += 1
                self.stdout.write(f'Added: {word}')
            except IntegrityError:
                # Catches IntegrityError if the word already exists (due to unique=True constraint)
                self.stdout.write(self.style.WARNING(f'Word "{word}" already exists. Skipping.'))
            except Exception as e:
                # Catch any other database errors
                self.stdout.write(self.style.ERROR(f'Error adding word "{word}": {e}'))

        # 4. Final output summary
        self.stdout.write(self.style.SUCCESS(f'\n--- Population Complete ---'))
        self.stdout.write(self.style.SUCCESS(f'Successfully added {created_count} words out of {total_words} processed.'))