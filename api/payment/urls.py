from django.urls import path
from . import views

urlpatterns = [
    path('pay/', views.PaymentListView.as_view(), name='pay'),
    path('create-rates/', views.CreatRechargePlanView.as_view(), name='create_recharge_plan'),
    path('rates/', views.ListRechargePlanView.as_view(), name='list_recharge_plans'),
    path('rates/<int:pk>/', views.DeleteUpdateRechargePlanView.as_view(), name='update_delete_rate'),
    path('branding-fee/', views.SetBrandingFeeView.as_view(), name='create_branding_fee'),
    path('branding-fee/<int:pk>/', views.EditBrandingFeeView.as_view(), name='edit_branding_fee')
]
