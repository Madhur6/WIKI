from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect,HttpResponseBadRequest
from django.urls import reverse
from django import forms

from . import util

from markdown2 import Markdown

import random

class NewForm(forms.Form):
    title = forms.CharField(label="title:", max_length=30, widget=forms.TextInput(attrs={'autofocus':'autofocus', 'autocomplete':'off'}))
    content = forms.CharField(label="Your content:", widget=forms.Textarea(attrs={'rows':4,'cols':30, 'class':'textarea', 'style': 'height: 50vh; width: 60%;'}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def title(request, TITLE):
    title = util.get_entry(TITLE)

    if title is None:
        return render(request, "encyclopedia/error.html", {
            "message": "request not found!!"
        })

    return render(request, "encyclopedia/title.html", {
        "title":TITLE,
        "content": markdown(title)
    })

def search(request):
    if request.method == "POST":
        title = request.POST["q"]

        entry = util.get_entry(title)

        if entry is not None:
            return render(request, "encyclopedia/title.html", {
                "title": title,
                "content": markdown(entry)
            })
        elif entry is None:
            entries = util.list_entries()
            search_result = []

            for entry in entries:
                if title.lower() in entry.lower():
                    search_result.append(entry)
            if not search_result:
                return render(request, "encyclopedia/error.html", {
                    "message": "request not found!!"
                })
            else:
                return render(request, "encyclopedia/index.html", {
                    "entries": search_result
                })

def new_page(request):

    if request.method == "GET":
        return render(request, "encyclopedia/new_page.html", {
            "forms": NewForm
        })
    
    elif request.method == "POST":
        form = NewForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            titles = util.list_entries()

            for title1 in titles:
                if title1.lower() == title.lower():
                    return render(request, "encyclopedia/error.html", {
                        "message": "title already exists!!"
                    })
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("title", args=(title,)))
        else:
            return render(request, "encyclopedia/new_page.html", {
                "forms": NewForm()
            })
        

def edit_page(request, TITLE):
    if request.method == "GET":
        title = util.get_entry(TITLE)

        #pre-populated the form
        form = NewForm(initial={'title': TITLE, 'content': title})

        return render(request, "encyclopedia/edit.html", {
            "title": TITLE,
            "forms": form
        })
    
    else:
        form = NewForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("title", args=(title,)))
        
        
def random_choice(request):
    titles = util.list_entries()

    random_title = random.choice(titles)

    return redirect("title", TITLE=random_title)


def markdown(content):
    markdowner = Markdown()

    return markdowner.convert(content)