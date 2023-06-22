from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from .models import Listing, User,Bid,Comment,Watchlist
from django.shortcuts import redirect

def index(request):
    return render(request, "auctions/index.html",{
        "listings": Listing.objects.all()
    })


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

def listing(request,id):
    watchlist = None
    if request.method == "POST":
        try:
            username = request.POST["username"]
            if username is not None:
                watchlist = Watchlist.objects.get(listing=Listing.objects.get(id=id))
        except MultiValueDictKeyError:
            pass

        # Check whether the field is empty 
        if "bid" in request.POST and request.POST["bid"]:
            if Decimal(request.POST["bid"]) <= Listing.objects.get(id=id).current_bid:
                return render(request, "auctions/listing.html",{
                    "item": Listing.objects.get(id=id)
                })
            else:
                # Change the current_bid in Listing 
                listing = Listing.objects.get(id=id)
                listing.current_bid = Decimal(request.POST["bid"])
                listing.save()
                # Create and save the bid in Bid
                bids = Bid.objects.create(listing=listing,bidder = request.user,bid =Decimal(request.POST["bid"]))
                bids.save()

        if "comment" in request.POST and request.POST["comment"]:
            # Save the comment in Comment
            comment= Comment.objects.create(listing=Listing.objects.get(id=id),user_comm = request.user,comment=request.POST["comment"])
            comment.save()
        if "watchlist" in request.POST and request.POST["watchlist"]:
            if request.POST["watchlist"] == "True":
                watch = Watchlist.objects.get(listing=Listing.objects.get(id=id))
                watch.state = True
                watch.save()
            else:
                watch = Watchlist.objects.get(listing=Listing.objects.get(id=id))
                watch.state = False
                watch.save()
                return redirect("listing", id=id)



    return render(request, "auctions/listing.html",{
        "item":  Listing.objects.get(id=id),
        "comments": Comment.objects.all(),
        "watchlists" : watchlist
    })

def create(request):
    if request.method == "POST":
        # Check whether the field is empty 
        if "title" in request.POST and request.POST["title"]:
            if "description" in request.POST and request.POST["description"]:
                if "bid" in request.POST and request.POST["bid"]:
                    if "category" in request.POST and request.POST["category"]:
                        if "image" in request.POST and request.POST["image"]:
                            # Create and save the listing in Listing
                            listing = Listing.objects.create(seller=request.user,title=request.POST["title"],description=request.POST["description"],current_bid=Decimal(request.POST["bid"]),image=request.POST["image"],category=request.POST["category"],active=True,winner=None)
                            listing.save()
                            Watchlist.objects.create(user = request.user,listing=Listing.objects.order_by('-id').first(),state=False).save()
                            return HttpResponseRedirect(reverse("index"))
    
    return render(request, "auctions/create.html")