from django.urls import path
from api.views import TimingsView, TimingAggregatorView, TransmittedTimingsView, ServiceTaskView, TokenView

urlpatterns = [
    path('pumps/<int:pid>/timings/transmitted', TransmittedTimingsView.as_view(), name='transmitted_timings'),
    path('pumps/<int:pid>/timings', TimingsView.as_view(), name='timings'),
    path('pumps/timings', TimingAggregatorView.as_view(), name='timings_aggregation'),
    path('service_tasks/<int:tid>', ServiceTaskView.as_view(), name='service_tasks'),
    path('token', TokenView.as_view(), name='token')
]
