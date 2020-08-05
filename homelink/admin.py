from django.contrib import admin
from homelink.models import HouseInfo
# Register your models here.

class HouseInfoAdmin(admin.ModelAdmin):
    list_display = ('title','house','location','bedroom','total_price')
    search_fields = ('house','total_price','bedroom')
    ordering = ("location",)


admin.site.register(HouseInfo,HouseInfoAdmin)
