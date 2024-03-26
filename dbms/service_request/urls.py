from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.user_login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_user, name="logout"),
    path("role/new", views.create_roles, name="create_role"),
    path("role/<int:id>/delete", views.delete_role, name="delete_role"),
    path("assign_role/", views.assign_roles, name="assign_role"),
    path("assignment/<int:id>/delete", views.delete_assignment, name="delete_assignment"),
    path("templates/", views.templates, name="templates"),
    path("template/<int:id>/delete", views.delete_template, name="delete_template"),
    path("template/<int:id>", views.template, name="template"),
    path("create_field/<int:id>", views.create_field, name="create_field"),
    path("create_approval/<int:id>", views.create_approval, name="create_approval"),
    path("create_request/<int:id>", views.create_request, name="create_request"),
    path("template_request/<int:id>", views.template_request, name="template_request"),
    path("approval_requests/", views.approval_requests, name="approval_requests"),
    path("approve_request/<int:id>", views.approve_request, name="approve_request"),
    path("requests/", views.get_all_requests, name="requests"),
    path("create_sendback/<int:id>", views.create_sendback, name="create_sendback"),
    path("sendbacks/<int:id>", views.all_sendbacks, name="sendbacks"),
    path("sendback_reponse/<int:id>", views.sendback_res, name="sendback_response"),
]
