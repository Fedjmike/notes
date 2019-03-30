from django.contrib import admin

from .models import Tag, Note, Revision

admin.site.register(Tag)
admin.site.register(Note)
admin.site.register(Revision)