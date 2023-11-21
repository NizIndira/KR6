from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DetailView

from main.models import Mailing, Client, Message, MailLogs


class MailingView(TemplateView):
    template_name = 'main/home.html'
    extra_context = {
        'title': 'Общая информация о сайте'
    }


class MailingListView(ListView):
    model = Mailing

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class MailingUpdateView(UpdateView):
    model = Mailing
    fields = ['send_time', 'frequency', 'status', 'name', 'message']
    template_name = 'main/mailing_form.html'
    success_url = reverse_lazy('main:mailing')


class MailingCreateView(CreateView):
    model = Mailing
    fields = ['send_time', 'frequency', 'status', 'name', 'message']
    template_name = 'main/mailing_form.html'
    success_url = reverse_lazy('main:mailing')


class ClientListView(ListView):
    model = Client
    template_name = 'main/client_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ClientUpdateView(UpdateView):
    model = Client
    fields = ['email', 'full_name', 'comment']
    template_name = 'main/client_form3.html'
    success_url = reverse_lazy('main:clients')


class ClientCreateView(CreateView):
    model = Client
    fields = ['email', 'full_name', 'comments']
    template_name = 'main/client_form.html'
    success_url = reverse_lazy('main:clients')


class MessageListView(ListView):
    model = Message
    template_name = 'main/message_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class MessageUpdateView(UpdateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'main/message_form.html'
    success_url = reverse_lazy('main:message')


class MessageCreateView(CreateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'main/message_form.html'
    success_url = reverse_lazy('main:message')


class MessageDetailView(DetailView):
    model = Message
    template_name = 'main/message_detail.html'
    context_object_name = 'message'


class MailLogsListView(ListView):
    model = MailLogs
    template_name = 'main/maillogs_list.html'
    context_object_name = 'logs'

    def get_queryset(self):
        queryset = super().get_queryset()
        mailing_id = self.kwargs.get('pk')
        return queryset.filter(mailing_id=mailing_id)
