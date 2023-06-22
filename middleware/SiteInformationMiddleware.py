from Blog.models import SiteLink, SiteInformation, SiteMenu


class SiteInformationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        sitelinks = SiteLink.objects.all()  # 获取友情链接
        siteinfo = SiteInformation.objects.all()
        sitemenu = SiteMenu.objects.all()
        request.sitelinks = sitelinks  # 将友情链接数据存入 request 对象中
        request.siteinfos = siteinfo
        request.sitemenus = sitemenu
        response = self.get_response(request)
        return response
