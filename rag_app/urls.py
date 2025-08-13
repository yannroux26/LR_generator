from django.urls import path
from . import views

app_name = "rag_app"

urlpatterns = [
	path('', views.index, name='index'),
	path('generate/', views.generate_review, name='generate_review'),
	path('results/<int:run_id>/', views.review_results, name='review_results'),
	path('settings/', views.settings_view, name='settings'),
	path('delete-writing-file/<int:file_id>/', views.delete_writing_file, name='delete_writing_file'),
	path('rename/<int:run_id>/', views.rename_review, name='rename_review'),
	path('delete/<int:run_id>/', views.delete_review, name='delete_review'),
    path('analyse-writing-style/', views.analyse_writing_style, name='analyse_writing_style'),
]