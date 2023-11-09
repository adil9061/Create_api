from django.contrib import admin
from ap.models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Token)
admin.site.register(Live)
admin.site.register(Exam)