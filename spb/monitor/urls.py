from django.urls import path
from monitor.views import OverView, PumpDetailsView, NewPumpView, LoginView, LogoutView

urlpatterns = [
    path('overview', OverView.as_view(), name='overview'),
    path('pumps/<int:pid>', PumpDetailsView.as_view(), name='pump_details'),
    path('pumps/new', NewPumpView.as_view(), name='pump_new'),
    path('login', LoginView.as_view(), name='login'),  # URL for the login page
    path('logout', LogoutView.as_view(), name='logout'),  # URL for the logout procedure
]
