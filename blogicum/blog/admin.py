from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    search_fields = ('text',)
    list_display = (
        'id',
        'title',
        'author',
        'text',
        'category',
        'pub_date',
        'location',
        'is_published',
        'created_at',
    )
    list_display_links = ('title',)
    list_editable = (
        'category',
        'is_published',
        'location'
    )
    list_filter = ('created_at',)
    empty_value_display = '-пусто-'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = (
        'id',
        'title',
        'is_published',
        'created_at',
        'description',
    )
    list_display_links = ('title',)
    list_editable = ('is_published',)
    list_filter = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = (
        'id',
        'name',
        'is_published',
        'created_at',
    )
    list_display_links = ('name',)
    list_filter = ('name',)
