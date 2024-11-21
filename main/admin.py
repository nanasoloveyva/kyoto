from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

from .models import Blogposts, Tag, Events, Comment

# Админка для событий
@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ('id', 'titles', 'events_date', 'events_time', 'events_type', 'is_active', 'attendeess_count')
    list_display_links = ('id', 'titles')
    search_fields = ('titles', 'descriptions')

# Админка для тегов
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

# Админка для блог-постов
@admin.register(Blogposts)
class BlogpostsAdmin(admin.ModelAdmin):
    list_display = ('id', 'titles', 'time_create', 'get_tags', 'photos', 'is_published')
    list_display_links = ('id', 'titles')
    search_fields = ('titles', 'contents')
    list_filter = ('tags',)

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Теги'

    
# Админка для комментариев
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'text', 'created_date', 'is_active', 'post_link')
    list_filter = ('is_active', 'created_date')
    search_fields = ('author__username', 'text')

    def post_link(self, obj):
        """Создание ссылки на пост"""
        url = reverse('post', kwargs={'post_slug': obj.post.slug})
        return format_html('<a href="{}" target="_blank">{}</a>', url, obj.post.titles)
    post_link.short_description = 'Ссылка на пост'

# Кастомная админка для пользователей
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'date_joined', 'is_staff')
    ordering = ('-date_joined',)

# Перерегистрация модели User с кастомным админ-классом
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)