from django.db import models
from django.contrib.auth import get_user_model, password_validation
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db import IntegrityError
from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)

from rest_framework.exceptions import ValidationError

from core.models import AbstractBaseModel, ActiveObjectsQuerySet
from core.utils.validators import validate_phone_number, validate_required_arguments


class UserManager(BaseUserManager):
    """
    Custom manager to handle the User model methods.
    """

    def create_user(
        self, full_name=None, email=None, password=None, phone=None, company=None, county=None, is_reseller=False, parent_company=None, is_admin=True, **kwargs
    ):
        REQUIRED_ARGS = ("full_name", "email", "password", "phone", "company")
        validate_required_arguments(
            {
                "full_name": full_name,
                "email": email,
                "password": password,
                "phone": phone,
                "company": company,
                "county": county
            },
            REQUIRED_ARGS,
        )
        # ensure that the passwords are strong enough.
        try:
            password_validation.validate_password(password)
        except ValidationError as exc:
            # return error accessible in the appropriate field, ie password
            raise ValidationError({"password": exc.messages}) from exc

        get_or_create_company_mapping = {
            True: self.create_company,
            False: self.get_company
        }
        
        company = get_or_create_company_mapping[is_admin](name=company, county=county, is_reseller=is_reseller, parent=parent_company)
        
        user = self.model(
            full_name=full_name,
            email=self.normalize_email(email),
            phone=phone,
            company=company,
            **kwargs
        )   
        # ensure phone number and all fields are valid.
        user.clean()
        user.set_password(password)
        user.save()
        return user

    def get_company(self, name=None, county=None, is_reseller=None, parent=None):
        return Company.objects.get(name=name)

    def create_company(self, name=None, county=None, is_reseller=None, parent=None):
        try:
            company = Company.objects.create(name=name, county=county, is_reseller=is_reseller, parent=parent)
        except IntegrityError:
            raise ValidationError({"name": "Company already exists with name"}) 
        return company

    def create_superuser(
        self,
        full_name=None,
        email=None,
        password=None,
        phone=None,
        company=None,
        **kwargs
    ):
        """
        This is the method that creates superusers in the database.
        """

        superuser = self.create_user(
            full_name=full_name,
            email=email,
            password=password,
            phone=phone,
            is_superuser=True,
            is_staff=True,
            is_verified=True,
            is_active=True,
            is_director=True,
            is_admin=True,
            company='superuser',
            county="Nairobi"
        )

        return superuser

    def create_staff(
        self,
        full_name=None,
        email=None,
        password=None,
        phone=None,
        company=None,
        **kwargs
        ):
        """
        This is the method that creates staff in the database.
        """
        staff = self.create_user(
            full_name=full_name,
            email=email,
            password=password,
            phone=phone,
            company=company,
            is_superuser=False,
            is_staff=True,
            is_verified=True,
            is_active=True,
            is_admin=False
        )

        return staff

    def create_reseller(
        self,
        full_name=None,
        email=None,
        password=None,
        phone=None,
        company=None,
        **kwargs
    ):
        """
        This is the method that creates resellers in the database.
        """
        reseller = self.create_user(
            full_name=full_name,
            email=email,
            password=password,
            phone=phone,
            company=company,
            is_staff=True,
            is_director=True,
            is_reseller=True,
            is_admin=True,
            **kwargs

        )

        return reseller

    def create_reseller_client(
        self,
        full_name=None,
        email=None,
        password=None,
        phone=None,
        company=None,
        parent_company=None,
        **kwargs
    ):
        """
        This is the method that creates reseller clients in the database.
        """
        reseller_client = self.create_user(
            full_name=full_name,
            email=email,
            password=password,
            phone=phone,
            company=company,
            is_staff=True,
            is_director=True,
            is_admin=True,
            parent_company=parent_company,
            **kwargs
        )

        return reseller_client


class User(AbstractBaseModel, AbstractBaseUser, PermissionsMixin):
    """
    Custom user model to be used throughout the application.
    """

    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(unique=True, max_length=50)
    company = models.ForeignKey(
        "Company",
        on_delete=models.CASCADE,
        related_name="employees"
    )
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_director = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["full_name", "phone"]
    USERNAME_FIELD = "email"

    objects = UserManager()

    # this manager will now return a QuerySet of all instances that are not soft deleted.

    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):

        return self.get_username()

    @property
    def get_email(self):

        return self.email

    @property
    def get_full_name(self):
        return self.full_name

    def clean(self):
        """
        We ensure that the phone number is of the proper format before we save it.
        """

        phone = self.phone

        if not validate_phone_number(phone):
            raise ValidationError(
                {"phone": "Please enter a valid international phone number."}
            )
        return super().clean()

class AddStaffModel(models.Model):

    """Stores emails and token"""
    email = models.EmailField()
    token = models.CharField(unique=True, max_length=300)

    def __str__(self):
        return self.email

class Company(models.Model):
    name = models.CharField(unique=True, max_length=50)
    sms_count = models.IntegerField(default=5)
    email_count = models.IntegerField(default=5)
    county = models.CharField(max_length=50)
    is_reseller = models.BooleanField(default=False)
    parent = models.ForeignKey("Company", on_delete=models.SET_NULL,
        related_name="clients", null=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=AddStaffModel, dispatch_uid="create_staff_registration_token")
def send_staff_registry_email(sender, instance, **kwargs):
    subject = "Jambo SMS Staff registration link"
    message = settings.FRONTEND_LINK + instance.token.decode("utf-8")
    email_from = settings.EMAIL_HOST_USER
    receipient_list = [instance.email]
    send_mail( subject, message, email_from, receipient_list )
