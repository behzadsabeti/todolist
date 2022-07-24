from django.urls import path, reverse_lazy
from . import views

app_name='todolist'
urlpatterns = [
    path('', views.TasksListView.as_view(), name='all'),
    path('task/<int:pk>', views.TasksDetailView.as_view(), name='task_detail'),
    path('task/create',
        views.TasksCreateView.as_view(success_url=reverse_lazy('todolist:all')), name='task_create'),
    path('task/<int:pk>/update',
        views.TasksUpdateView.as_view(success_url=reverse_lazy('todolist:all')), name='task_update'),
    path('task/<int:pk>/delete',
        views.TasksDeleteView.as_view(success_url=reverse_lazy('todolist:all')), name='task_delete'),

    path('task/<int:pk>/favorite',
        views.AddFavoriteView.as_view(), name='task_favorite'),
    path('task/<int:pk>/unfavorite',
        views.DeleteFavoriteView.as_view(), name='task_unfavorite'),
]
