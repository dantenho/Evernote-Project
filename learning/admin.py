from django.contrib import admin
from .models import (
    Area,
    Topico,
    Trilha,
    Passo,
    Questao,
    Alternativa,
    UserProgress,
    UserProfile,
    Achievement,
    UserAchievement,
)

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


# ============================================================================
# Gamification Admin
# ============================================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for user profiles with gamification data."""

    list_display = ('user', 'xp_points', 'level', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('level', 'xp_for_current_level', 'xp_for_next_level', 'progress_to_next_level', 'created_at', 'updated_at')
    ordering = ('-xp_points',)

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Experience Points', {
            'fields': ('xp_points', 'level', 'xp_for_current_level', 'xp_for_next_level', 'progress_to_next_level')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """Admin interface for managing achievements."""

    list_display = ('icon', 'name', 'achievement_type', 'xp_reward', 'order')
    list_filter = ('achievement_type',)
    search_fields = ('name', 'description')
    ordering = ('order', 'name')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'icon', 'achievement_type', 'order')
        }),
        ('Rewards', {
            'fields': ('xp_reward',)
        }),
        ('Requirements', {
            'fields': ('related_track', 'related_area', 'required_value'),
            'description': 'Set specific requirements based on achievement type'
        }),
    )


class UserAchievementInline(admin.TabularInline):
    """Inline for viewing user achievements in profile admin."""

    model = UserAchievement
    extra = 0
    readonly_fields = ('achievement', 'earned_at', 'xp_awarded')
    can_delete = False


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    """Admin interface for user achievements."""

    list_display = ('user', 'achievement', 'earned_at', 'xp_awarded')
    list_filter = ('achievement__achievement_type', 'earned_at')
    search_fields = ('user__username', 'achievement__name')
    readonly_fields = ('earned_at',)
    date_hierarchy = 'earned_at'
    ordering = ('-earned_at',)
