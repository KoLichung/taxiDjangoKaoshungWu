from django import dispatch
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.gis.db.models import PointField

class UserManager(BaseUserManager):

    def create_user(self, phone, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not phone:
            raise ValueError('Users must have an phone')
        # user = self.model(email=self.normalize_email(email), **extra_fields)
        user = self.model(
            phone = phone, 
            name=extra_fields.get('name'),
            nick_name=extra_fields.get('nick_name'),
            line_id=extra_fields.get('line_id'),
            vehicalLicence=extra_fields.get('vehicalLicence'),
            # userId=extra_fields.get('userId'),
            idNumber=extra_fields.get('idNumber'),
            # gender=extra_fields.get('gender'),
            # type=extra_fields.get('type'),
            # category=extra_fields.get('category'),
            # car_model=extra_fields.get('car_model'),
            car_color=extra_fields.get('car_color'),
            number_sites=extra_fields.get('number_sites'),
            car_memo=extra_fields.get('car_memo'),
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
    nick_name = models.CharField(max_length=255, default='', blank = True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    
    line_id = models.CharField(max_length=255, default='', blank = True, null=True, unique=True)
    telegram_id = models.CharField(max_length=128, default='', blank = True, null=True)
    is_telegram_bot_enable = models.BooleanField(default=True)

    vehicalLicence = models.CharField(max_length=255, default='', null=True) #車牌
    # userId = models.CharField(max_length=10, default='', null=True ) #台號
    idNumber = models.CharField(max_length=20, default='', blank = True, null=True) #身分證
    gender = models.CharField(max_length=10, default='', blank = True, null=True)

    # type = models.CharField(max_length=20, default='', blank = True, null=True) #type(car, suv, sports_car, van)
    # category =  models.CharField(max_length=20, default='', blank = True, null=True) #category(taxi, diversity, rental_car, x_card)
    # car_model = models.CharField(max_length=128, default='', blank = True, null=True)
    
    car_color = models.CharField(max_length=20, default='', blank = True, null=True)
    number_sites = models.IntegerField(default=0, blank = True, null=True)
    
    car_memo = models.TextField(default='', blank = True, null=True)

    is_online = models.BooleanField(default=False)
    left_money = models.IntegerField(default=0)

    is_passed = models.BooleanField(default=False)

    current_lat = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null=True)
    current_lng = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null=True)
    location = PointField(srid=4326, geography=True, blank=True, null=True)

    is_on_task = models.BooleanField(default=False)
    # 20230/06/20 新增 is_asking
    is_asking = models.BooleanField(default=False) 

    violation_time = models.IntegerField(default=0)
    is_in_penalty = models.BooleanField(default=False)
    penalty_datetime = models.DateTimeField(auto_now=False,blank = True,null=True)

    # dispatch_fee_percent_integer = models.IntegerField(
    #     default=10,
    #     validators=[
    #         MaxValueValidator(100),
    #         MinValueValidator(0)
    #     ]
    # )

    USERNAME_FIELD = 'phone'

    def __str__(self):
        return self.name
    
    def car_teams_string(self):
        car_teams_string = ''
        if UserCarTeamShip.objects.filter(user=self).count() > 0:
            ships = UserCarTeamShip.objects.filter(user=self)
            for ship in ships:
                if car_teams_string == '':
                    car_teams_string = ship.carTeam.name
                else:
                    car_teams_string = car_teams_string+' '+ ship.carTeam.name
            return car_teams_string
        else:
            return '無車隊'

    def main_car_team_string(self):
        if UserCarTeamShip.objects.filter(user=self).count() > 0:
            ships = UserCarTeamShip.objects.filter(user=self)
            return ships[0].carTeam.name
        else:
            return '無車隊'

    def car_teams_id_array(self):
        user_car_teams = UserCarTeamShip.objects.filter(user=self)
        user_carTeam_ids = list(user_car_teams.values_list('carTeam',flat=True))
        return user_carTeam_ids

class CarTeam(models.Model):
    name = models.CharField(max_length=255)
    day_case_count = models.IntegerField(default=0)

    @property
    def get_car_team_number_string(self):
        if self.day_case_count < 10:
            return f'0000{self.day_case_count}'
        elif self.day_case_count < 100:
            return f'000{self.day_case_count}'
        elif self.day_case_count < 1000:
            return f'00{self.day_case_count}'
        elif self.day_case_count < 10000:
            return f'0{self.day_case_count}'
        else:
            return f'{self.day_case_count}'

    def __str__(self):
        return self.name

class UserCarTeamShip(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_car_teams'
    )
    carTeam = models.ForeignKey(
        CarTeam,
        on_delete=models.CASCADE,
        related_name='car_team_users'
    )
    # 是否派單, 如果不派單, 該車隊發出的單就不會派給他?!
    is_dispatch = models.BooleanField(default=True)

class UserStoreMoney(models.Model):
    user =  models.ForeignKey(
        User,
        on_delete=models.CASCADE
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
    line_id = models.CharField(max_length=255, default='', blank = True, null=True)

    def __str__(self):
        return self.name

class Case(models.Model):
    #派單的車隊
    carTeam = models.ForeignKey(
        CarTeam,
        on_delete=models.SET_NULL,
        blank = True,
        null=True,
    )
    #單號
    case_number = models.CharField(max_length=255, default='', blank = True, null=True) #單號

    #(wait, way_to_catch, arrived, catched, on_road, finished, canceled)
    CASE_STATE_CHOICES = [
        ('wait', 'wait'),
        ('dispatching', 'dispatching'),
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
        on_delete=models.SET_NULL,
        blank = True,
        null=True,
    )

    customer_name = models.CharField(max_length=128, default='', blank = True, null=True)
    customer_phone = models.CharField(max_length=20, default='', blank = True, null=True)

    # 派單者的 telegram_id
    telegram_id = models.CharField(max_length=128, default='', blank = True, null=True)

    # user is the driver
    user =  models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank = True
    )

    # userId = models.CharField(max_length=10, default='', blank = True, null=True) #台號

    on_lat = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null=True)
    on_lng = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null=True)
    on_address = models.CharField(max_length=255, default='', blank = True, null=True)
    
    off_lat = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null=True)
    off_lng = models.DecimalField(max_digits=9, decimal_places=6, blank = True, null=True)
    off_address = models.CharField(max_length=255, default='', blank = True, null=True)
    
    case_money = models.IntegerField(default=0, blank = True, null=True)

    time_memo = models.CharField(max_length=255, default='', blank = True, null=True)
    memo = models.TextField(default='', blank = True, null=True)

    create_time = models.DateTimeField(auto_now=False, blank = True, null=True)
    confirm_time = models.DateTimeField(auto_now=False, blank = True, null=True)
    arrived_time = models.DateTimeField(auto_now=False, blank = True, null=True)
    catched_time = models.DateTimeField(auto_now=False, blank = True, null=True)
    off_time = models.DateTimeField(auto_now=False, blank = True, null=True)

    dispatch_fee = models.IntegerField(default=0, blank = True, null=True)
    exclude_ids_text = models.TextField(default='',blank = True, null=True)

