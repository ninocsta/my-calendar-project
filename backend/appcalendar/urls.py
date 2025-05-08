from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfissionalViewSet, ServicoViewSet, 
    ClienteViewSet, CalendarSyncView, CalendarLoadView
)

router = DefaultRouter()
router.register(r'profissionais', ProfissionalViewSet)
router.register(r'servicos', ServicoViewSet)
router.register(r'clientes', ClienteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('calendar/load/', CalendarLoadView.as_view(), name='calendar-load'),
    path('calendar/sync/', CalendarSyncView.as_view(), name='calendar-sync'),
]
