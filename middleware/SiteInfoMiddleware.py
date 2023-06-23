from django.db.models import Q

from Blog.models import SiteLink, SiteInfo, SiteMenu


class SiteInfoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        links = SiteLink.objects.all().order_by('link_order')
        site_infos = SiteInfo.objects.all()
        site_menus = SiteMenu.objects.all()
        request.site_links = links.filter(link_type='site')
        request.user_links = links.filter(link_type='user')
        request.footer_links = links.filter(link_type='footer')
        request.site_infos = site_infos
        request.site_menus = site_menus
        response = self.get_response(request)
        return response
