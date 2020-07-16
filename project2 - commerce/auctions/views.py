from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.db.models import Max

from .models import User, Listing, Bid, Watchlist, Comment


def index(request):
    listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {'listings': listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='login')
def create(request):
    if request.method == "GET":
        args = {'choices': [cat[0] for cat in Listing.CATEGORIES]} # Get Category Choices From Model
        return render(request, "auctions/create.html", args)
    else:
        title = request.POST["title"]
        desc = request.POST["desc"]
        startbid = request.POST["startbid"]
        image_url = request.POST["image-url"]
        category = request.POST["category"]

        try:
            listing = Listing.objects.create(title=title, 
                description=desc, 
                start_bid=startbid, 
                image_url=image_url, 
                category=category,
                creator=request.user)
            listing.save()
        except Exception as e:
            print(e)
            return HttpResponse("Something Went Wrong!")
        listing_url = reverse('listing', args=[listing.id])
        return HttpResponseRedirect(listing_url) # Redirects to Created Listing

def listing(request, id):
    if request.method == "GET":
        listing = Listing.objects.get(pk=id)
        args = {'listing': listing}
        if not request.user.is_anonymous:
            args.update({'watch': Watchlist.objects.filter(listingID=id, userID=request.user)})
        args.update({'comments': Comment.objects.filter(listingID=id)})
        
        bids = [float(bid.bid_amount) for bid in Bid.objects.filter(listingID=id)]
        args.update({'bids': bids})
        if len(bids) > 0:
            args.update({'max_bid': max(bids)})

        if listing.active == False:
            win_bid = Bid.objects.get(listingID=id, winner=True)
            args.update({'win_bid': win_bid})

        return render(request, "auctions/listing.html", args)
    else:
        listing = Listing.objects.get(pk=id)

        if 'watchlist' in request.POST:
            if request.POST['watchlist'] == 'add':
                try:
                    add = Watchlist.objects.create(listingID=listing, userID=request.user)
                    add.save()
                    messages.success(request, 'Added to watchlist!')
                except Exception as e:
                    print(e)
                    messages.error(request, 'Something went wrong!')
            else:
                try:
                    watch = Watchlist.objects.get(pk=request.POST.get('watchlist'))
                    watch.delete()
                    messages.success(request, 'Removed from watchlist!')
                except Exception as e:
                    print(e)
                    messages.error(request, 'Something went wrong!')
        elif 'bid' in request.POST:
            bid_value = float(request.POST.get('bid-value'))
            bids_placed = [bid.bid_amount for bid in Bid.objects.filter(listingID=id)]

            if bid_value < listing.start_bid or (len(bids_placed) > 0 and bid_value < max(bids_placed)):
                messages.warning(request, 'Bid Amount Insufficient!')                
            else:
                try:
                    bid = Bid.objects.create(bid_amount=bid_value, listingID=listing, userID=request.user)
                    bid.save()
                    messages.success(request, 'Bid Placed!')
                except Exception as e:
                    print(e)
                    messages.error(request, 'Something went wrong!')
        elif 'add-comment' in request.POST:
            comment = request.POST.get('comment')
            try:
                new_comment = Comment.objects.create(listingID=listing, userID=request.user, comment=comment)
                new_comment.save()
                messages.success(request, 'Comment Added!')
            except Exception as e:
                print(e)
                messages.error(request, 'Something went wrong!')
        elif 'close' in request.POST:
            bids = Bid.objects.filter(listingID=id)
            if len(bids) < 0:
                messages.success(request, "Listing Closed. 0 Bids.")
            else:
                max_bid = bids.order_by('bid_amount').last()
                max_bid.winner = True
                max_bid.save()
                messages.success(request, "Listing Closed. Bid Winner: {}".format(max_bid.userID))
            listing.active = False
            listing.save()
        else:
            print(request.POST)
            messages.error(request, "Invalid request")
        listing_url = reverse('listing', args=[id])
        return HttpResponseRedirect(listing_url)

@login_required(login_url='login')
def watchlist(request):
    watchlist = Watchlist.objects.filter(userID=request.user)
    args = {'watchlist': watchlist}
    return render(request, "auctions/watchlist.html", args)

def categories(request, category=None):
    if category is None:
        args = {'categories': [cat[0] for cat in Listing.CATEGORIES]}
        return render(request, "auctions/categories.html", args)
    else:
        args = {'category': category}
        category_listings = Listing.objects.filter(category=category, active=True)
        args.update({'listings': category_listings})
        return render(request, "auctions/category.html", args)