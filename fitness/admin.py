from django.contrib import admin
from django.contrib.auth.models import Group

from .models import (
    User, Trainer, FitnessClass,
    TariffType, Membership, ClassBooking,
    Role, FavoriteClass,
)

admin.site.unregister(Group)
admin.site.register(Role)


class MembershipInline(admin.TabularInline):
    model = Membership
    fk_name = 'user'
    extra = 0
    exclude = ('updated_by',)
    readonly_fields = ('created_at', 'updated_at')


class ClassBookingInline(admin.TabularInline):
    model = ClassBooking
    fk_name = 'user'
    extra = 0
    exclude = ('updated_by',)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('fitness_class',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'role', 'is_blocked', 'birth_date', 'get_memberships_count')
    list_display_links = ('full_name', 'email')
    list_filter = ('role', 'is_blocked', 'birth_date', 'created_at')
    search_fields = ('full_name', 'email', 'phone')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MembershipInline, ClassBookingInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name', 'email', 'phone', 'role', 'is_blocked')
        }),
        ('Дополнительно', {
            'fields': ('birth_date', 'password_hash')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_memberships_count(self, obj):
        return obj.memberships.count()
    get_memberships_count.short_description = 'Количество абонементов'


class TrainerClassInline(admin.TabularInline):
    model = FitnessClass
    extra = 0
    fields = ('name', 'description', 'capacity')
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('image', 'created_by', 'updated_by')


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('get_user_name', 'specialization', 'get_classes_count')
    list_display_links = ('get_user_name',)
    list_filter = ('specialization', 'created_at')
    search_fields = ('user__full_name', 'specialization')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'created_by')
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('bio', 'photo', 'updated_by')
    inlines = [TrainerClassInline]

    def get_user_name(self, obj):
        return obj.user.full_name
    get_user_name.short_description = 'Тренер'

    def get_classes_count(self, obj):
        return obj.fitnessclass_set.count()
    get_classes_count.short_description = 'Количество занятий'

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = obj.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, FitnessClass):
                instance.trainer = form.instance
            instance.save()
        formset.save_m2m()
        for obj in formset.deleted_objects:
            obj.delete()


class ClassBookingInlineForClass(admin.TabularInline):
    model = ClassBooking
    extra = 0
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('updated_by',)


@admin.register(FitnessClass)
class FitnessClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_trainer_name', 'capacity', 'get_bookings_count')
    list_display_links = ('name',)
    list_filter = ('trainer', 'created_at')
    search_fields = ('name', 'description', 'trainer__user__full_name')
    date_hierarchy = 'created_at'
    raw_id_fields = ('created_by',)
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('image', 'updated_by')
    inlines = [ClassBookingInlineForClass]
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'trainer', 'capacity')
        }),
        ('Системная информация', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_trainer_name(self, obj):
        return obj.trainer.user.full_name if obj.trainer and obj.trainer.user else '-'
    get_trainer_name.short_description = 'Тренер'

    def get_bookings_count(self, obj):
        return obj.classbooking_set.count()
    get_bookings_count.short_description = 'Записей'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'trainer':
            kwargs['queryset'] = Trainer.objects.select_related('user').all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id and obj.trainer_id:
            obj.created_by = obj.trainer.user
        if not obj.capacity:
            obj.capacity = 20
        super().save_model(request, obj, form, change)


@admin.register(TariffType)
class TariffTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_days', 'price', 'is_active')
    list_display_links = ('name',)
    list_filter = ('is_active', 'duration_days')
    search_fields = ('name',)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('get_user_name', 'tariff_type', 'start_date', 'end_date', 'status')
    list_display_links = ('get_user_name',)
    list_filter = ('status', 'tariff_type', 'start_date', 'end_date')
    search_fields = ('user__full_name',)
    date_hierarchy = 'start_date'
    raw_id_fields = ('user', 'created_by')
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('updated_by',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'tariff_type', 'status')
        }),
        ('Период действия', {
            'fields': ('start_date', 'end_date')
        }),
        ('Системная информация', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_user_name(self, obj):
        return obj.user.full_name
    get_user_name.short_description = 'Пользователь'


@admin.register(ClassBooking)
class ClassBookingAdmin(admin.ModelAdmin):
    list_display = ('get_user_name', 'get_class_name', 'status', 'start_time', 'created_at')
    list_display_links = ('get_user_name',)
    list_filter = ('status', 'created_at', 'start_time')
    search_fields = ('user__full_name', 'fitness_class__name')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'fitness_class')
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('updated_by',)

    def get_user_name(self, obj):
        return obj.user.full_name
    get_user_name.short_description = 'Пользователь'

    def get_class_name(self, obj):
        return obj.fitness_class.name if obj.fitness_class else '-'
    get_class_name.short_description = 'Занятие'


@admin.register(FavoriteClass)
class FavoriteClassAdmin(admin.ModelAdmin):
    list_display = ('get_user_name', 'get_class_name', 'created_at')
    list_filter = ('created_at',)
    raw_id_fields = ('user', 'fitness_class')
    readonly_fields = ('created_at',)

    def get_user_name(self, obj):
        return obj.user.full_name
    get_user_name.short_description = 'Пользователь'

    def get_class_name(self, obj):
        return obj.fitness_class.name if obj.fitness_class else '-'
    get_class_name.short_description = 'Занятие'
