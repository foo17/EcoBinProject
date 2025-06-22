from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(User)
admin.site.register(University)
admin.site.register(Organization)
admin.site.register(Incentive)
admin.site.register(CEApplication)
admin.site.register(Publication)
admin.site.register(Topic)
admin.site.register(Comment)
admin.site.register(Consultation)
admin.site.register(WasteCollectionBooking)
admin.site.register(MovementRecord)
admin.site.register(Appliance)
admin.site.register(Component)
admin.site.register(WasteCollectionSlot)
admin.site.register(ActivityRecord)
admin.site.register(Activity)