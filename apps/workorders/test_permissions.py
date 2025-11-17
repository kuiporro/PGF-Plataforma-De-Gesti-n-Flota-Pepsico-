# tests/workorders/test_permissions.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User

@pytest.mark.django_db
def test_guard_cannot_close_ot(ot_factory):
    guard = User.objects.create_user(username="g", password="x", rol="GUARDIA")
    client = APIClient()
    token = client.post(reverse("token_obtain_pair"), {"username":"g","password":"x"}).data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    ot = ot_factory()  # crea una OT ABIERTA
    url = f"/api/work/ordenes/{ot.id}/cerrar/"
    r = client.post(url)
    assert r.status_code in (401,403)
