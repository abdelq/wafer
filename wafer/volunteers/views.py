from django.views.generic import DetailView
from django.views.generic.list import ListView

from wafer.volunteers.models import Volunteer, Task


class TasksView(ListView):
    model = Task
    template_name = 'wafer.volunteers/tasks.html'


class TaskView(DetailView):
    model = Task
    template_name = 'wafer.volunteers/task.html'


class VolunteerView(DetailView):
    model = Volunteer
    slug_field = 'user__username'
    template_name = 'wafer.volunteers/volunteer.html'

    def get_context_data(self, **kwargs):
        context = super(VolunteerView, self).get_context_data(**kwargs)
        context['profile'] = self.object.user.userprofile
        return context
