from django.utils.deprecation import MiddlewareMixin

from Blog.models import SiteLink, SiteInfo, SiteMenu, Category


class SiteInfoMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)

    @staticmethod
    def process_request(request):
        # 网站链接
        links = SiteLink.objects.all().order_by('link_order')
        request.site_links = links.filter(link_type='site')
        request.user_links = links.filter(link_type='user')
        request.footer_links = links.filter(link_type='footer')
        request.focus_links = links.filter(link_type='')
        request.slide_links = links.filter(link_type='slide')
        # 网站信息
        site_infos = SiteInfo.objects.filter(level=True)
        if site_infos:
            request.site_infos = site_infos[0]
        # 菜单
        request.site_menus = SiteMenu.objects.all()
        # 分类
        request.site_categories = Category.objects.all()
