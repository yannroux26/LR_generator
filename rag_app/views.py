from django.views.decorators.csrf import csrf_exempt
from .models import AppSettings

def settings_view(request):
    settings = AppSettings.get_solo()
    if request.method == "POST":
        settings.research_question_chars = int(request.POST.get("research_question", 5000))
        settings.methodology_chars = int(request.POST.get("methodology", 5000))
        settings.findings_chars = int(request.POST.get("findings", 5000))
        settings.gaps_chars = int(request.POST.get("gaps", 5000))
        settings.max_tokens_compose = int(request.POST.get("max_tokens_compose", 1500))
        settings.max_tokens_edit = int(request.POST.get("max_tokens_edit", 1500))
        settings.save()
        saved = True
    else:
        saved = False
    nbchar = {
        "research_question": settings.research_question_chars,
        "methodology": settings.methodology_chars,
        "findings": settings.findings_chars,
        "gaps": settings.gaps_chars
    }
    return render(request, "rag_app/settings.html", {
        "nbchar": nbchar,
        "max_tokens_compose": settings.max_tokens_compose,
        "max_tokens_edit": settings.max_tokens_edit,
        "saved": saved
    })
import os
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import FolderSelectionForm
from .models import ReviewRun
from .utils.rag_pipeline import run_rag_litreview
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect

def index(request):
    form = FolderSelectionForm()
    reviews = ReviewRun.objects.all().order_by('-id')
    return render(request, "rag_app/index.html", {"form": form, "reviews": reviews})

@require_POST
def rename_review(request, run_id):
    run = get_object_or_404(ReviewRun, pk=run_id)
    new_name = request.POST.get("new_name", "").strip()
    if new_name:
        run.name = new_name
        run.save()
    return redirect(reverse("rag_app:index"))

@require_POST
def delete_review(request, run_id):
    run = get_object_or_404(ReviewRun, pk=run_id)
    run.delete()
    return redirect(reverse("rag_app:index"))

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
    # If ?download=1, return plain text for download
    if request.GET.get("download") == "1":
        from django.http import HttpResponse
        review_text = result.get("final_review", "")
        return HttpResponse(review_text, content_type="text/plain; charset=utf-8")
    return render(request, "rag_app/review_results.html", {
        "result": result
    })
