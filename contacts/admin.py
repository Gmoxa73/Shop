
from django.contrib import admin
from .models import Address, Contact

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('city', 'street', 'house', 'building', 'apartment')
    list_filter = ('city',)
    search_fields = ('city', 'street', 'house')
    ordering = ('city', 'street')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'phone', 'address')
    list_filter = ('last_name',)
    search_fields = ('last_name', 'first_name', 'email', 'phone')
    fieldsets = (
        ('Персональные данные', {
            'fields': ('last_name', 'first_name', 'patronymic')
        }),
        ('Контакты', {
            'fields': ('email', 'phone')
        }),
        ('Адрес', {
            'fields': ('address',)
        }),
    )