from .models import Tenant
from django.http import Http404

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = None
        path_parts = request.path_info.split('/')

        # Expected URL: /t/<tenant_slug>/...
        # path_parts will be ['', 't', <tenant_slug>, ...]
        if len(path_parts) > 2 and path_parts[1] == 't':
            tenant_slug = path_parts[2]
            try:
                request.tenant = Tenant.objects.get(slug=tenant_slug)
            except Tenant.DoesNotExist:
                # Optionally, you could raise Http404 or handle differently
                # For now, request.tenant remains None as per instructions
                pass
        
        response = self.get_response(request)
        return response
