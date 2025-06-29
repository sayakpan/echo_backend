from django.contrib import admin
from tools.models.base import Tool
from tools.models.analyser import SchoolProfileScan
# from tools.models.meta import MetaTagScan
# from tools.models.schema import SchemaScan

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    search_fields = ('name', 'slug')
    list_filter = ('is_active',)
    
@admin.register(SchoolProfileScan)
class SchoolProfileScanAdmin(admin.ModelAdmin):
    list_display = ('slug', 'score', 'created_at')
    search_fields = ('slug',)
    ordering = ('-created_at',)

# @admin.register(MetaTagScan)
# class MetaTagScanAdmin(admin.ModelAdmin):
#     list_display = ('url', 'title', 'created_at')
#     search_fields = ('url', 'title')
#     ordering = ('-created_at',)

# @admin.register(SchemaScan)
# class SchemaScanAdmin(admin.ModelAdmin):
#     list_display = ('url', 'schema_type', 'created_at')
#     search_fields = ('url', 'schema_type')
#     ordering = ('-created_at',)
