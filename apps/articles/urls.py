from django.urls import path, re_path

from . import views

app_name = 'articles'

urlpatterns = [

    re_path(r'^articlelist/$', views.article_list, name='article_list'),
    path('articledetail/<int:id>/', views.article_detail, name='article_detail'),
    path('articledelete/<int:id>/', views.article_delete, name='article_delete'),
]
