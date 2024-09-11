from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from blog import constants


User = get_user_model()


class CreatedAt(models.Model):
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ('created_at', )


class IsPublishedCreatedAtModel(CreatedAt):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True


class Location(IsPublishedCreatedAtModel):
    name = models.CharField(
        'Название места',
        max_length=constants.MAX_FIELD_LENGTH,
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name[:constants.REPRESENTATION_LENGTH]


class Category(IsPublishedCreatedAtModel):
    title = models.CharField(
        'Заголовок',
        max_length=constants.MAX_FIELD_LENGTH,
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        'Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; разрешены символы '
            'латиницы, цифры, дефис и подчёркивание.'
        ),
        unique=True
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title[:constants.REPRESENTATION_LENGTH]


class Post(IsPublishedCreatedAtModel):
    title = models.CharField(
        'Заголовок',
        max_length=constants.MAX_FIELD_LENGTH,
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — можно делать '
            'отложенные публикации.'
        )
    )
    image = models.ImageField(
        verbose_name='Картинка у публикации',
        blank=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )

    class Meta:
        default_related_name = 'posts'
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.title[:constants.REPRESENTATION_LENGTH]

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=(self.id))


class Comment(CreatedAt):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментируемый пост',
    )
    text = models.TextField(verbose_name='Текст комментария')

    class Meta(CreatedAt.Meta):
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:constants.COMMENT_LENGTH]
