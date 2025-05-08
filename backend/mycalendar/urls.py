from django.contrib import admin
from django.urls import path
from appcalendar.views import CalendarLoadView, CalendarSyncView, ProfissionalListView, ServicoListView, ClienteListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/calendar/load/', CalendarLoadView.as_view(), name='calendar-load'),
    path('api/calendar/sync/', CalendarSyncView.as_view(), name='calendar-sync'),
    path('api/profissionais/', ProfissionalListView.as_view(), name='profissional-list'),
    path('api/servicos/', ServicoListView.as_view(), name='servico-list'),
    path('api/clientes/', ClienteListView.as_view(), name='cliente-list'),
]