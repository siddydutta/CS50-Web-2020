from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
	CATEGORIES = (
		('None', 'None'),
		('Fashion', 'Fashion'),
		('Electronics', 'Electronics'),
		('Books', 'Books'),
		('Home Products', 'Home Products'))
	title = models.CharField(max_length=50)
	description = models.TextField(max_length=999)
	start_bid = models.DecimalField(max_digits=10, decimal_places=2)
	image_url = models.URLField(blank=True)
	category = models.CharField(max_length=20, choices=CATEGORIES, default='None')
	active = models.BooleanField(default=True)
	creator = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.title

class Watchlist(models.Model):
	listingID = models.ForeignKey(Listing, on_delete=models.CASCADE)
	userID = models.ForeignKey(User, on_delete=models.CASCADE)

class Bid(models.Model):
	bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
	winner = models.BooleanField(default=False)
	listingID = models.ForeignKey(Listing, on_delete=models.CASCADE)
	userID = models.ForeignKey(User, on_delete=models.CASCADE)

class Comment(models.Model):
	comment = models.TextField(max_length=999)
	listingID = models.ForeignKey(Listing, on_delete=models.CASCADE)
	userID = models.ForeignKey(User, on_delete=models.CASCADE)
