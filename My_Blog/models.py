from __future__ import unicode_literals
from django.template.defaultfilters import slugify
from django.db import models
from django.db.models.signals import pre_save
from django.core.urlresolvers import reverse
from django.conf import settings
from markdown_deux import  markdown
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
def upload_loction(intance,filename):
    return "%s/%s"%(intance.id,filename)
class PostCategory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    title = models.CharField(max_length=120)
    slug = models.SlugField()
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    image = models.ImageField(upload_to=upload_loction,
                              null=True,
                              blank=True,
                              width_field="width_field",
                              height_field="height_field")
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    content = models.TextField(null=True,blank=True)
    def save(self,*args,**kwargs):
        # Uncomment if you don't want the slug to change every time the name changes
        # if self.id is None:
        # self.slug = slugify(self.name)
        self.slug=slugify(self.title)
        super(PostCategory,self).save(*args,**kwargs)
    def get_absolute_urls(self):
        return reverse("posts:category_detail",kwargs={"slug":self.slug})

    def __str__(self):
        return self.title

    def get_markdown(self):
        content = self.content
        markdown_text = markdown(content)
        return mark_safe(markdown_text)


class Post(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,default=1)
    category = models.ForeignKey(PostCategory, on_delete=models.CASCADE,null=True)
    title=models.CharField(max_length=120)
    slug=models.SlugField(unique=True)
    draft=models.BooleanField(default=False)
    publish=models.DateField()
    image=models.ImageField(upload_to=upload_loction,
          null=True,
          blank=True,
          width_field="width_field",
          height_field="height_field")
    height_field=models.IntegerField(default=0)
    width_field=models.IntegerField(default=0)
    content=models.TextField()
    updated=models.DateTimeField(auto_now=True,auto_now_add=False)
    timestamp=models.DateTimeField(auto_now=False,auto_now_add=True)

    def __str__(self):
        return self.title
    def get_absolute_urls(self):
        return reverse("posts:post_detail",kwargs={"slug":self.slug})

    class Meta:
       ordering=["-timestamp","-updated"]

    def get_markdown(self):
        content=self.content
        markdown_text=markdown(content)
        return mark_safe(markdown_text)

def create_slug(instance,new_slug=None):
    slug=slugify(instance.title)
    if new_slug is not None:
        slug=new_slug
    qs=Post.objects.filter(slug=slug).order_by("-id")
    exists=qs.exists()
    if exists:
        new_slug="%s-%s" %(slug,qs.first().id)
        return create_slug(instance,new_slug=new_slug)
    return slug

def pre_save_post_receiver(sender,instance,*args,**kwargs):
    if not instance.slug:
        instance.slug=create_slug(instance)

pre_save.connect(pre_save_post_receiver,sender=Post)

