from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import connection


def is_staff(user):
    return user.is_staff


def dict_fetchall(cursor):
    """Retorna todas as linhas como lista de dicts."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# ── QUERIES FIXAS ─────────────────────────────────────────────────────────────

def _vendas_por_dia(dias=30):
    sql = """
        SELECT
            DATE(c.fechada_em) AS dia,
            COUNT(DISTINCT c.id)            AS comandas,
            SUM(ic.quantidade * ic.preco_unitario) AS total
        FROM comandas_comanda c
        JOIN comandas_itemcomanda ic ON ic.comanda_id = c.id
        JOIN comandas_item i ON i.id = ic.item_id
        WHERE c.status = 'fechada'
          AND c.fechada_em >= DATE('now', :offset)
        GROUP BY DATE(c.fechada_em)
        ORDER BY dia DESC
    """
    with connection.cursor() as cur:
        cur.execute(sql, {'offset': f'-{dias} days'})
        return dict_fetchall(cur)


def _itens_mais_vendidos(dias=30):
    sql = """
        SELECT
            i.nome                          AS item,
            cat.nome                        AS categoria,
            SUM(ic.quantidade)              AS quantidade,
            SUM(ic.quantidade * ic.preco_unitario) AS total
        FROM comandas_itemcomanda ic
        JOIN comandas_item i ON i.id = ic.item_id
        LEFT JOIN comandas_categoria cat ON cat.id = i.categoria_id
        JOIN comandas_comanda c ON c.id = ic.comanda_id
        WHERE c.status = 'fechada'
          AND c.fechada_em >= DATE('now', :offset)
        GROUP BY ic.item_id
        ORDER BY quantidade DESC
        LIMIT 20
    """
    with connection.cursor() as cur:
        cur.execute(sql, {'offset': f'-{dias} days'})
        return dict_fetchall(cur)


def _ticket_medio(dias=30):
    sql = """
        SELECT
            ROUND(AVG(total_comanda), 2) AS ticket_medio,
            MIN(total_comanda)           AS menor,
            MAX(total_comanda)           AS maior,
            COUNT(*)                     AS total_comandas
        FROM (
            SELECT
                c.id,
                SUM(ic.quantidade * ic.preco_unitario) AS total_comanda
            FROM comandas_comanda c
            JOIN comandas_itemcomanda ic ON ic.comanda_id = c.id
            JOIN comandas_item i ON i.id = ic.item_id
            WHERE c.status = 'fechada'
              AND c.fechada_em >= DATE('now', :offset)
            GROUP BY c.id
        )
    """
    with connection.cursor() as cur:
        cur.execute(sql, {'offset': f'-{dias} days'})
        return dict_fetchall(cur)


def _pico_por_hora(dias=30):
    # O cursor do Django usa interpolação de parâmetros; %% resulta em % no SQLite.
    sql = """
        SELECT
            strftime('%%H:00', c.criada_em) AS hora,
            COUNT(*) AS comandas
        FROM comandas_comanda c
        WHERE c.status = 'fechada'
          AND c.fechada_em >= DATE('now', :offset)
        GROUP BY strftime('%%H', c.criada_em)
        ORDER BY hora
    """
    with connection.cursor() as cur:
        cur.execute(sql, {'offset': f'-{dias} days'})
        return dict_fetchall(cur)


# ── VIEWS ─────────────────────────────────────────────────────────────────────

@login_required
@user_passes_test(is_staff)
def dashboard(request):
    try:
        dias = int(request.GET.get('dias', 30))
    except (TypeError, ValueError):
        dias = 30
    dias = dias if dias in {7, 30, 90} else 30

    context = {
        'dias': dias,
        'vendas_por_dia':      _vendas_por_dia(dias),
        'itens_mais_vendidos': _itens_mais_vendidos(dias),
        'ticket_medio':        _ticket_medio(dias),
        'pico_por_hora':       _pico_por_hora(dias),
    }
    return render(request, 'analytics/dashboard.html', context)
