import os
from rag_app.models import WritingStyleFile
from django.conf import settings

def sync_writing_style_folder():
    """
    Ensure every file in the writing_styles/ folder is referenced in the DB, and every DB entry has a file.
    """
    folder = os.path.join(settings.MEDIA_ROOT, 'writing_styles')
    if not os.path.exists(folder):
        return
    files_on_disk = set(os.listdir(folder))
    db_files = set(os.path.basename(obj.file.name) for obj in WritingStyleFile.objects.all())

    # Add DB entry for files on disk but not in DB
    for fname in files_on_disk - db_files:
        WritingStyleFile.objects.create(
            file=f'writing_styles/{fname}',
            original_name=fname
        )
    # Optionally, remove DB entries for missing files (not deleting DB, just for info)
    # for obj in WritingStyleFile.objects.all():
    #     if os.path.basename(obj.file.name) not in files_on_disk:
    #         obj.delete()

def delete_writing_style_file(file_id):
    obj = WritingStyleFile.objects.get(pk=file_id)
    obj.file.delete(save=False)
    obj.delete()
