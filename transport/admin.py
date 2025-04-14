from django.contrib import admin
from .models import Transport, Cargo, TransportStatus, SupportTicket, SupportMessage

@admin.register(Transport)
class TransportAdmin(admin.ModelAdmin):
    list_display = ('number', 'type', 'status', 'current_location', 'created_at')
    list_filter = ('status', 'type')
    search_fields = ('number', 'current_location')

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('transport', 'description', 'weight', 'volume', 'sender', 'receiver')
    list_filter = ('transport',)
    search_fields = ('description', 'sender', 'receiver')

@admin.register(TransportStatus)
class TransportStatusAdmin(admin.ModelAdmin):
    list_display = ('transport', 'status', 'location', 'timestamp')
    list_filter = ('status',)
    search_fields = ('transport__number', 'location')

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'email', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('subject', 'email')

@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'is_staff', 'message', 'created_at')
    list_filter = ('is_staff',)
    search_fields = ('message',)
