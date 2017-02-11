from django import forms
from .models import Post,PostCategory
from pagedown.widgets import PagedownWidget
class PostForm(forms.ModelForm):
    content=forms.CharField(widget=PagedownWidget)
    publish=forms.DateField(widget=forms.SelectDateWidget)
    category=forms.Select()
    class Meta:
        model=Post
        fields=[
         "category",
        "title",
        "content",
         "image",
           "draft",
            "publish"
         ]

class CategoryForm(forms.ModelForm):
    content=forms.CharField(widget=PagedownWidget)
    class Meta:
        model=PostCategory
        fields=[
            "title",
            "content",
            "image",
        ]