# rag_app/models.py

from django.db import models
from django.contrib.postgres.fields import JSONField  # for Django >= 3.1 use models.JSONField

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
