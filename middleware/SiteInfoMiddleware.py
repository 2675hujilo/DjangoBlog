from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache  # 导入缓存库

from Blog.models import SiteLink, SiteInfo, SiteMenu, Category


class SiteInfoMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)

    @staticmethod
    def process_request(request):
        cache_ttl = 60 * 30
        # 网站链接从缓存中获取，如果不存在则从数据库中查询，并设置到缓存中，过期时间为1小时
        request.site_links = cache.get('site_links')
        if not request.site_links:
            links = SiteLink.objects.all().order_by('link_order')
            request.site_links = links.filter(link_type='site')
            request.user_links = links.filter(link_type='user')
            request.footer_links = links.filter(link_type='footer')
            request.focus_links = links.filter(link_type='')
            request.slide_links = links.filter(link_type='slide')
            cache.set('site_links', (request.site_links, request.user_links, request.footer_links,
                                     request.focus_links, request.slide_links), timeout=cache_ttl)
        else:
            (request.site_links, request.user_links, request.footer_links,
             request.focus_links, request.slide_links) = request.site_links

        # 网站信息
        site_infos = cache.get('site_infos')
        if not site_infos:
            site_infos = SiteInfo.objects.filter(level=True)
            if site_infos:
                site_infos = site_infos[0]
                cache.set('site_infos', site_infos, timeout=cache_ttl)
        request.site_infos = site_infos

        # 菜单
        site_menus = cache.get('site_menus')
        print("11")
        if not site_menus:
            site_menus = SiteMenu.objects.all()
            root_menus = site_menus.filter(menu_root_id=True)
            for root_menu in root_menus:
                root_menu.children = site_menus.filter(menu_root_id=False, menus__in=[root_menu])
                print("root_menu:", root_menu, "root_menu.children:", root_menu.children)
            cache.set('site_menus', root_menus, timeout=3600)
        request.site_menus = site_menus

        # 分类
        site_categories = cache.get('site_categories')
        if not site_categories:
            site_categories = Category.objects.all()
            cache.set('site_categories', site_categories, timeout=cache_ttl)
        request.site_categories = site_categories
