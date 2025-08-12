
from django.db import models
from django.contrib.postgres.fields import JSONField

class WritingStyleFile(models.Model):
    file = models.FileField(upload_to='writing_styles/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    original_name = models.CharField(max_length=255)

    def __str__(self):
        return self.original_name

class AppSettings(models.Model):
    writing_style_description = models.TextField(blank=True, default="")
    research_question_chars = models.IntegerField(default=5000)
    methodology_chars = models.IntegerField(default=5000)
    findings_chars = models.IntegerField(default=5000)
    gaps_chars = models.IntegerField(default=5000)
    max_tokens_compose = models.IntegerField(default=1500)
    max_tokens_edit = models.IntegerField(default=1500)

    writing_style_text = models.TextField(blank=True, default="")

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce singleton
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class ReviewRun(models.Model):
    """
    Stores a single literature-review run:
    - folder_path: the path of PDFs ingested
    - started_at / finished_at: timestamps for the run
    - status: could be ‘PENDING’, ‘RUNNING’, ‘COMPLETED’, or ‘FAILED’
    - result: full JSON output from rag_pipeline.run_rag_litreview()
    """
    STATUS_CHOICES = [
        ('PENDING',   'Pending'),
        ('RUNNING',   'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED',    'Failed'),
    ]

    folder_path  = models.CharField(max_length=512)
    started_at   = models.DateTimeField(auto_now_add=True)
    name         = models.CharField(max_length=255, blank=True, default="")
    finished_at  = models.DateTimeField(null=True, blank=True)
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    result       = models.JSONField(null=True, blank=True)

    def display_name(self):
        if self.name:
            return self.name
        return f"Literature review n°{self.id}"
    def __str__(self):
        return f"ReviewRun {self.id} – {self.folder_path} [{self.status}]"
