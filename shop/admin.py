from django.contrib import admin

# Register your models here.
from .models import Product,Registration,Contact
from .models import Orders,OrderUpdate

admin.site.register(Product),
admin.site.register(Registration)
admin.site.register(Contact),
admin.site.register(Orders),
admin.site.register(OrderUpdate),