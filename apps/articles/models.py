
from django import forms
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils import timezone

# Create your models here.
class ArticlePost(models.Model):
    author = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='标题', max_length=100)
    body = models.TextField(verbose_name='正文')
    created_time = models.DateTimeField(verbose_name='创建时间', default=timezone.now)
    updated_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        db_table = 'tb_articles'
        ordering = ('-created_time',)
        verbose_name = '文章'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class ArticlePostForm(forms.ModelForm):
    class Meta:
        model = ArticlePost
        fields = ('title', 'body')
