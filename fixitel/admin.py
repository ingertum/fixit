from django.contrib import admin
from .models import *


admin.site.register(Ticket)

admin.site.register(Status)

admin.site.register(Profile)

admin.site.register(Specialty)

admin.site.register(Log)

admin.site.register(Comment)

admin.site.register(TransactionTypes)

admin.site.register(Transaction)