from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('lexi.apps.users.urls')),
    path('contracts/', include('lexi.apps.contracts.urls')),
    path('chatbot/', include('lexi.apps.chatbot.urls'))
    path('', include('lexi.apps.training.urls')),
    path('', include('lexi.apps.contract_analysis.urls')),
]
