from __future__ import unicode_literals

from struct import pack

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
class Comment(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,default=1)
    content_type=models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id=models.PositiveIntegerField()
    content_object=GenericForeignKey('content_type','object_id')
    parent=models.ForeignKey("self",null=True,blank=True)

    content=models.TextField()
    timestamp=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=["-timestamp"]


    def __unicode__(self):
        return self.user.username

    def children(self):
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True

