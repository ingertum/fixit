from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import HttpResponseForbidden

from .models import *
from .forms import *

from django.urls import reverse_lazy, resolve
from django.views.generic.edit import DeleteView

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages
# Create your views here.







@login_required(login_url='/login/')
def mainpage(request):
    """Панель управления"""
    profile = Profile.objects.get(user=request.user.id)
    currentRole = profile.specialty.is_boss
    total_money = 0
    if currentRole:
        # Если Менеджер
        all_profiles = Profile.objects.all();
        for pritem in all_profiles:
            total_money = total_money + int(pritem.cash)
        mastersAll = all_profiles.count()
        ticketsAll = Ticket.objects.select_related('status').all()
        ticketsList = ticketsAll.exclude(status__is_archive=0).order_by('-updated')[:4]
        ticketsCount = ticketsAll.exclude(status__is_archive=0).count()
        ticketsFinishedCount = ticketsAll.exclude(status__is_archive=1).count()

        comments = Comment.objects.all().order_by('updated')[:5]

        return render(request,'fixitel/mainpage.html', {
            "isAdmin": True,
            "tickets": ticketsList,
            "ticketsCount": ticketsCount,
            "ticketsFinishedCount": ticketsFinishedCount,
            'mastersAll': mastersAll,
            'profile': profile,
            'comments': comments,
            'total_money': total_money,
        })
    else:
        # Если Мастер
        ticketsAll = Ticket.objects.select_related('status').filter(master__id=profile.id)
        ticketsList = ticketsAll.exclude(status__is_archive=0).order_by('-updated')[:4]
        ticketsCount = ticketsAll.exclude(status__is_archive=0).count()
        comments = Comment.objects.filter(autor__id=profile.id).order_by('-updated')[:5]
        return render(request,'fixitel/mainpage.html', {
            "tickets": ticketsList,
            "ticketsCount": ticketsCount,
            "ticketsFinishedCount": 0,
            'mastersAll': {},
            'profile': profile,
            'comments': comments,
        })
    









@login_required(login_url='/login/')
def ticketList(request):
    """Список активных заявок"""
    profile = Profile.objects.get(user=request.user.id)
    currentRole = profile.specialty.is_boss

    if currentRole:
        # Если Менеджер
        ticketsAll = Ticket.objects.select_related('status').all()
        ticketsList = ticketsAll.exclude(status__is_archive=0).order_by('-created')
        ticketsCount = ticketsList.count()
        return render(request,'fixitel/ticketlist.html', {
            "isAdmin": True,
            'ticketsCount': ticketsCount,
            "tickets": ticketsList,
            'profile': profile,
        })
    else:
        # Если Мастер
        ticketsAll = Ticket.objects.select_related('status').filter(master__id=profile.id)
        ticketsList = ticketsAll.exclude(status__is_archive=0).order_by('-created')
        ticketsCount = ticketsList.count()
        return render(request,'fixitel/ticketlist.html', {
            "isAdmin": False,
            'ticketsCount': ticketsCount,
            "tickets": ticketsList,
            'profile': profile,
        })







@login_required(login_url='/login/')
def ticketArchive(request):
    """Список выполненных заявок"""
    profile = Profile.objects.get(user=request.user.id)
    currentRole = profile.specialty.is_boss
    if not currentRole:
        return HttpResponseForbidden()

    profile = Profile.objects.get(user=request.user.id)

    ticketsAll = Ticket.objects.select_related('status').all()
    ticketsList = ticketsAll.exclude(status__is_archive=1).order_by('-created')
    ticketsCount = ticketsList.count()

    return render(request,'fixitel/ticketarchive.html', {
        "isAdmin": True,
        'ticketsCount': ticketsCount,
        "tickets": ticketsList,
        'profile': profile,
    })






@login_required(login_url='/login/')
def ticketAdd(request):
    """Форма добавления заявки"""
    profile = Profile.objects.get(user=request.user.id)
    currentRole = profile.specialty.is_boss
    if not currentRole:
        return HttpResponseForbidden()

    if request.method == "POST":
        form = TicketsForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            messText = ticket.save()
            messages.add_message(request, messages.SUCCESS, messText)
            if ticket.status.is_archive:
                return redirect(reverse_lazy('ticket_list'))
            else:
                return redirect(reverse_lazy('ticket_archive'))
        else: 
            form = TicketsForm(request.POST)
    else:
        form = TicketsForm()
    return render(request, 'fixitel/edit.html', {
        "isAdmin": True,
        'form': form,
        'profile': profile,
        'pagetitle': "Создать заявку",
        'id': 0,
    })






