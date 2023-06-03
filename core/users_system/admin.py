from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users_system.models import Usuario

@admin.register(Usuario)
class UserAdmin(BaseUserAdmin):
    pass
