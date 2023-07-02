from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import SiteInfo, Category, SiteLink, SiteMenu, Post, PostInfo, Comment


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
def clear_post_cache(sender, instance, created, **kwargs):
    if created:
        post_info = PostInfo(post_id=instance.post_id, post_title=instance.title)
        post_info.save()
    cache.delete("all_posts")  # 清除所有帖子的缓存
    for name in Category.objects.values_list('name', flat=True).distinct():
        # flat=True:结果以单个值的方式返回，而不是以元组或列表的形式。
        cache.delete(f"posts_category_name_{name}")  # 清除特定分类文章的缓存
    for title in Post.objects.values_list('title', flat=True).distinct():  # 清除特定文章的缓存
        cache.delete(f"posts_title_{title}")


@receiver([post_save, post_delete], sender=Comment)
def clear_post_name(sender, **kwargs):
    for title in Post.objects.values_list('title', flat=True).distinct():
        cache.delete(f"posts_comment_{title}")


@receiver([post_save, post_delete], sender=SiteMenu)
def clear_site_menu_cache(sender, **kwargs):
    cache.delete("site_menus")
