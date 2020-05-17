# Create your views here.
import markdown as markdown
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, CreateView
from notifications.models import Notification

from apps.comment.forms import CommentForm
from apps.comment.models import Comment
from .models import ArticlePost, ArticlePostForm, ArticleColumn


# 更新文章
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """

    # 获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=id)

    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")

    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']

            if request.POST['column'] != 'none':
                # 保存文章栏目
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None

            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')

            article.tags.set(*request.POST.get('tags').split(','), clear=True)
            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("articles:article_detail", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()

        # 文章栏目
        columns = ArticleColumn.objects.all()
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的内容
        context = {
            'article': article,
            'article_post_form': article_post_form,
            'columns': columns,
            'tags': ','.join([x for x in article.tags.names()]),
        }

        # 将响应返回到模板中
        return render(request, 'articles/update.html', context)


@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定登录的用户为作者
            new_article.author = User.objects.get(id=request.user.id)
            if request.POST['column'] != 'none':
                # 保存文章栏目
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            # 将新文章保存到数据库中
            new_article.save()
            # 保存 tags 的多对多关系
            article_post_form.save_m2m()
            # 完成后返回到文章列表
            return redirect("articles:article_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 文章栏目
        columns = ArticleColumn.objects.all()
        # 赋值上下文
        context = {'article_post_form': article_post_form, 'columns': columns}
        # 返回模板
        return render(request, 'articles/create.html', context)


class ArticleListView(ListView):
    queryset = ArticlePost.objects.all()
    context_object_name = 'articles'
    template_name = 'articles/list.html'

    def get(self, request, *args, **kwargs):
        search = request.GET.get('search')
        order = request.GET.get('order')
        # 用户搜索逻辑
        if search:
            if order == 'total_views':
                # 用 Q对象 进行联合搜索
                article_list = self.queryset.filter(
                    Q(title__icontains=search) |
                    Q(body__icontains=search)
                ).order_by('-total_views')
            else:
                article_list = self.queryset.filter(
                    Q(title__icontains=search) |
                    Q(body__icontains=search)
                )
        else:
            # 将 search 参数重置为空
            search = ''
            if order == 'total_views':
                article_list = self.queryset.all().order_by('-total_views')
            else:
                article_list = self.queryset.all()

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
        Notification.objects.filter(target_object_id=id).delete()
        article.delete()
        return redirect("articles:article_list")
    else:
        return HttpResponse("仅允许post请求")


# 文章详情
def article_detail(request, id):
    # 取出相应的文章
    article = ArticlePost.objects.get(id=id)

    # 取出文章评论
    comments = Comment.objects.filter(article=id)

    # 引入评论表单
    comment_form = CommentForm()

    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])
    # 过滤出所有的id比当前文章小的文章
    pre_article = ArticlePost.objects.filter(id__lt=article.id).order_by('-id')
    # 过滤出id大的文章
    next_article = ArticlePost.objects.filter(id__gt=article.id).order_by('id')

    # 取出相邻前一篇文章
    if pre_article.count() > 0:
        pre_article = pre_article[0]
    else:
        pre_article = None

    # 取出相邻后一篇文章
    if next_article.count() > 0:
        next_article = next_article[0]
    else:
        next_article = None

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
    content = {'article': article, 'comment_form': comment_form, 'toc': md.toc, 'comments': comments, 'pre_article': pre_article,
        'next_article': next_article,}

    # 载入模板，并返回context对象
    return render(request, 'articles/detail.html', content)


# 点赞数 +1
class IncreaseLikesView(View):
    def post(self, request, *args, **kwargs):
        article = ArticlePost.objects.get(id=kwargs.get('id'))
        article.likes += 1
        article.save()
        return HttpResponse('success')
# class ArticleCreateView(CreateView):
#     model = ArticlePost
#     fields = '__all__'
#     template_name = 'articles/create.html'
