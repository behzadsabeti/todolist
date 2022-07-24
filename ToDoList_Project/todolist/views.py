from todolist.models import Task, Fav
from todolist.owner import OwnerListView, OwnerDetailView , OwnerDeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.urls import reverse_lazy
from todolist.forms import CreateForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q

class TasksListView(OwnerListView):
    model = Task
    template_name = "todolist/task_list.html"


    def get(self, request) :
        strval =  request.GET.get("search", False)
        # ad_list = Ad.objects.all()
        if strval :
            # Simple title-only search
            # objects = Post.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

            # Multi-field search
            # __icontains for case-insensitive search
            query = Q(title__icontains=strval)
            query.add(Q(text__icontains=strval), Q.OR)
            query.add(Q(tags__name__in=[strval]), Q.OR)
            task_list = Task.objects.filter(query).select_related().distinct().order_by('-updated_at')[:10]
        else :
            task_list = Task.objects.all()

        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_tasks.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['id'] for row in rows ]
        ctx = {'task_list' : task_list, 'favorites': favorites, 'search': strval}
        return render(request, self.template_name, ctx)


class TasksDetailView(OwnerDetailView):
    model = Task
    template_name = "todolist/task_detail.html"

class TasksCreateView(LoginRequiredMixin, View):
    template_name = 'todolist/task_form.html'
    success_url = reverse_lazy('todolist:all')

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        task = form.save(commit=False)
        task.owner = self.request.user
        task.save()
        form.save_m2m()
        return redirect(self.success_url)

class TasksUpdateView(LoginRequiredMixin, View):
    template_name = 'todolist/task_form.html'
    success_url = reverse_lazy('todolist:all')

    def get(self, request, pk):
        task = get_object_or_404(Task, id=pk, owner=self.request.user)
        form = CreateForm(instance=task)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        task = get_object_or_404(Task, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=Task)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        task = form.save(commit=False)
        task.save()
        form.save_m2m()

        return redirect(self.success_url)


class TasksDeleteView(OwnerDeleteView):
    model = Task

# csrf exemption in class based views
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Task, id=pk)
        fav = Fav(user=request.user, ad=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Task, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, ad=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()
