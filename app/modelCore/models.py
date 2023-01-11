from django import dispatch
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.gis.db.models import PointField

class Owner(models.Model):
    name = models.CharField(max_length=128, default='')
    driverNum = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):

    def create_user(self, phone, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not phone:
            raise ValueError('Users must have an phone')
        # user = self.model(email=self.normalize_email(email), **extra_fields)
        user = self.model(
            phone = phone, 
            name=extra_fields.get('name'),
            line_id=extra_fields.get('line_id'),
            vehicalLicence=extra_fields.get('vehicalLicence'),
            userId=extra_fields.get('userId'),
            idNumber=extra_fields.get('idNumber'),
            gender=extra_fields.get('gender'),
            type=extra_fields.get('type'),
            category=extra_fields.get('category'),
            car_model=extra_fields.get('car_model'),
            car_color=extra_fields.get('car_color'),
            number_sites=extra_fields.get('number_sites'),
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, phone, password, **extra_fields):
        """Creates and saves a new super user"""
        user = self.create_user(phone, password, **extra_fields)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that suppors using email instead of username"""
    phone = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    
    line_id = models.CharField(max_length=255, default='', blank = True, null=True, unique=True)

    vehicalLicence = models.CharField(max_length=255, default='', null=True) #車牌
    userId = models.CharField(max_length=10, default='', null=True ) #台號
    idNumber = models.CharField(max_length=20, default='', null=True) #身分證
    gender = models.CharField(max_length=10, default='', blank = True, null=True)
    type = models.CharField(max_length=20, default='', blank = True, null=True) #type(car, suv, sports_car, van)
    category =  models.CharField(max_length=20, default='', blank = True, null=True) #category(taxi, diversity, rental_car, x_card)
    car_model = models.CharField(max_length=128, default='', blank = True, null=True)
    car_color = models.CharField(max_length=20, default='', blank = True, null=True)
    number_sites = models.IntegerField(default=0, blank = True, null=True)
    
    car_memo = models.TextField(default='', blank = True, null=True)

    is_online = models.BooleanField(default=False)
    left_money = models.IntegerField(default=0)

    is_passed = models.BooleanField(default=False)
    owner =  models.ForeignKey(
        Owner,
        on_delete=models.RESTRICT,
        null=True
    )
    current_lat = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null=True)
    current_lng = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null=True)
    location = PointField(srid=4326, geography=True, blank=True, null=True)

    dispatch_fee_percent_integer = models.IntegerField(
        default=10,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ]
    )

    USERNAME_FIELD = 'phone'

    def __str__(self):
        return self.name

class UserStoreMoney(models.Model):
    user =  models.ForeignKey(
        User,
        on_delete=models.RESTRICT
    )
    # 增加或減少金額
    increase_money = models.IntegerField(default=0)
    # decrease_money = models.IntegerField(default=0)
    
    # 當時餘額
    user_left_money = models.IntegerField(default=0)

    # 當時結算餘額
    sum_money = models.IntegerField(default=0)
   
    date = models.DateTimeField(auto_now=False,null=True)

class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    owner =  models.ForeignKey(
        Owner,
        on_delete=models.RESTRICT,
        null=True
    )
    line_id = models.CharField(max_length=255, default='', blank = True, null=True)

    def __str__(self):
        return self.name

class Case(models.Model):
    #(wait, way_to_catch, arrived, catched, on_road, finished, canceled)
    CASE_STATE_CHOICES = [
        ('wait', 'wait'),
        ('way_to_catch', 'way_to_catch'),
        ('arrived', 'arrived'),
        ('catched', 'catched'),
        ('on_road', 'on_road'),
        ('finished', 'finished'),
        ('canceled', 'canceled'),
    ]
    case_state = models.CharField(max_length=20, choices=CASE_STATE_CHOICES, default='') 
    
    customer =  models.ForeignKey(
        Customer,
        on_delete=models.RESTRICT
    )
    customer_name = models.CharField(max_length=128, default='', blank = True, null=True)
    customer_phone = models.CharField(max_length=20, default='', blank = True, null=True)
    
    #customer owner
    owner =  models.ForeignKey(
        Owner,
        on_delete=models.DO_NOTHING,
        null=True,
        blank = True
    )

    user =  models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        null=True,
        blank = True
    )

    userId = models.CharField(max_length=10, default='', blank = True, null=True) #台號

    on_lat = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null=True)
    on_lng = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null=True)
    on_address = models.CharField(max_length=255, default='', blank = True, null=True)
    
    off_lat = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null=True)
    off_lng = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null=True)
    off_address = models.CharField(max_length=255, default='', blank = True, null=True)
    
    case_money = models.IntegerField(default=0, blank = True, null=True)
    memo = models.TextField(default='', blank = True, null=True)

    create_time = models.DateTimeField(auto_now=False, blank = True, null=True)
    confirm_time = models.DateTimeField(auto_now=False, blank = True, null=True)
    arrived_time = models.DateTimeField(auto_now=False, blank = True, null=True)
    catched_time = models.DateTimeField(auto_now=False, blank = True, null=True)
    off_time = models.DateTimeField(auto_now=False, blank = True, null=True)

    dispatch_fee = models.IntegerField(default=0, blank = True, null=True)

class UserCaseShip(models.Model):
    user =  models.ForeignKey(
        User,
        on_delete=models.RESTRICT
    )
    case =  models.ForeignKey(
        Case,
        on_delete=models.RESTRICT
    )
    state = models.CharField(max_length=20, default='state1') #state1, state2, state3
    countdown_second = models.IntegerField(default=20)

class CaseSummary(models.Model):
    case = models.ForeignKey(
        Case,
        on_delete=models.RESTRICT,
        null= True
    )
    driver_user_id = models.CharField(max_length=10, default='')
    driver_owner = models.CharField(max_length=128, default='')

    customer_name = models.CharField(max_length=128, default='')
    customer_owner = models.CharField(max_length=128, default='')

    increase_money = models.IntegerField(default=0)
    decrease_money = models.IntegerField(default=0)
    driver_left_money = models.IntegerField(default=0)

class MonthSummary(models.Model):
    month_date = models.DateField(null=True)
    # month_increase_money = models.IntegerField(default=0)
    # month_decrease_money = models.IntegerField(default=0)
    # month_owners= models.CharField(max_length=255, default='') #’nameA, nameB’
    # month_owners_decrease_money= models.CharField(max_length=255, default='') #’123, 456’
    # month_driver_arrears = models.IntegerField(default=0)
    month_store_money = models.IntegerField(default=0)
    month_owner_a_money = models.IntegerField(default=0)
    month_owner_b_money = models.IntegerField(default=0)
    month_driver_arrears = models.IntegerField(default=0)

