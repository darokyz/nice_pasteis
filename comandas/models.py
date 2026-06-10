from django.db import models
from django.utils.text import slugify
from django.utils import timezone


def gerar_numero_dia():
    """Retorna o próximo número sequencial do dia."""
    hoje = timezone.localdate()
    count = Comanda.objects.filter(criada_em__date=hoje).count()
    return count + 1


def gerar_id_comanda(numero, data=None):
    """Gera ID no formato AAAAMMDD-NNN (ex: 20260609-001)."""
    if data is None:
        data = timezone.localdate()
    return f"{data.strftime('%Y%m%d')}-{numero:03d}"


class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Item(models.Model):
    nome = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='itens'
    )
    disponivel = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Itens'
        ordering = ['categoria', 'nome']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nome} — R$ {self.preco}'


class Comanda(models.Model):
    STATUS_ABERTA = 'aberta'
    STATUS_FECHADA = 'fechada'
    STATUS_CHOICES = [
        (STATUS_ABERTA, 'Aberta'),
        (STATUS_FECHADA, 'Fechada'),
    ]

    # Identificação
    numero      = models.PositiveIntegerField()                          # sequencial do dia
    id_comanda  = models.CharField(max_length=20, unique=True, blank=True)  # 20260609-001
    mesa        = models.PositiveIntegerField(null=True, blank=True)
    cliente     = models.CharField(max_length=200, blank=True)
    obs         = models.TextField(blank=True, help_text='Observações gerais da comanda')

    # Controle
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ABERTA)
    versao      = models.PositiveIntegerField(default=1)
    criada_em   = models.DateTimeField(auto_now_add=True)
    fechada_em  = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Comanda'
        verbose_name_plural = 'Comandas'
        ordering = ['-criada_em']

    def __str__(self):
        return f'Comanda #{self.numero} ({self.id_comanda}) — {self.get_status_display()}'

    def save(self, *args, **kwargs):
        if not self.pk:  # nova comanda
            self.numero = gerar_numero_dia()
            self.id_comanda = gerar_id_comanda(self.numero)
        super().save(*args, **kwargs)

    @property
    def total(self):
        return sum(ic.subtotal for ic in self.itens.all())

    def snapshot_itens(self):
        return [
            {
                'item': ic.item.nome,
                'quantidade': ic.quantidade,
                'preco_unitario': str(ic.item.preco),
                'subtotal': str(ic.subtotal),
                'obs': ic.obs,
            }
            for ic in self.itens.all()
        ]

    def salvar_versao_json(self):
        """Acumula versões no mesmo arquivo JSON da comanda."""
        import json, os

        path = f'historico/{self.id_comanda}.json'
        os.makedirs('historico', exist_ok=True)

        # Carrega versões existentes
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
        else:
            dados = {
                'id_comanda': self.id_comanda,
                'numero': self.numero,
                'mesa': self.mesa,
                'cliente': self.cliente,
                'versoes': [],
            }

        # Atualiza metadados e appenda nova versão
        dados['mesa'] = self.mesa
        dados['cliente'] = self.cliente
        dados['obs'] = self.obs
        dados['versao_atual'] = self.versao
        dados['status'] = self.status
        dados['versoes'].append({
            'versao': self.versao,
            'timestamp': timezone.now().isoformat(),
            'total': str(self.total),
            'itens': self.snapshot_itens(),
        })

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)


class ItemComanda(models.Model):
    comanda     = models.ForeignKey(Comanda, on_delete=models.CASCADE, related_name='itens')
    item        = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantidade  = models.PositiveIntegerField(default=1)
    obs         = models.CharField(max_length=300, blank=True, help_text='Ex: sem cebola, mal passado')

    class Meta:
        verbose_name = 'Item da Comanda'
        verbose_name_plural = 'Itens da Comanda'

    def __str__(self):
        return f'{self.quantidade}x {self.item.nome}'

    @property
    def subtotal(self):
        return self.item.preco * self.quantidade
