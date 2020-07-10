from django.shortcuts import render, redirect
from django.http import HttpResponse

from . import util
from random import choice


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def get_title(request, title):
	entry = util.get_entry(title)
	if entry is None:
		return HttpResponse("<h1>Error: Requested Page Not Found!<h1>")
	args = {'title': title}
	args.update({'entry': entry})
	return render(request, "encyclopedia/entry.html", args)

def search(request):
	query = request.GET.get('q')
	all_entries = [entry for entry in util.list_entries()]

	if query in all_entries:
		return redirect('title', query)

	alt = [entry for entry in all_entries if query in entry]
	return render(request, "encyclopedia/search_results.html", {'entries': alt})

def create(request):
	if request.method == "GET":
		return render(request, "encyclopedia/create.html")
	else:
		title = request.POST.get('title')
		content = request.POST.get('content')
		all_entries = util.list_entries()

		if title in all_entries:
			return HttpResponse("<h1>Error: Page Already Exists!<h1>")
		else:
			util.save_entry(title, content)
			return redirect('title', title)

def edit(request, title):
	print(title)
	return HttpResponse("Under Development")

def random(request):
	return redirect('title', choice(util.list_entries()))