class UserCaseShip(models.Model):
    user =  models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        blank = True, 
        null=True,
        related_name='user_cases'
    )
    case =  models.ForeignKey(
        Case,
        on_delete=models.RESTRICT,
        related_name='case_users'
    )
    
    expect_second = models.IntegerField(default=0)
    dispatch_time = models.DateTimeField(auto_now=False, blank = True, null=True)

    # ask_ranking_ids_text = models.TextField(default='',blank = True, null=True)
    # ask_manager_ids_text = models.TextField(default='',blank = True, null=True)
    # ask_no_car_team_ids_text = models.TextField(default='',blank = True, null=True)

    # 以下是 2023/06/20 修正, 去掉 ask_same_car_team_ids_text, ask_not_same_car_team_ids_text, countdown_second
    # 並把 exclude_ids_text 移到 Case

    # ask_same_car_team_ids_text = models.TextField(default='',blank = True, null=True)
    # ask_not_same_car_team_ids_text = models.TextField(default='',blank = True, null=True)
    
    # exclude_ids_text = models.TextField(default='',blank = True, null=True)
    # countdown_second = models.IntegerField(default=18)
    

class CaseSummary(models.Model):
    case = models.ForeignKey(
        Case,
        on_delete=models.RESTRICT,
        null= True
    )
    driver_user_id = models.CharField(max_length=10, default='')

    customer_name = models.CharField(max_length=128, default='')

    increase_money = models.IntegerField(default=0)
    decrease_money = models.IntegerField(default=0)
    driver_left_money = models.IntegerField(default=0)

class AppVersion(models.Model):
    iOS_current_version = models.CharField(max_length=10, default='', blank = True, null=True)
    android_current_version = models.CharField(max_length=10, default='', blank = True, null=True)