from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Comanda, Item, ItemComanda, Categoria


# ── HELPERS ──────────────────────────────────────────────────────────────────

def _incrementar_versao(comanda):
    """Incrementa versão e salva snapshot JSON."""
    comanda.versao += 1
    comanda.save()
    comanda.salvar_versao_json()


# ── VIEWS ─────────────────────────────────────────────────────────────────────

def index(request):
    comandas = Comanda.objects.filter(status=Comanda.STATUS_ABERTA).prefetch_related('itens')
    return render(request, 'comandas/index.html', {'comandas': comandas})


def nova_comanda(request):
    if request.method == 'POST':
        mesa    = request.POST.get('mesa', '').strip()
        cliente = request.POST.get('cliente', '').strip()
        obs     = request.POST.get('obs', '').strip()

        comanda = Comanda.objects.create(
            mesa=int(mesa) if mesa else None,
            cliente=cliente,
            obs=obs,
        )
        # Salva versão inicial no JSON
        comanda.salvar_versao_json()
        return redirect('comanda_detalhe', pk=comanda.pk)

    return render(request, 'comandas/nova_comanda.html')


def comanda_detalhe(request, pk):
    comanda = get_object_or_404(Comanda, pk=pk)
    categorias = Categoria.objects.prefetch_related('itens').all()
    itens_disponiveis = Item.objects.filter(disponivel=True).select_related('categoria')
    return render(request, 'comandas/comanda_detalhe.html', {
        'comanda': comanda,
        'categorias': categorias,
        'itens_disponiveis': itens_disponiveis,
    })


@require_POST
def adicionar_item(request, pk):
    comanda = get_object_or_404(Comanda, pk=pk, status=Comanda.STATUS_ABERTA)
    item    = get_object_or_404(Item, pk=request.POST.get('item_id'))
    qtd     = int(request.POST.get('quantidade', 1))
    obs     = request.POST.get('obs', '')

    ic, criado = ItemComanda.objects.get_or_create(
        comanda=comanda, item=item, obs=obs,
        defaults={'quantidade': qtd}
    )
    if not criado:
        ic.quantidade += qtd
        ic.save()

    _incrementar_versao(comanda)
    return render(request, 'comandas/partials/lista_itens.html', {'comanda': comanda})


@require_POST
def remover_item(request, pk, item_comanda_id):
    comanda = get_object_or_404(Comanda, pk=pk, status=Comanda.STATUS_ABERTA)
    get_object_or_404(ItemComanda, pk=item_comanda_id, comanda=comanda).delete()
    _incrementar_versao(comanda)
    return render(request, 'comandas/partials/lista_itens.html', {'comanda': comanda})


@require_POST
def salvar_obs(request, pk):
    """Atualiza observações gerais da comanda via HTMX."""
    comanda = get_object_or_404(Comanda, pk=pk, status=Comanda.STATUS_ABERTA)
    comanda.obs = request.POST.get('obs', '').strip()
    comanda.save()
    return render(request, 'comandas/partials/obs_salva.html', {'comanda': comanda})


@require_POST
def fechar_comanda(request, pk):
    comanda = get_object_or_404(Comanda, pk=pk, status=Comanda.STATUS_ABERTA)
    if not comanda.itens.exists():
        return render(request, 'comandas/partials/lista_itens.html', {
            'comanda': comanda,
            'erro': 'Adicione pelo menos um item antes de fechar.'
        })
    comanda.status    = Comanda.STATUS_FECHADA
    comanda.fechada_em = timezone.now()
    comanda.save()
    comanda.salvar_versao_json()
    return redirect('index')


def imprimir_comanda(request, pk):
    comanda = get_object_or_404(Comanda, pk=pk)
    return render(request, 'comandas/imprimir.html', {'comanda': comanda})


def historico(request):
    comandas = Comanda.objects.filter(status=Comanda.STATUS_FECHADA).prefetch_related('itens')
    return render(request, 'comandas/historico.html', {'comandas': comandas})
