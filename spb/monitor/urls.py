from django.urls import path
from monitor.views import OverView, PumpDetailsView, NewPumpView

urlpatterns = [
    path('overview/', OverView.as_view(), name='overview'),
    path('pumps/<int:pid>', PumpDetailsView.as_view(), name='pump_details'),
    path('pumps/new', NewPumpView.as_view(), name='pump_new'),

]
