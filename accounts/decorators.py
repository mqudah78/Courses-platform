from functools import wraps
from django.core.exceptions import PermissionDenied

def instructor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if (
            request.user.is_authenticated and
            request.user.profile.role in ['INSTRUCTOR', 'Admin']
        ):
            return view_func(request, *args, **kwargs)

        raise PermissionDenied  # 403 Forbidden
    return _wrapped_view
