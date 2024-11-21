from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.contrib.auth.views import (
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from . import views
from .views import RegisterUser, LoginUser, logout_user, ProfileUser, delete_comment
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Основные страницы
    path('', views.index, name='home'),
    path('about-us/', views.about, name='about'),
    path('chai/', views.chai, name='chai'),

    # Аутентификация
    path('register/', RegisterUser.as_view(), name='register'),
    path('authentication/', LoginUser.as_view(), name='authentication'),
    path('logout/', logout_user, name='logout'),
    path('profile/', ProfileUser.as_view(), name='profile'),

    # Блог и посты
    path('blog/', views.blog, name='blog'),
    path('post/<slug:post_slug>/', views.show_post, name='post'),

    # Теги
    path('tag/<slug:tag_slug>/', views.tag_posts, name='tag_posts'),

    # Комментарии
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/like/', views.toggle_comment_like, name='toggle_comment_like'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/reply/', views.reply_to_comment, name='reply_to_comment'),

    # Управление паролем
    path('password-change/', 
        PasswordChangeView.as_view(template_name='main/password_change_form.html'),
        name='password_change'),
    path('password-change/done/',
        PasswordChangeDoneView.as_view(template_name='main/password_change_done.html'),
        name='password_change_done'),
    path('password-reset/',
        PasswordResetView.as_view(template_name="main/password_reset_form.html"),
        name='password_reset'),
    path('password-reset/done/',
        PasswordResetDoneView.as_view(template_name="main/password_reset_done.html"),
        name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(template_name="main/password_reset_confirm.html"),
        name='password_reset_confirm'),
    path('password-reset/complete/',
        PasswordResetCompleteView.as_view(template_name="main/password_reset_complete.html"),
        name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
