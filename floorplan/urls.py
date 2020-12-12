from django.urls import *
from .views import *
from django.conf.urls import url
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static


urlpatterns = [
    path('', plan_list, name='plan_list_url'),
    path('plans/create', PlanCreate.as_view(), name = 'plan_create_url'),
    path('plans/<str:slug>/', PlanDetail.as_view(), name = 'plan_detail_url'),
    # path('media/images'/ ', )
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
