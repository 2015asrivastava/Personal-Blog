from django.conf.urls import url
from My_Blog import views
urlpatterns = [
    url(r'^$', views.post_list, name="post_list"),
    url(r'^create/$',views.post_create,name="post_create"),
    url(r'^category_create/$',views.category_create,name="category_create"),
    url(r'^category/$', views.category_list, name="category_list"),
    url(r'^category/(?P<slug>[\w-]+)/$',views.category_detail,name="category_detail"),
    url(r'^(?P<slug>[\w-]+)/$',views.post_detail,name="post_detail"),
    url(r'^(?P<slug>[\w-]+)/edit/$',views.post_update,name="post_update"),
    url(r'^(?P<slug>[\w-]+)/delete/$',views.post_delete,name="post_delete"),

]
