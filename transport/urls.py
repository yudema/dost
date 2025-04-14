from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('transport/<int:transport_id>/', views.transport_detail, name='transport_detail'),
    path('transport/<int:transport_id>/update_status/', views.update_transport_status, name='update_transport_status'),
    path('support/', views.support_chat, name='support_chat'),
    path('support/admin/', views.support_admin, name='support_admin'),
    path('support/create_ticket/', views.create_ticket, name='create_ticket'),
    path('support/ticket/<int:ticket_id>/send_message/', views.send_message, name='send_message'),
    path('support/ticket/<int:ticket_id>/admin_send_message/', views.admin_send_message, name='admin_send_message'),
    path('support/ticket/<int:ticket_id>/messages/', views.get_ticket_messages, name='get_ticket_messages'),
    path('support/ticket/<int:ticket_id>/update_status/', views.update_ticket_status, name='update_ticket_status'),
] 