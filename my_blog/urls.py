"""my_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import notifications.urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from apps.articles import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('articles/', include('apps.articles.urls', namespace='articles')),
    path('userprofile/', include('apps.userprofile.urls', namespace='userprofile')),
    path('password-reset', include('password_reset.urls')),
    path('comment/', include('apps.comment.urls', namespace='comment')),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path('notice/', include('apps.notice.urls', namespace='notice')),
    path('accounts/', include('allauth.urls')),
    # home
    path('', views.ArticleListView.as_view(), name='home'),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
