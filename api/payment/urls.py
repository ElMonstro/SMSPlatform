from django.urls import path
from . import views

urlpatterns = [
    path('', views.MpesaCallbackView.as_view(), name='mpesa_callback_receiver'),
    path('pay/', views.MpesaPayView.as_view(), name='pay'),
    path('list/', views.PaymentListView.as_view(), name='list_payments'),
    path('recharge-plan/', views.CreateListRechargePlanView.as_view(), name='create_list_recharge_plan'),
    path('branding-fee/', views.SetBrandingFeeView.as_view(), name='create_branding_fee'),
    path('branding-fee/<int:pk>/', views.EditBrandingFeeView.as_view(), name='edit_branding_fee'),
]
