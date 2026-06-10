from django.contrib import admin
from .models import Categoria, Item, Comanda, ItemComanda


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'preco', 'disponivel']
    list_filter = ['categoria', 'disponivel']
    list_editable = ['preco', 'disponivel']
    prepopulated_fields = {'slug': ('nome',)}


class ItemComandaInline(admin.TabularInline):
    model = ItemComanda
    extra = 0


@admin.register(Comanda)
class ComandaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'id_comanda', 'mesa', 'cliente', 'versao', 'status', 'total', 'criada_em']
    list_filter = ['status']
    inlines = [ItemComandaInline]
    readonly_fields = ['numero', 'id_comanda', 'versao', 'criada_em', 'fechada_em']
