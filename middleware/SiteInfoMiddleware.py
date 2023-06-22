from Blog.models import SiteLink, SiteInformation, SiteMenu


class SiteInfoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        sitelinks = SiteLink.objects.all()
        siteinfos = SiteInformation.objects.all()
        sitemenus = SiteMenu.objects.all()
        request.sitelinks = sitelinks
        request.siteinfos = siteinfos
        request.sitemenus = sitemenus
        response = self.get_response(request)
        return response
