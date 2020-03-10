''' models for storing different kinds of Activities '''
from datetime import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from model_utils.managers import InheritanceManager
import urllib.parse

from fedireads.utils.models import FedireadsModel


class Status(FedireadsModel):
    ''' any post, like a reply to a review, etc '''
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    status_type = models.CharField(max_length=255, default='Note')
    content = models.TextField(blank=True, null=True)
    mention_users = models.ManyToManyField('User', related_name='mention_user')
    mention_books = models.ManyToManyField('Book', related_name='mention_book')
    activity_type = models.CharField(max_length=255, default='Note')
    local = models.BooleanField(default=True)
    privacy = models.CharField(max_length=255, default='public')
    sensitive = models.BooleanField(default=False)
    # the created date can't be this, because of receiving federated posts
    published_date = models.DateTimeField(default=datetime.now)
    favorites = models.ManyToManyField(
        'User',
        symmetrical=False,
        through='Favorite',
        through_fields=('status', 'user'),
        related_name='user_favorites'
    )
    reply_parent = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.PROTECT
    )
    objects = InheritanceManager()


class Review(Status):
    ''' a book review '''
    name = models.CharField(max_length=255)
    book = models.ForeignKey('Book', on_delete=models.PROTECT)
    rating = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    def save(self, *args, **kwargs):
        self.status_type = 'Review'
        self.activity_type = 'Article'
        super().save(*args, **kwargs)


class Favorite(FedireadsModel):
    ''' fav'ing a post '''
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    status = models.ForeignKey('Status', on_delete=models.PROTECT)

    class Meta:
        unique_together = ('user', 'status')


class Tag(FedireadsModel):
    ''' freeform tags for books '''
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    book = models.ForeignKey('Book', on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.id:
            # add identifiers to new tags
            self.identifier = urllib.parse.quote_plus(self.name)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'book', 'name')


class Notification(FedireadsModel):
    ''' you've been tagged, liked, followed, etc '''
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    related_book = models.ForeignKey(
        'Book', on_delete=models.PROTECT, null=True)
    related_user = models.ForeignKey(
        'User',
        on_delete=models.PROTECT, null=True, related_name='related_user')
    related_status = models.ForeignKey(
        'Status', on_delete=models.PROTECT, null=True)
    read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        # TODO: there's probably a real way to do enums
        types = [
            'FAVORITE',
            'REPLY',
            'TAG',
            'FOLLOW'
        ]
        if not self.notification_type in types:
            raise ValueError('Invalid notitication type')
        super().save(*args, **kwargs)
