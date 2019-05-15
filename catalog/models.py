from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
import uuid


class Genre(models.Model):
    """Model representing a book genere"""
    name = models.CharField(max_length=200,
                            help_text='Enter a book genere (e.g. Science Fiction)')

    def __str__(self):
        """String for representing the Model object"""
        return self.name


class Language(models.Model):
    """Model representing a language"""
    name = models.CharField(max_length=100, help_text='What language is this book written in')

    def __str__(self):
        return self.name


class Book(models.Model):
    """Model representing a book (but not a specific copy of that book)"""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=10000,
                               help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=14,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre,
                                   help_text='Select a genre for this book')
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin"""
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'genre'

    def __str__(self):
        """String representing the model object"""
        return self.title

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book"""
        return reverse('book-detail', args=[str(self.id)])


class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. one that can be borrowed from the library)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Unique ID for this particular book across the whole library')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)

    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    due_back = models.DateField(null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True,
                              default='m', help_text='Book availability')

    class Meta:
        ordering = ['due_back']
        permissions = (
            ('can_mark_returned', 'Set book as returned'),
        )


    @property
    def is_overdue(self):
        if self.due_back and timezone.now().date() > self.due_back:
            return True
        return False

    def __str__(self):
        """String representing the Model object"""
        return f'{self.id} ({self.book.title})'


class Author(models.Model):
    """Model representing the author of a book"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance"""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String representing the Model object"""
        return f'{self.last_name}, {self.first_name}'
