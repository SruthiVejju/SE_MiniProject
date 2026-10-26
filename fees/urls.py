from django.urls import path

from . import views

urlpatterns = [
    path('payments/new/', views.record, name='fee-record'),
    path('receipts/<int:pk>/', views.receipt, name='fee-receipt'),
]
