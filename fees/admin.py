from django.contrib import admin

from .models import FeeAccount, FeePayment

admin.site.register(FeeAccount)
admin.site.register(FeePayment)
