from django.contrib import admin
from django.urls import path,include
from chatbot.views import chat, index,admin_dashboard,get_conversation,add_example

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('chat/', chat, name='chat'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('get_conversation/<int:conversation_id>/', get_conversation, name='get_conversation'),
    path('add_example/', add_example, name='add_example'),
    path('', index, name='index'),
    path('tinymce/', include('tinymce.urls')),
]