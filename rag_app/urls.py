from django.urls import path
from . import views

app_name = "rag_app"

urlpatterns = [
path('', views.index, name='index'),
path('generate/', views.generate_review, name='generate_review'),
path('results/int:run_id/', views.review_results, name='review_results'),
]