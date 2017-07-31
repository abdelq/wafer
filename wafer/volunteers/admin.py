from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count, F

from wafer.volunteers.models import Volunteer, Task, TaskCategory, TaskLocation


def duplicate(modeladmin, request, queryset):
    for object in queryset:
        object.id = None
        object.save()


duplicate.short_description = "Duplicate selected record"


class DayListFilter(admin.SimpleListFilter):
    title = _('day')
    parameter_name = 'day'

    def lookups(self, request, model_admin):
        return (
            (1, 'Sunday'),
            (2, 'Monday'),
            (3, 'Tuesday'),
            (4, 'Wednesday'),
            (5, 'Thursday'),
            (6, 'Friday'),
            (7, 'Saturday'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(start__week_day=self.value())


class NumTasksListFilter(admin.SimpleListFilter):
    title = _('tasks')
    parameter_name = 'tasks'

    def lookups(self, request, model_admin):
        return (
            (0, _('No tasks')),
            (1, _('1 - 5 tasks')),
            (2, _('More than 5 tasks')),
        )

    def queryset(self, request, queryset):
        query = queryset.annotate(num_tasks=Count('tasks'))

        if self.value() == '0':
            return query.filter(num_tasks__lte=0)
        if self.value() == '1':
            return query.filter(num_tasks__gte=1, num_tasks__lte=5)
        if self.value() == '2':
            return query.filter(num_tasks__gte=6)


class HasVolunteersListFilter(admin.SimpleListFilter):
    title = _('volunteers')
    parameter_name = 'volunteers'

    def lookups(self, request, model_admin):
        return (
            ('full', _('No more needed')),
            ('some', _('More needed')),
            ('none', _('None')),
        )

    def queryset(self, request, queryset):
        query = queryset.annotate(nbr_volunteers=Count('volunteers'))

        if self.value() == 'full':
            return query.filter(nbr_volunteers=F('nbr_volunteers_max'))
        elif self.value() == 'some':
            return query.filter(nbr_volunteers__lt=F('nbr_volunteers_max'))
        elif self.value() == 'none':
            return query.filter(nbr_volunteers=0)


class VolunteerAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Personal information', {
            'fields': ('user', 'full_name', 'email', 'contact_number'),
        }),
        (None, {
            'fields': ('tasks', 'preferred_categories'),
        }),
        ('For staff', {
            'classes': ('collapse',),
            'fields': ('staff_rating', 'staff_notes'),
        }),
    )

    list_display = ('user', 'full_name', 'email', 'contact_number',
                    'num_tasks', 'staff_rating')
    list_editable = ('staff_rating',)
    list_filter = ('staff_rating', NumTasksListFilter)

    readonly_fields = ('full_name', 'email', 'contact_number', 'num_tasks')

    def full_name(self, volunteer):
        return u'%s %s' % (volunteer.user.first_name, volunteer.user.last_name)

    def email(self, volunteer):
        return volunteer.user.email

    def contact_number(self, volunteer):
        return volunteer.user.userprofile.contact_number

    def num_tasks(self, volunteer):
        return volunteer.tasks.count()


class TaskAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'description'),
        }),
        (None, {
            'fields': ('start', 'end'),
        }),
        ('Volunteers', {
            'fields': ('volunteers',
                       'nbr_volunteers_min', 'nbr_volunteers_max'),
        }),
        (None, {
            'fields': ('category', 'talk'),
        }),
    )

    list_display = (
        'name', 'start', 'end', 'location', 'nbr_volunteers', 'volunteers_',
        'nbr_volunteers_min', 'nbr_volunteers_max', 'category', 'talk',
    )
    list_editable = (
        'location', 'nbr_volunteers_min', 'nbr_volunteers_max', 'category'
    )
    list_filter = ('category', DayListFilter, HasVolunteersListFilter)

    actions = [duplicate]

    def volunteers_(self, instance):
        return format_html('<ul>{0}</ul>', format_html_join(
            '',
            '<li>{}</li>',
            ((volunteer.user.get_full_name(),)
             for volunteer in instance.volunteers.all())
        ))
    volunteers_.short_description = 'Volunteers'


class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue')
    list_editable = ('name', 'venue')


admin.site.register(Volunteer, VolunteerAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskCategory, TaskCategoryAdmin)
admin.site.register(TaskLocation, LocationAdmin)
