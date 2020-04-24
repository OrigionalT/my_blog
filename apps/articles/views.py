# Create your views here.
import markdown as markdown
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .models import ArticlePost, ArticlePostForm


@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """
    print(request.POST)

    article = ArticlePost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    if request.method == 'POST':
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            # 保存写入数据
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.save()
            return redirect("articles:article_detail", id=id)
        else:
            return HttpResponse("表单填写内容有误")
    else:
        article_post_form = ArticlePostForm()
        content = {'article': article, 'article_post_form': article_post_form}
        return render(request, 'articles/update.html', content)


@login_required(login_url='/userprofile/login/')
def article_create(request):
    if request.method == 'POST':
        # 获取
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)
            new_article.save()
            return redirect("articles:article_list")
        else:
            return HttpResponse("表单内容有误，请重新填写")
    else:
        article_post_form = ArticlePostForm()
        content = {'article_post_form': article_post_form}
        return render(request, 'articles/create.html')


def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    # 用户搜索逻辑
    if search:
        if order == 'total_views':
            # 用 Q对象 进行联合搜索
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            ).order_by('-total_views')
        else:
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            )
    else:
        # 将 search 参数重置为空
        search = ''
        if order == 'total_views':
            article_list = ArticlePost.objects.all().order_by('-total_views')
        else:
            article_list = ArticlePost.objects.all()

    paginator = Paginator(article_list, 3)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    # 增加 search 到 context
    context = {'articles': articles, 'order': order, 'search': search}

    return render(request, 'articles/list.html', context)


# def article_delete(request, id):
#     articel = ArticlePost.objects.get(id=id)
#     articel.delete()
#     return redirect("articles:article_list")
# 安全删除文章
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")


# 文章详情
def article_detail(request, id):
    # 取出相应的文章
    article = ArticlePost.objects.get(id=id)
    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])
    # 将markdown语法渲染成html样式
    # 修改 Markdown 语法渲染
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)

    # 需要传递给模板的对象
    content = {'article': article,'toc':md.toc}
    # 载入模板，并返回context对象
    return render(request, 'articles/detail.html', content)
