from .models import PropertyRequest
from .models import Property

def unread_requests(request):
    if request.user.is_authenticated:
        from .models import PropertyRequest
        unread_count = PropertyRequest.objects.filter(
            property__owner=request.user,
            is_read=False
        ).count()
        return {'unread_requests_count': unread_count}
    return {'unread_requests_count': 0}
