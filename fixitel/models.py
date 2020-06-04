from django.db import models
from django.conf import settings
from django.utils import timezone

from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
# from django.core.exceptions import ObjectDoesNotExist
# Create your models here.









class Status(models.Model):
    """Статусы заявок"""
    name = models.CharField(max_length=300, verbose_name="Название статуса")
    is_archive = models.BooleanField(verbose_name="Заявка активна при этом статусе")
    order = models.DecimalField(default=1, verbose_name="Порядковый номер", decimal_places=0, max_digits=50)

    class Meta:
        verbose_name = "Статус заявок"
        verbose_name_plural = "Статусы заявок"
        ordering = ["order", "name"]
    def __str__(self):
        return self.name






class Specialty(models.Model):
    """Статусы заявок"""
    name = models.CharField(max_length=300, verbose_name="Название должности")
    is_boss = models.BooleanField(verbose_name="Это менеджерская должность")
    order = models.DecimalField(default=1, verbose_name="Порядковый номер", decimal_places=0, max_digits=50)

    class Meta:
        verbose_name = "Должность мастеров"
        verbose_name_plural = "Должности мастеров"
        ordering = ["order", "name"]
    def __str__(self):
        return self.name







class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialty = models.ForeignKey(
        'Specialty',
        null=True,
        on_delete=models.SET_NULL,
        default=1,
        verbose_name="Должность"
    )
    cash = models.PositiveIntegerField(verbose_name="Денег на счету (Р)", default=0)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    findata = models.CharField(max_length=300, verbose_name="Финансовые реквизиты", blank=True, null=True)
    role = models.ForeignKey(
        Group,
        null=True,
        default=1,
        on_delete=models.SET_NULL,
        verbose_name="Роль прав в системе"
    )

    class Meta:
            ordering = ('-created',)
            verbose_name = "Профиль сотрудника"
            verbose_name_plural = "Профили сотрудников"

    def __str__(self):
        return '%s %s [ %s / %s ]' % (self.user.first_name, self.user.last_name, self.specialty,  self.role)

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        # Устанавливаем группу пользователя при изменении его роли
        # Также даём доступ в админкк
        targetUser = User.objects.get(id=self.user.id)
        targetUser.groups.clear()
        targetUser.groups.add(self.role)
        if(self.role.id != 1):
            targetUser.is_staff=True
            if(self.role.id != 2):
                targetUser.is_superuser = True
            targetUser.save()
        else:
            targetUser.is_staff=False
            targetUser.is_superuser = False
            targetUser.save()





class Ticket(models.Model):

    title = models.CharField(max_length=300, verbose_name="Название заявки", default="Новая заявка")
    clientName = models.CharField(max_length=300, verbose_name="Ф.И.О. клиента", blank=True)
    clientAdress = models.CharField(max_length=300, verbose_name="Адрес клиента", blank=True)
    clientPhone = models.CharField(max_length=300, verbose_name="Номер телефона клиента", blank=True)
    body = models.TextField(verbose_name="Описание проблемы", blank=True)
    status = models.ForeignKey(
        'Status',
        null=True,
        on_delete=models.SET_NULL,
        default=1,
        verbose_name="Статус"

    )
    master = models.ForeignKey(
        'Profile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        default=None,
        verbose_name="Назначенный мастер",
        related_name='masters',
    )
    fullprice = models.PositiveIntegerField(verbose_name="Стоимость работ (Р)", default=0)
    price = models.PositiveIntegerField(verbose_name="Выплата за выезд (Р)", default=0)
    priceDetails = models.PositiveIntegerField(verbose_name="Стоимость комплектующих (Р)", default=0)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated = models.DateTimeField(auto_now=True)
    

    def save(self, *args, **kwargs): 
        """Увеличиваем количество денег мастера при завершении заявки"""
        
        try:
            oldTicket = Ticket.objects.get(pk = self.pk)
        except Ticket.DoesNotExist:
            super(Ticket, self).save(*args, **kwargs)
            message =  'Заявка  «%s» создана' % self.title
            return message

        if oldTicket.status.name != "Выполнена" and self.status.name == "Выполнена":
            if self.master != None:
                currentMaster = Profile.objects.get(user__id = self.master.user.id)
                currentMaster.cash += self.price
                currentMaster.save()
                
                message = 'Заявка «%s» закрыта. Мастеру «%s» начислено %s Р.' % (self.title, currentMaster, self.price)
            else:
                message = 'Заявка  «%s» закрыта' % self.title
        else: 
            message =  'Заявка  «%s» отредактированна' % self.title
        
        super(Ticket, self).save(*args, **kwargs)
        return message

        
        

    class Meta:
        ordering = ('-created',)
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
    def __str__(self):
        return self.title






