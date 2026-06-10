from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('nova/', views.nova_comanda, name='nova_comanda'),
    path('historico/', views.historico, name='historico'),
    path('<int:pk>/', views.comanda_detalhe, name='comanda_detalhe'),
    path('<int:pk>/adicionar/', views.adicionar_item, name='adicionar_item'),
    path('<int:pk>/remover/<int:item_comanda_id>/', views.remover_item, name='remover_item'),
    path('<int:pk>/obs/', views.salvar_obs, name='salvar_obs'),
    path('<int:pk>/fechar/', views.fechar_comanda, name='fechar_comanda'),
    path('<int:pk>/imprimir/', views.imprimir_comanda, name='imprimir_comanda'),
]