@login_required(login_url='/login/')
def ticketEdit(request, pk):
    """Форма редактирования заявки"""
    profile = Profile.objects.get(user=request.user.id)
    currentRole = profile.specialty.is_boss
    if not currentRole:
        return redirect('/view/%s' % pk)

    ticket = get_object_or_404(Ticket, pk=pk)
    comments = Comment.objects.filter(Ticket__id = ticket.id).order_by('updated')
    commentform = CommentForm()

    if request.method == "POST":
        form = TicketsForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save(commit=False)
            messText = ticket.save()
            messages.add_message(request, messages.SUCCESS, messText)

            if ticket.status.is_archive:
                return redirect(reverse_lazy('ticket_list'))
            else:
                return redirect(reverse_lazy('ticket_archive'))
    else:
        form = TicketsForm(instance=ticket)

    return render(request, 'fixitel/edit.html', {
        "isAdmin": True,
        'form': form,
        'profile': profile,
        'pagetitle': "Редактировать заявку",
        'comments': comments,
        'id': pk,
        'commentform': commentform,
        'ticket': ticket,
    })


@login_required(login_url='/login/')
def ticketClose(request, pk):
    """Закрытие заявки"""
    endStatus = Status.objects.get(name="Выполнена")
    ticket = get_object_or_404(Ticket, pk=pk)
    ticket.status = endStatus
    messText = ticket.save()
    messages.add_message(request, messages.SUCCESS, messText)
    return redirect('/tickets/')











@login_required(login_url='/login/')
def ticketView(request, pk):
    """Просмотр заявки"""
    profile = Profile.objects.get(user=request.user.id)
    currentRole = profile.specialty.is_boss
    ticket = get_object_or_404(Ticket, pk=pk)

    comments = Comment.objects.filter(Ticket__id = ticket.id).order_by('updated')
    commentform = CommentForm()
    ticketForm = TicketsSimpleForm(instance=ticket)

    return render(request, 'fixitel/view.html', {
        "isAdmin": currentRole,
        'profile': profile,
        'pagetitle': "Просмотр заявки",
        'ticket': ticket,
        'comments': comments,
        'id': pk,
        'commentform': commentform,
        'ticketForm': ticketForm,
    })

@login_required(login_url='/login/')
def ticketSimpleEdit(request, pk):
    """Форма редактирования статуса заявки"""
    if request.method == "POST":
        ticket = get_object_or_404(Ticket, pk=pk)
        form = TicketsSimpleForm(request.POST)
        ticket.status = Status.objects.get(id=form.data['status'])
        ticket.save()
        messages.add_message(request, messages.SUCCESS, 'Статус заявки изменен на «%s»' % ticket.status)
    
    return redirect('/view/%s' % pk)







@login_required(login_url='/login/')
def commentAdd(request, pk):
    """Просмотр заявки"""
    profile = Profile.objects.get(user=request.user.id)
    ticket = get_object_or_404(Ticket, pk=pk)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            newcomment = form.save(commit=False)
            newcomment.autor = profile
            newcomment.Ticket = ticket
            newcomment.save();
            messages.add_message(request, messages.SUCCESS, "Комментарий добавлен")
            return redirect('/view/%s' % pk)
    else:
        return HttpResponse('Ошибка создания коментария')











# =======
# Мастера
# =======
@login_required(login_url='/login/')
def masterList(request):
    """Страница списка мастеров"""    
    profile = Profile.objects.get(user=request.user.id)
    currentRole = profile.specialty.is_boss
    if not currentRole:
        return HttpResponseForbidden()

    profiles = Profile.objects.all();
    profilesCount = profiles.count();
    return render(request, 'fixitel/masterslist.html', {
        "isAdmin": True,
        'profile': profile,
        'profiles': profiles,
        'profilesCount': profilesCount,
    })



