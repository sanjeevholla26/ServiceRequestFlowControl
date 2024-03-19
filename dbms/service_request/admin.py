from django.contrib import admin
from .models import Role, Assignment, Template, Approval, Fields, Request, Response, Requeststage, User
# Register your models here.

admin.site.register(Role)
admin.site.register(Assignment)
admin.site.register(Template)
admin.site.register(Approval)
admin.site.register(Fields)
admin.site.register(Request)
admin.site.register(Response)
admin.site.register(Requeststage)
admin.site.register(User)
