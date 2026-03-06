import random

import markdown2
from django.shortcuts import redirect, render

from . import util


def index(request):
    return render(
        request,
        "encyclopedia/index.html",
        {"entries": util.list_entries()},
    )


def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(
            request,
            "encyclopedia/error.html",
            {"message": f'The requested page "{title}" was not found.'},
        )

    return render(
        request,
        "encyclopedia/entry.html",
        {
            "title": title,
            "content": markdown2.markdown(content),
        },
    )


def search(request):
    query = request.GET.get("q", "").strip()
    entries = util.list_entries()

    if not query:
        return render(
            request,
            "encyclopedia/search_results.html",
            {"query": query, "results": []},
        )

    for existing_title in entries:
        if existing_title.lower() == query.lower():
            return redirect("entry", title=existing_title)

    matches = [title for title in entries if query.lower() in title.lower()]
    return render(
        request,
        "encyclopedia/search_results.html",
        {"query": query, "results": matches},
    )


def new_page(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()

        if not title or not content:
            return render(
                request,
                "encyclopedia/error.html",
                {"message": "Title and content are required."},
            )

        existing_titles = util.list_entries()
        if any(existing.lower() == title.lower() for existing in existing_titles):
            return render(
                request,
                "encyclopedia/error.html",
                {"message": f'An entry named "{title}" already exists.'},
            )

        util.save_entry(title, content)
        return redirect("entry", title=title)

    return render(request, "encyclopedia/new.html")


def edit_page(request, title):
    current_content = util.get_entry(title)
    if current_content is None:
        return render(
            request,
            "encyclopedia/error.html",
            {"message": f'Cannot edit. The page "{title}" does not exist.'},
        )

    if request.method == "POST":
        updated_content = request.POST.get("content", "").strip()
        if not updated_content:
            return render(
                request,
                "encyclopedia/error.html",
                {"message": "Content cannot be empty."},
            )
        util.save_entry(title, updated_content)
        return redirect("entry", title=title)

    return render(
        request,
        "encyclopedia/edit.html",
        {"title": title, "content": current_content},
    )


def random_page(request):
    entries = util.list_entries()
    if not entries:
        return render(
            request,
            "encyclopedia/error.html",
            {"message": "No entries are available yet."},
        )

    return redirect("entry", title=random.choice(entries))
