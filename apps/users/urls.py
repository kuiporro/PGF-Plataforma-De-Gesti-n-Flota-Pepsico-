# apps/users/urls.py

from rest_framework.routers import DefaultRouter
from apps.users.views import UserViewSet, ProfileViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='users')         # /api/v1/users/
router.register(r'profiles', ProfileViewSet, basename='profiles')

urlpatterns = router.urls
# /api/v1/users/profiles/