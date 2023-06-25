from Blog.models import SiteLink, SiteInfo, SiteMenu, Category


class SiteInfoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 网站底部链接
        links = SiteLink.objects.all().order_by('link_order')
        request.site_links = links.filter(link_type='site')
        request.user_links = links.filter(link_type='user')
        request.footer_links = links.filter(link_type='footer')
        # 网站信息
        site_infos = SiteInfo.objects.filter(level=True)
        if site_infos:
            request.site_infos = site_infos[0]
        # 菜单
        site_menus = SiteMenu.objects.all()
        request.site_menus = site_menus
        # 分类
        site_categories = Category.objects.all()
        request.site_categories = site_categories

        response = self.get_response(request)
        return response