class Comment(models.Model):
    autor = models.ForeignKey(
        'Profile',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        default=None,
        verbose_name="Автор комментария",
        related_name='autor',
    )
    Ticket = models.ForeignKey(
        'Ticket',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        default=None,
        verbose_name="К заявке",
        related_name='ticketFor',
    )
    body = models.TextField(verbose_name="комментарий")
    created = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '[%s] Комментарий от %s' % (self.updated, self.autor)

    class Meta:
        ordering = ('-updated',)
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"





class Log(models.Model):
    logTypes = [
        ('primary', 'primary'),
        ('finance', 'finance'),
        ('error', 'error'),
        ('success', 'success'),
    ]
    logtype = models.CharField(max_length=300, choices=logTypes, verbose_name="тип лога")
    logtext = models.CharField(max_length=300, verbose_name="сообщение", default="", blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="дата")

    class Meta:
        ordering = ('-created',)
        verbose_name = "Логи"
        verbose_name_plural = "Логи"




class TransactionTypes(models.Model):
    name = models.CharField(max_length=300, verbose_name="Название Статьи расходов")
    order = models.DecimalField(default=1, verbose_name="Порядковый номер", decimal_places=0, max_digits=50)
    moneyback = models.BooleanField(verbose_name="Можно отменить", default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-name',)
        verbose_name = "Статьи расходов"
        verbose_name_plural = "Статьи расходов"



def getCompanyProfileID():
    try:
        companyScore = Profile.objects.get(findata="Main");
        return companyScore.id
    except Profile.DoesNotExist:
        raise ValueError("Счёт компании не найден. Создайте сотрудника и укажите в платежных реквизитах слово Main")


class Transaction(models.Model):
    transact_type = models.ForeignKey(
        TransactionTypes,
        null=False,
        blank=False,
        on_delete=models.SET_DEFAULT,
        default=1,
        verbose_name="Статья расхода",
        related_name='transaction',
    )
    name = models.TextField(max_length=300, verbose_name="Назначение платежа", blank=True, null=True)
    total = models.IntegerField(verbose_name="Сумма (Р)")
    before = models.IntegerField(verbose_name="Счёт до (Р)", default=0)
    after = models.IntegerField(verbose_name="Счёт после (Р)", default=0)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата транзакции")
    trans_from = models.ForeignKey(
        Profile,
        null=True,
        blank=True,
        on_delete=models.SET_DEFAULT,
        default=getCompanyProfileID,
        verbose_name="Отправитель",
        related_name='trans_from',
    )
    trans_to = models.ForeignKey(
        Profile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        default=None,
        verbose_name="Получатель",
        related_name='trans_to',
    )

    def __str__(self):
        return '%s (%s Р.)' % (self.name, self.total)

    class Meta:
        ordering = ('-created',)
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакция"


    def save_model(self, request, obj, form, change):
        # if obj.pk:
        messages.success(request, 'Write your overrided message here...')
        pass
            # return False
        # super(Transaction, self).save_model(request, obj, form, change)


    def save(self, *args, **kwargs): 
        """Перечисляем деньги"""

        if self._state.adding:
            companyCash = Profile.objects.get(findata="Main");
            if self.trans_from == companyCash:
                self.before = companyCash.cash
                companyCash.cash += int(self.total)
                companyCash.save()
                self.after = companyCash.cash
            super(Transaction, self).save(*args, **kwargs)
        else:
            return False

        # if self.trans_from == companyScore:

        
        