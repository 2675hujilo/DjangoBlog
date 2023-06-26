from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import SiteInfo, Category, SiteLink, SiteMenu, Post


@receiver([post_save, post_delete], sender=Category)
def clear_site_category_cache(sender, **kwargs):
    cache.delete("site_categories")


@receiver([post_save, post_delete], sender=SiteLink)
def clear_site_link_cache(sender, **kwargs):
    cache.delete("site_links")


@receiver([post_save, post_delete], sender=SiteMenu)
def clear_site_menu_cache(sender, **kwargs):
    cache.delete("site_menus")


@receiver([post_save, post_delete], sender=SiteInfo)
def clear_site_info_cache(sender, **kwargs):
    cache.delete("site_infos")


@receiver([post_save, post_delete], sender=Post)
def clear_post_cache(sender, **kwargs):
    cache.delete("all_posts")  # 清除所有帖子的缓存
    for pk in Category.objects.values_list('category_id', flat=True).distinct():
        cache.delete(f"posts_pk_{pk}")  # 清除特定分类文章的缓存
