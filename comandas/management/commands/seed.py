from django.core.management.base import BaseCommand
from comandas.models import Categoria, Item

CARDAPIO = {
    "Prato do Dia": [
        ("Bife acebolado",        "30.00", "bife-acebolado"),
        ("Estrogonofe de frango", "30.00", "estrogonofe-de-frango"),
        ("Virado a paulista",     "30.00", "virado-a-paulista"),
        ("Parmegiana de carne",   "30.00", "parmegiana-de-carne"),
        ("Parmegiana de frango",  "30.00", "parmegiana-de-frango"),
    ],
    "Bebidas": [
        ("Agua mineral",      "4.00",  "agua-mineral"),
        ("Refrigerante lata", "6.00",  "refrigerante-lata"),
        ("Suco natural",      "10.00", "suco-natural"),
    ],
    "Extras": [
        ("Arroz",  "5.00", "arroz"),
        ("Feijao", "4.00", "feijao"),
        ("Salada", "5.00", "salada"),
    ],
}


class Command(BaseCommand):
    help = "Popula o banco com o cardapio inicial"

    def handle(self, *args, **kwargs):
        criados = 0
        for cat_nome, itens in CARDAPIO.items():
            cat, _ = Categoria.objects.get_or_create(nome=cat_nome)
            for nome, preco, slug in itens:
                _, novo = Item.objects.get_or_create(
                    slug=slug,
                    defaults={"nome": nome, "preco": preco, "categoria": cat}
                )
                if novo:
                    criados += 1
                    self.stdout.write(f"  + {nome}")
        self.stdout.write(self.style.SUCCESS(f"\n{criados} itens criados."))
