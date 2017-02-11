from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse,HttpResponseRedirect,Http404
from  My_Blog.models import Post,PostCategory
from .forms import PostForm,CategoryForm
from  django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from comments.forms import CommentForm
from comments.models import Comment


# Create your views here.

def post_create(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        raise Http404
    form=PostForm(request.POST or None,request.FILES or None)
    if form.is_valid():
        instance=form.save(commit=False)
        instance.user=request.user
        instance.save()

        return HttpResponseRedirect(instance.get_absolute_urls())
    context={
        "form":form
    }
    return render(request,"post_create.html",context)

def post_detail(request,slug=None):
    posts=Post.objects.order_by("-timestamp")[:5]
    categories=PostCategory.objects.all()
    instance=get_object_or_404(Post,slug=slug)
    if instance.draft or instance.publish > timezone.now().date():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    content_type = ContentType.objects.get_for_model(Post)
    obj_id = instance.id
    parent_obj=None

    initial_data={
        "content_type": content_type,
        "object_id": instance.id,
    }
    form=CommentForm(request.POST or None,initial=initial_data)
    if form.is_valid() and request.user.is_authenticated():
        c_type=form.cleaned_data.get("content_type")

        content_type=ContentType.objects.get(model=c_type)
        obj_id1=form.cleaned_data.get('object_id')
        content_data=form.cleaned_data.get("content")
        parent_obj=None
        try:
            parent_id=request.POST.get("parent_id")
        except:
            parent_id=None
        if parent_id:
            parent_qs=Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count()==1:
                parent_obj=parent_qs.first()
        new_comment,created= Comment.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj_id1,
            content=content_data,
            parent=parent_obj,
        )
        return HttpResponseRedirect(new_comment.content_object.get_absolute_urls())

    #Giving all the comments related to  a particular post
    comments = Comment.objects.filter(content_type=content_type, object_id=obj_id).filter(parent=None)

    context={
        "title":instance.title,
        "instance":instance,
        "comments":comments,
        "comment_form":form,
        "posts":posts,
        "categories":categories,

    }
    return render(request,"post_detail.html",context)



def post_list(request):
    today=timezone.now().date()
    no_search=None
    posts = Post.objects.order_by("-timestamp")[:5]
    categories = PostCategory.objects.all()
    queryset_list=Post.objects.filter(draft=False).filter(publish__lte=timezone.now())
    if request.user.is_staff or request.user.is_superuser:
       queryset_list=Post.objects.all()
    query=request.GET.get("q")
    if query:
        queryset_list=queryset_list.filter(Q(title__icontains=query)|
                                           Q(content__icontains=query)|
                                           Q(user__first_name__icontains=query)|
                                           Q(user__last_name__icontains=query)
                                           ).distinct()
        if (queryset_list.count() == 0):
            no_search = "Sorry! No content matches your criteria.Please try some different keywords"

    paginator=Paginator(queryset_list,6)
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    context={
        "object_list":queryset,
        "today":today,
        "posts": posts,
        "categories": categories,
        "no_search":no_search,
    }
    return render(request,"post_list.html",context)

def post_update(request,slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None,request.FILES or None,instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Post successfully updated")
        return HttpResponseRedirect(instance.get_absolute_urls())
    context = {
        "form":form,
        "instance":instance.title,
    }
    return render(request, "post_create.html", context)

def post_delete(request,slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    instance.delete()
    messages.success(request, "Post successfully deleted")
    return redirect("posts:post_list")

def category_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form = CategoryForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, "Category successfully added")
        return HttpResponseRedirect("/category")
    context = {
        "form": form
    }
    return render(request, "category_create.html", context)

def category_list(request):
    category=PostCategory.objects.all()
    paginator = Paginator(category, 6)
    page = request.GET.get('page')
    header="Choose Category"
    try:
        category = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        category = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        category = paginator.page(paginator.num_pages)
    context_dict={

        "object_list":category,
        "header":header,
    }
    return render(request, "post_list.html", context_dict)

def category_detail(request,slug=None):
    category_listing=get_object_or_404(PostCategory,slug=slug)
    title=category_listing.title
    category_listslug=category_listing.post_set.all()
    paginator = Paginator(category_listslug, 6)
    page = request.GET.get('page')
    try:
        category_listslug = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        category_listslug = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        category_listslug = paginator.page(paginator.num_pages)
    context_dict={
        "object_list":category_listslug,
         "title":title,

    }
    return render(request, "post_list.html", context_dict)