from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail


def post_share(request, post_id):
    # выбираем пост с нужным id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # если метод запроса post, то работаем с введенными данными
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # поля формы прошли валидацию
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n"
            f"{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published',
                             publish__year=year, publish__month=month,
                             publish__day=day)
    # список комментариев для поста
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        # постим комментарий
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # создаем объект комментария, но пока не сохраняем в базу
            new_comment = comment_form.save(commit=False)
            # привязываем текущий пост к комментарию
            new_comment.post = post
            # сохраняем комментарий в базу данных
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post': post, 'comments':comments,
                                                     'new_comment': new_comment,
                                                     'comment_form':comment_form})
