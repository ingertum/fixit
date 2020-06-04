from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('json/', Jsonlist.as_view(), name='flat_json'),
    # path('loginold/', user_login, name="old"),
    path('login/', auth_views.LoginView.as_view(), name="login2"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout2'),
    
    path('edit/<int:pk>', ticketEdit, name='ticket_edit'),
    path('editsimple/<int:pk>', ticketSimpleEdit, name='ticket_simpleedit'),
    path('view/<int:pk>', ticketView, name='ticket_view'),
    path('comment/<int:pk>', commentAdd, name='ticket_comment'),
    path('add/', ticketAdd, name='ticket_add'),

    path('tickets/archive/', ticketArchive, name='ticket_archive'),
    path('tickets/', ticketList, name='ticket_list'),
    path('tickets/close/<int:pk>', ticketClose, name='ticket_close'),

    path('masters/', masterList, name='master_list'),
    path('masters/add/', masterAdd, name='master_add'),
    path('masters/edit/<int:pk>', masterEdit, name='master_edit'),
    path('masters/zero/<int:pk>', masterZero, name='master_zero'),


    path('finance/', FinanceAdmin, name='finance_main'),
    path('score/', ScoreMain, name='score_main'),
    path('score/plus', ScoreTrans, name='score_plus'),
    path('score/minus', ScoreTrans, name='score_minus'),
    
    
    path('settings/', Settings, name='settings'),


    path('delete/<int:pk>', TicketDelete.as_view(), name='delete_ticket'),
    path('delete/comment/<int:pk>', CommentDelete.as_view(), name='delete_comment'),

    path('', mainpage, name='main'),
]