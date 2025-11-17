# apps/vehicles/urls.py

from rest_framework.routers import DefaultRouter
from apps.vehicles.views import VehiculoViewSet

router = DefaultRouter()
router.register(r'', VehiculoViewSet, basename='vehicles')   # /api/v1/vehicles/

urlpatterns = router.urls
# /api/v1/users/profiles/