from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView

from .utils import DataMixin
from .forms import RegisterUserForm, ProfileUsersForm, CommentForm, UserUpdateForm
from .models import Events, Blogposts, Comment, Tag, User, Profile, CommentLike
import json

# Основные представления
def index(request):
    latest_posts = Blogposts.objects.order_by('-time_create')[:3]
    return render(request, 'main/index.html', {'latest_posts': latest_posts})

def about(request):
    return render(request, 'main/about.html')

def login(request):
    return render(request, 'main/login.html')

def chai(request):
    return render(request, 'main/chai.html')

# Представления блога
def blog(request):
    selected_tags = request.GET.getlist('tags')
    tags = Tag.objects.all()
    
    if selected_tags:
        posts = (Blogposts.objects
                .prefetch_related('tags', 'comments')
                .filter(tags__slug__in=selected_tags)
                .distinct())
    else:
        posts = Blogposts.objects.prefetch_related('tags', 'comments').all()
    
    return render(request, 'main/blog.html', {
        'posts': posts,
        'tags': tags,
        'selected_tags': selected_tags
    })

def categories(request, post):
    posts = Blogposts.objects.filter(slug=post)
    return render(request, 'main/blog.html', {'posts': posts})

def tag_posts(request, tag_slug):
    selected_tags = request.GET.getlist('tags')
    if tag_slug not in selected_tags:
        selected_tags.append(tag_slug)
    
    posts = Blogposts.objects.filter(tags__slug__in=selected_tags).distinct()
    tags = Tag.objects.all()
    
    return render(request, 'main/blog.html', {
        'posts': posts,
        'tags': tags,
        'selected_tags': selected_tags
    })

# Представления постов и комментариев
def post(request, pk):
    post = get_object_or_404(Blogposts, pk=pk)
    comments = Comment.objects.filter(post=post).order_by('-created_date')
    
    if request.method == 'POST' and request.user.is_authenticated:
        comment_text = request.POST.get('text')
        if comment_text:
            Comment.objects.create(
                post=post,
                author=request.user,
                text=comment_text
            )
    
    return render(request, 'main/post.html', {
        'post': post,
        'comments': comments,
    })

def show_post(request, post_slug):
    post = get_object_or_404(Blogposts, slug=post_slug)
    comments = post.comments.filter(is_active=True).prefetch_related('likes')
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post', post_slug=post_slug)
    else:
        comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'tags': post.tags.all(),
        'title': post.titles,
        'user_likes': Comment.objects.filter(likes__user=request.user) if request.user.is_authenticated else []
    }
    
    return render(request, 'main/post.html', context)

# Классы аутентификации
class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'main/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Регистрация")
        return dict(list(context.items()) + list(c_def.items()))

class LoginUser(DataMixin, LoginView):
    form_class = AuthenticationForm
    template_name = 'main/authentication.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Авторизация")
        return dict(list(context.items()) + list(c_def.items()))
    
    def get_success_url(self):
        return reverse_lazy('home')

def logout_user(request):
    logout(request)
    return redirect('authentication')

# Профиль пользователя
class ProfileUser(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUsersForm
    template_name = 'main/profile.html'
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        selected_avatar = self.request.POST.get('selected_avatar')
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        if selected_avatar:
            profile.avatar = selected_avatar
            profile.save()
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Профиль пользователя'
        try:
            context['current_avatar'] = self.request.user.profile.avatar
        except Profile.DoesNotExist:
            context['current_avatar'] = None
        return context
    
    def get_success_url(self):
        return reverse_lazy('profile')

# Управление комментариями
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post = comment.post
    
    if request.user == comment.author or request.user.is_superuser:
        comment.delete()
        return redirect('post', post_slug=post.slug)
    return HttpResponseForbidden("У вас нет прав для удаления этого комментария")

def toggle_comment_like(request, comment_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    comment = get_object_or_404(Comment, id=comment_id)
    like, created = CommentLike.objects.get_or_create(
        comment=comment,
        user=request.user
    )
    
    if not created:
        like.delete()
        is_liked = False
    else:
        is_liked = True
    
    return JsonResponse({
        'is_liked': is_liked,
        'likes_count': comment.likes.count()
    })

@login_required
def edit_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user != comment.author:
            return JsonResponse({'success': False, 'error': 'Нет прав доступа'}, status=403)
            
        data = json.loads(request.body)
        comment.text = data['text']
        comment.save()
        return JsonResponse({'success': True})
    
@login_required
def reply_to_comment(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    post = parent_comment.post
    
    if request.method == 'POST':
        data = json.loads(request.body)
        reply_text = data.get('text')
        
        if reply_text:
            new_reply = Comment.objects.create(
                post=post,
                author=request.user,
                text=reply_text,
                parent=parent_comment
            )
            
            return JsonResponse({
                'success': True,
                'author': new_reply.author.username,
                'author_avatar': str(new_reply.author.profile.avatar) if new_reply.author.profile.avatar else None,
                'text': new_reply.text,
                'created_date': new_reply.created_date.strftime('%d.%m.%Y %H:%M'),
                'comment_id': new_reply.id
            })
    
    return JsonResponse({'success': False})