from django.db import models
from django.contrib.auth.models import User

# class Event(models.Model):
#     title = models.CharField('Название мероприятия', max_length=200)  # название мероприятия
#     event_date = models.DateField('Дата мероприятия')  # дата мероприятия
#     event_time = models.TimeField('Время мероприятия')  # время мероприятия
#     event_type = models.CharField('Тип мероприятия', max_length=120)
#     description = models.TextField('Описание мероприятия')  # описание мероприятия
#     attendees_count = models.PositiveIntegerField('Количество присутствующих', default=0)
#     attendees = models.ManyToManyField(User, related_name='events', blank=True)  # участники мероприятия
#     is_active = models.BooleanField('Активность мероприятия', default=True) 

#     def __str__(self):
#         return f"{self.event_date}: '{self.title}' ({self.event_type}) - [{self.description}]"
    
#     class Meta:
#         verbose_name = 'Мероприятие'
#         verbose_name_plural = 'Мероприятия'
    

# class Blogpost(models.Model):
#     title = models.CharField('Название поста', max_length=200)
#     photo = models.ImageField('Фото', upload_to='blog_photos/')
#     content = models.TextField('Содержание поста')
#     time_create = models.DateTimeField(auto_now_add=True)
#     is_published = models.BooleanField('Опубликовано', default=True)


#     def __str__(self):
#         return f"{self.time_create}: '{self.title}' - [{self.content}]"

#     class Meta:
#         verbose_name = 'Пост'
#         verbose_name_plural = 'Посты'


class Events(models.Model):
    titles = models.CharField('Название мероприятия', max_length=200)  # название мероприятия
    events_date = models.DateField('Дата мероприятия')  # дата мероприятия
    events_time = models.TimeField('Время мероприятия')  # время мероприятия
    events_type = models.CharField('Тип мероприятия', max_length=120)
    descriptions = models.TextField('Описание мероприятия')  # описание мероприятия
    attendeess_count = models.PositiveIntegerField('Количество присутствующих', default=0)
    attendeess = models.ManyToManyField(User, related_name='events_attendees', blank=True)
    is_active = models.BooleanField('Активность мероприятия', default=True) 

    def __str__(self):
        return f"{self.events_date}: '{self.titles}' ({self.events_type}) - [{self.descriptions}]"
    
    class Meta:
        verbose_name = 'Мероприятие KYOTOCHAI'
        verbose_name_plural = 'Мероприятия KYOTOCHAI'
    

class Blogposts(models.Model):
    titles = models.CharField('Название поста', max_length=200)
    photos = models.ImageField('Фото', upload_to='blog_photos/')
    contents = models.TextField('Содержание поста')
    time_create = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField('Опубликовано', default=True)
    slug = models.SlugField(unique=True, null=True)
    tags = models.ManyToManyField('Tag', related_name='posts')

    def __str__(self):
        return f"{self.time_create}: '{self.titles}'"

    class Meta:
        verbose_name = 'Пост KYOTOCHAI'
        verbose_name_plural = 'Посты KYOTOCHAI'
        ordering = ['-time_create']

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('posts', kwargs={'post': self.slug})


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Comment(models.Model):
    post = models.ForeignKey(Blogposts, on_delete=models.CASCADE, related_name='comments', verbose_name='Пост')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    text = models.TextField('Текст комментария')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_active = models.BooleanField('Активный', default=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_date']

    def __str__(self):
        return f'Комментарий от {self.author} к {self.post.titles}'
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.CharField(max_length=200, default='main/images/default.png')

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')