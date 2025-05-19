# rag_app/views.py

import os
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import FolderSelectionForm
from .models import ReviewRun
from .utils.rag_pipeline import run_rag_litreview

def index(request):
    form = FolderSelectionForm()
    return render(request, "rag_app/index.html", {"form": form})

def generate_review(request):
    if request.method != "POST":
        return redirect(reverse("rag_app:index"))

    form = FolderSelectionForm(request.POST)
    if not form.is_valid():
        return render(request, "rag_app/index.html", {"form": form})

    folder_path = form.cleaned_data["folder_path"]
    # Create a ReviewRun entry
    run = ReviewRun.objects.create(folder_path=folder_path, status="RUNNING")
    try:
        # Invoke pipeline
        result = run_rag_litreview(folder_path)
        # Save results and mark completed
        run.result = result
        run.status = "COMPLETED"
        run.save()
        return redirect(reverse("rag_app:review_results", args=[run.id]))
    except Exception as e:
        # Mark as failed
        run.status = "FAILED"
        run.result = {"error": str(e)}
        run.save()
        return render(request, "rag_app/index.html", {
            "form": form,
            "error": "An error occurred while generating the review: " + str(e)
        })

def review_results(request, run_id):
    run = get_object_or_404(ReviewRun, pk=run_id)
    if run.status != "COMPLETED":
        return render(request, "rag_app/index.html", {
            "form": FolderSelectionForm(),
            "error": f"Review run is not completed (status: {run.status})."
        })
    result = run.result
    return render(request, "rag_app/review_results.html", {
        "result": result
    })
