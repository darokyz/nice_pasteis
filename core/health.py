from django.http import HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def healthcheck(request):
    """Endpoint sem dados, destinado exclusivamente ao monitoramento do Render."""
    return HttpResponse(status=204)
