from django.contrib import admin
from .form import UserAdminCreationForm, UserAdminChangeForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


Users = get_user_model()


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('account', 'full_name', 'email', 'phone', 'is_superuser', 'is_active', 'created_date', 'updated_date',)
    list_filter = ('is_superuser', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('account', 'password',)}),
        ('Personal info', {'fields': ('full_name', 'email', 'phone', 'organization',)}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', 'is_active',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('account', 'full_name', 'email', 'phone', 'organization', 'password1', 'password2')}
        ),
    )
    search_fields = ('account', 'full_name', 'email',)
    ordering = ('created_date',)
    filter_horizontal = ()


# class UserAdmin(admin.ModelAdmin):
#     search_fields = ['username', 'full_name', 'email']
#     form = UserAdminChangeForm  # Update view
#     add_form = UserAdminCreationForm  # Create view

    # class Meta:
    #     model = Users

admin.site.register(Users, UserAdmin)

# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)
