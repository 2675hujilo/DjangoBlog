from Blog.models import SiteLink, SiteInfo, SiteMenu


class SiteInfoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        site_links = SiteLink.objects.filter(link_type='site')
        user_links = SiteLink.objects.filter(link_type='user')
        footer_links = SiteLink.objects.filter(link_type='footer')
        site_infos = SiteInfo.objects.all()
        site_menus = SiteMenu.objects.all()
        request.site_links = site_links
        request.user_links = user_links
        request.footer_links = footer_links
        request.site_infos = site_infos
        request.site_menus = site_menus
        response = self.get_response(request)
        return response
