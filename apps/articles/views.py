# Create your views here.
import markdown as markdown
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .models import ArticlePost, ArticlePostForm


def article_create(request):
    if request.method == 'POST':
        # 获取
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=1)
            new_article.save()
            return redirect("articles:article_list")
        else:
            return HttpResponse("表单内容有误，请重新填写")
    else:
        article_post_form = ArticlePostForm()
        content = {'article_post_form': article_post_form}
        return render(request, 'articles/create.html')


def article_list(request):
    content = {'articles': ArticlePost.objects.all()}
    return render(request, 'articles/list.html', content)


def article_delete(request, id):
    articel = ArticlePost.objects.get(id=id)
    articel.delete()
    return redirect("articles:article_list")


# 文章详情
def article_detail(request, id):
    # 取出相应的文章
    article = ArticlePost.objects.get(id=id)
    # 将markdown语法渲染成html样式
    article.body = markdown.markdown(article.body,
                                     extensions=[
                                         # 包含 缩写、表格等常用扩展
                                         'markdown.extensions.extra',
                                         # 语法高亮扩展
                                         'markdown.extensions.codehilite',
                                     ])

    # 需要传递给模板的对象
    context = {'article': article}
    # 载入模板，并返回context对象
    return render(request, 'articles/detail.html', context)
