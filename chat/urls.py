from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('chat/<int:chat_id>/', views.chat_view, name='chat_detail'),
    path('new-chat/', views.new_chat, name='new_chat'),
    path('delete-chat/<int:chat_id>/', views.delete_chat, name='delete_chat'),
]
