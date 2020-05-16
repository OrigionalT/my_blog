from PIL import Image
from django import forms
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


# Create your models here.
class ArticleColumn(models.Model):
    """
    栏目的 Model
    """
    # 栏目标题
    title = models.CharField(max_length=100, blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class ArticlePost(models.Model):
    author = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='标题', max_length=100)
    # 文章标题图
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)
    # 文章标签
    tags = TaggableManager(blank=True)
    # 文章栏目的 “一对多” 外键
    column = models.ForeignKey(
        ArticleColumn,
        verbose_name='文章栏目',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )
    body = models.TextField(verbose_name='正文')
    likes = models.PositiveIntegerField(default=0)
    created_time = models.DateTimeField(verbose_name='创建时间', default=timezone.now)
    updated_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    total_views = models.PositiveIntegerField(verbose_name='游览次数', default=0)

    class Meta:
        db_table = 'tb_articles'
        ordering = ('-created_time',)
        verbose_name = '文章'
        verbose_name_plural = verbose_name

    def get_absolute_url(self):
        return reverse('articles:article_detail', args=[self.id])

    def __str__(self):
        return self.title

    # 保存时处理图片
    def save(self, *args, **kwargs):
        # 调用原有的 save() 的功能
        article = super(ArticlePost, self).save(*args, **kwargs)

        # 固定宽度缩放图片大小
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 400
            new_y = int(new_x * (y / x))
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)

        return article


class ArticlePostForm(forms.ModelForm):
    class Meta:
        model = ArticlePost
        fields = ('title', 'body', 'tags', 'avatar')
