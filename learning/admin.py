from django.contrib import admin
from .models import Area, Topico, Trilha, Passo, Questao, Alternativa, UserProgress

class TopicoInline(admin.TabularInline):
    model = Topico
    extra = 1
    ordering = ('order',)

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    inlines = [TopicoInline]

class TrilhaInline(admin.TabularInline):
    model = Trilha
    extra = 1
    ordering = ('order',)

@admin.register(Topico)
class TopicoAdmin(admin.ModelAdmin):
    list_display = ('title', 'area', 'order')
    list_filter = ('area',)
    inlines = [TrilhaInline]

class PassoInline(admin.TabularInline):
    model = Passo
    extra = 1
    ordering = ('order',)

@admin.register(Trilha)
class TrilhaAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'order')
    list_filter = ('topic__area', 'topic')
    inlines = [PassoInline]

class AlternativaInline(admin.TabularInline):
    model = Alternativa
    extra = 4

class QuestaoInline(admin.TabularInline):
    model = Questao
    extra = 1
    inlines = [AlternativaInline]

@admin.register(Passo)
class PassoAdmin(admin.ModelAdmin):
    list_display = ('title', 'track', 'content_type', 'order')
    list_filter = ('track__topic__area', 'track__topic', 'track', 'content_type')

    def get_inlines(self, request, obj=None):
        if obj and obj.content_type == 'quiz':
            return [QuestaoInline]
        return []

@admin.register(Questao)
class QuestaoAdmin(admin.ModelAdmin):
    list_display = ('text', 'step')
    inlines = [AlternativaInline]

@admin.register(Alternativa)
class AlternativaAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('question',)


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'step', 'status', 'completed_at', 'updated_at')
    list_filter = ('status', 'user', 'step__track__topic__area')
    search_fields = ('user__username', 'step__title')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    date_hierarchy = 'updated_at'
