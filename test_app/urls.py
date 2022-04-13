from django.urls import path

from . import views

app_name = 'test_app'
urlpatterns = [
    path('', views.index, name='index'),
    path('read/query1', views.model1a, name='page1'),
    path('read/query1/result/', views.model1b, name='page1_result'),
    path('read/query2/', views.model2a, name='page2'),
    # path('read/query2/result/', views.model2b, name='page2_result'),
    path('write/write_triple/', views.model3a, name='page3'),
    path('write/write_triple/result/', views.model3b, name='page3_result'),
]