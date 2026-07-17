from django.db import migrations, models
from django.db.models import Max


def preencher_precos_historicos(apps, schema_editor):
    ItemComanda = apps.get_model('comandas', 'ItemComanda')
    for item_comanda in ItemComanda.objects.select_related('item').iterator():
        item_comanda.preco_unitario = item_comanda.item.preco
        item_comanda.save(update_fields=['preco_unitario'])


def preencher_sequencias_diarias(apps, schema_editor):
    Comanda = apps.get_model('comandas', 'Comanda')
    SequenciaDiaria = apps.get_model('comandas', 'SequenciaDiaria')
    maiores_numeros = (
        Comanda.objects.values('criada_em__date')
        .annotate(ultimo_numero=Max('numero'))
    )
    for sequencia in maiores_numeros:
        SequenciaDiaria.objects.update_or_create(
            data=sequencia['criada_em__date'],
            defaults={'ultimo_numero': sequencia['ultimo_numero']},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('comandas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SequenciaDiaria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(unique=True)),
                ('ultimo_numero', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.RunPython(preencher_sequencias_diarias, migrations.RunPython.noop),
        migrations.AddField(
            model_name='itemcomanda',
            name='preco_unitario',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.RunPython(preencher_precos_historicos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='itemcomanda',
            name='preco_unitario',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
    ]
