from django.db import models
from django.contrib.auth.models import AbstractUser
from app.settings import MEDIA_URL, STATIC_URL
from django.forms import model_to_dict

# Create your models here.

class User(AbstractUser):
    image = models.ImageField(upload_to='users/%Y/%m/%d',null=True, blank=True)
    SAP_Code = models.CharField(max_length=150)
    UserType = models.IntegerField(null=True)
    is_head_of_area = models.BooleanField(default=False, null=True, blank=True)
    departamento = models.CharField(max_length=150, null=True, blank=True)

    def get_image(self):
        if self.image:
            return '{}{}'.format(MEDIA_URL, self.image)
        return '{}{}'.format(STATIC_URL, 'base/img/user.png')
    
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['password', 'user_permissions', 'last_login'])
        if self.last_login:
            item['last_login'] = self.last_login.strftime('%Y-%m-%d  %H:%M:%S')
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['image'] = self.get_image()
        item['groups'] = [{'id':g.id, 'name':g.name}for g in self.groups.all()]
        return item
    

     