@login_required(login_url='/login/')
def masterEdit(request, pk):
    """Форма редактирования мастера"""
    profile = Profile.objects.get(user=request.user.id)
    currentRole = profile.specialty.is_boss

    targetProfile = get_object_or_404(Profile, pk=pk)
    targetUser = User.objects.get(id=targetProfile.user.id)
    
    if not currentRole:
        return HttpResponseForbidden()


    if request.method == "POST":
        user_form = MasterEditForm(request.POST, instance=targetUser)
        profile_form = MasterForm(request.POST, instance=targetProfile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            new_user_profile = profile_form.save(commit=False)
            profile_form.save()
            messages.add_message(request, messages.SUCCESS, 'Данные мастера успешно отредактированы')
            return redirect(request.path_info)
            
    else:
        user_form = MasterEditForm(instance=targetUser)
        profile_form = MasterForm(instance=targetProfile)

    return render(request, 'fixitel/editmaster.html', {
        "isAdmin": currentRole,
        'user_form': user_form,
        'profile_form': profile_form,
        'pagetitle': "Редактировать данные мастера %s %s" % (targetUser.first_name, targetUser.last_name),
        'profile': profile,
        'targetProfile': targetProfile,
    })










@login_required(login_url='/login/')
def masterAdd(request):
    """Форма добавления мастера"""
    profile = Profile.objects.get(user=request.user.id)
    currentRole = profile.specialty.is_boss
    if not currentRole:
        return HttpResponseForbidden()

    if request.method == "POST":
        profile_form = MasterForm(request.POST)
        user_form = UserForm(request.POST);
        if user_form.is_valid() and profile_form.is_valid():

            newUser = user_form.save();
            newProfile = profile_form.save(commit=False);
            
            newProfile.user = newUser
            newProfile.save()
            return redirect('/masters/')
            messages.add_message(request, messages.SUCCESS, 'Мастер успешно зарегистрирован')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки')
            
    else:
        user_form = UserForm()
        profile_form = MasterForm()

    return render(request, 'fixitel/editmaster.html', {
        "isAdmin": True,
        'user_form': user_form,
        'profile_form': profile_form,
        # 'user_moreform': user_moreform,
        'pagetitle': "Добавление нового мастера",
        'profile': profile,
    })




@login_required(login_url='/login/')
def masterZero(request, pk):
    """Форма обнуления счета мастера"""

    profile = Profile.objects.get(user=request.user.id)
    currentRole = profile.specialty.is_boss
    if not currentRole:
        return redirect('/finance/')

    current = get_object_or_404(Profile, pk=pk)
    current.cash = 0
    current.save()
    


    messages.add_message(request, messages.SUCCESS, 'Счет мастера обнулен')
    return redirect('/finance/')













@login_required(login_url='/login/')
def FinanceAdmin(request):
    profile = Profile.objects.get(user=request.user.id)
    currentRole = profile.specialty.is_boss
    if currentRole:
        all_profiles = Profile.objects.all();
        total_money = 0

        for profile in all_profiles:
            total_money = total_money + int(profile.cash)
    else:
        total_money = profile.cash
        all_profiles = {}


    return render(request, 'fixitel/finance.html', {
        "isAdmin": currentRole,
        'pagetitle': "Финансы",
        'profile': profile,
        'all_profiles': all_profiles,
        'total_money': total_money,
    })





@login_required(login_url='/login/')
def ScoreMain(request):
    profile = Profile.objects.get(user=request.user.id)

    currentRole = profile.specialty.is_boss
    if not currentRole:
        return redirect('/')

    try:
        companyCash = Profile.objects.get(findata="Main")
        total_money = companyCash.cash
    except Profile.DoesNotExist:
        total_money = "Не найден счёт"

    transList = Transaction.objects.all()[:20]
    
    return render(request, 'fixitel/score/main.html', {
        "isAdmin": currentRole,
        'pagetitle': "Финансовые операции",
        'profile': profile,
        'total_money': total_money,
        'transList': transList,
    })





@login_required(login_url='/login/')
def ScoreTrans(request):
    profile = Profile.objects.get(user=request.user.id)
    '''Форма добавления добавления транзакции'''
    currentRole = profile.specialty.is_boss
    if not currentRole:
        return redirect('/')


    current_url = resolve(request.path_info).url_name
    if current_url == 'score_plus':
        pagetitle = "Добавить доход"
    else: 
        pagetitle = "Добавить расход"


    if request.method == "POST":
        form = TransactForm(request.POST)
        if form.is_valid():
            newTrans = form.save(commit=False);

            if current_url == 'score_minus' and newTrans.total > 0:
                newTrans.total = newTrans.total * -1
            
            newTrans.save()
            messages.add_message(request, messages.SUCCESS, 'Транзакция успешно создана')
            return redirect(reverse_lazy('score_main'))
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки')
            
    else:
        form = TransactForm()

    
    return render(request, 'fixitel/score/add.html', {
        "isAdmin": True,
        'pagetitle': pagetitle,
        'profile': profile,
        'form': form,
    })




@login_required(login_url='/login/')
def Settings(request):
    profile = Profile.objects.get(user=request.user.id)
    currentRole = profile.specialty.is_boss

    return render(request, 'fixitel/settings.html', {
        "isAdmin": currentRole,
        'pagetitle': "Настройки",
        'profile': profile,
    })






# Удаление Заявки
class TicketDelete(LoginRequiredMixin, DeleteView):
    model = Ticket
    success_url = reverse_lazy('ticket_list')

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.groups.filter(name__in=['Администраторы', 'Разработчики']).exists():
            messages.error(request, 'Нет прав для удаления заявки')
            return redirect( reverse_lazy( 'ticket_view', kwargs={'pk': self.get_object().pk}) )
        return super(TicketDelete, self).dispatch(request, *args, **kwargs)


# Удаление Комментария
class CommentDelete(LoginRequiredMixin, DeleteView):
    model = Comment
    def get_success_url(self):
        ticket = self.object.Ticket
        return reverse_lazy( 'ticket_view', kwargs={'pk': ticket.id})

    def dispatch(self, request, *args, **kwargs):
        """ Проверка, что только автор может удалить комментарий """
        obj = self.get_object()
        if obj.autor.user != self.request.user:
            messages.error(request, 'Можно удалить только свой комментарий')
            return redirect( reverse_lazy( 'ticket_view', kwargs={'pk': obj.Ticket.id}) )
        return super(CommentDelete, self).dispatch(request, *args, **kwargs)









