from django.urls import path

from . import views

app_name = "policies"

urlpatterns = [
    path("", views.policy_list, name="policy_list"),
    path("new/", views.policy_create, name="policy_create"),
    path("<int:pk>/", views.policy_detail, name="policy_detail"),
    path("<int:pk>/edit/", views.policy_edit, name="policy_edit"),
    path("policy-types/quick-add/", views.policy_type_quick_add, name="policy_type_quick_add"),
]
