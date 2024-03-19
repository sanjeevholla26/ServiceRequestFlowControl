# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Approval(models.Model):
    stage = models.IntegerField(blank=True, null=True)
    role = models.ForeignKey('Role', on_delete = models.CASCADE, blank=True, null=True)
    user = models.ForeignKey('User', on_delete = models.CASCADE, blank=True, null=True)
    template = models.ForeignKey('Template', on_delete = models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Approval'


class Assignment(models.Model):
    user = models.ForeignKey('User', on_delete = models.CASCADE, blank=True, null=True)
    role = models.ForeignKey('Role', on_delete = models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Assignment'


class Fields(models.Model):
    name = models.CharField(max_length=25, blank=True, null=True)
    type = models.CharField(max_length=25, blank=True, null=True)
    required = models.IntegerField(blank=True, null=True)
    text = models.CharField(max_length=50, blank=True, null=True)
    template = models.ForeignKey('Template', on_delete = models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Fields'


class Request(models.Model):
    user = models.ForeignKey('User', on_delete = models.CASCADE, blank=True, null=True)
    template = models.ForeignKey('Template', on_delete = models.CASCADE, blank=True, null=True)
    approval_stage = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=17, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Request'


class Requeststage(models.Model):
    request = models.ForeignKey(Request, on_delete = models.CASCADE, blank=True, null=True)
    approval = models.ForeignKey(Approval, on_delete = models.CASCADE, blank=True, null=True)
    approved = models.IntegerField(blank=True, null=True)
    approved_timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'RequestStage'


class Response(models.Model):
    answer = models.CharField(max_length=25, blank=True, null=True)
    question = models.ForeignKey(Fields, on_delete = models.CASCADE, blank=True, null=True)
    request = models.ForeignKey(Request, on_delete = models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Response'


class Role(models.Model):
    name = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Role'


class Sendback(models.Model):
    requeststage = models.ForeignKey(Requeststage, on_delete = models.CASCADE, db_column='requestStage_id', blank=True, null=True)  # Field name made lowercase.
    question = models.CharField(max_length=50, blank=True, null=True)
    response = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Sendback'


class Template(models.Model):
    user = models.ForeignKey('User', on_delete = models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Template'


from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        return self.create_user(username, password, **extra_fields)

class User(AbstractBaseUser):
    username = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=255)
    last_login = models.DateTimeField(null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin


    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        managed = False
        db_table = 'User'

