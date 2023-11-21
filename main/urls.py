from django.urls import path

from main.apps import MainConfig
from main.views import MailingView, MailingListView, MailingCreateView, MailingUpdateView, ClientListView, \
    ClientUpdateView, ClientCreateView, MessageListView, MessageCreateView, MessageUpdateView, MessageDetailView, \
    MailLogsListView

app_name = MainConfig.name

urlpatterns = [
    path('', MailingView.as_view(), name='home'),
    path('mailing/', MailingListView.as_view(), name='mailing'),
    path('mailing/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailing/<int:pk>/edit/', MailingUpdateView.as_view(), name='mailing_update'),

    path('clients/', ClientListView.as_view(), name='clients'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='clients_update'),
    path('clients/create/', ClientCreateView.as_view(), name='clients_create'),

    path('message/', MessageListView.as_view(), name='message'),
    path('message/create/', MessageCreateView.as_view(), name='message_create'),
    path('message/<int:pk>/edit/', MessageUpdateView.as_view(), name='message_update'),
    path('message/<int:pk>/view/', MessageDetailView.as_view(), name='message_view'),

    path('maillogs/<int:pk>/', MailLogsListView.as_view(), name='maillogs'),
]
