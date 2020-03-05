from django.urls import path
from . import views

urlpatterns = [
    path('', views.MpesaCallbackView.as_view(), name='mpesa_callback_receiver'),
    path('recharge/', views.RechargeView.as_view(), name='recharge'),
    path('list/', views.PaymentListView.as_view(), name='list_payments'),
    path('recharge-plan/', views.CreateListRechargePlanView.as_view(), name='create_list_recharge_plan'),
]
