"""Datos simulados de la demo. Todo es ficticio y determinista.

La tienda, los productos y las personas son inventados: los nombres de las
embajadoras son un guiño a la serie The Office. Los pedidos se generan con una
semilla fija, así que cada corrida del generador produce las mismas páginas.
"""
import random
from collections import Counter
from datetime import date, timedelta

HOY = date(2026, 11, 15)
TIENDA = "Papelera Scranton"
DOMINIO = "papelerascranton.example"
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def fecha(d):
    return f"{d.day:02d}-{MESES[d.month - 1]}-{d.year}"


def ddmm(d):
    return f"{d.day:02d}/{d.month:02d}"


# ── Grupos del dashboard: un grupo por tipo de contrato, más las ventas sin código ──

GRUPOS = [
    dict(key="vip", nombre="Gerencia VIP", emoji="🏆"),
    dict(key="ven", nombre="Fuerza de Ventas", emoji="💙"),
    dict(key="com", nombre="Comité de Fiestas", emoji="🎉"),
    dict(key="sin", nombre="Sin código", emoji="⬜"),
]
GRUPO = {g["key"]: g for g in GRUPOS}
GRUPOS_TIPO = [g for g in GRUPOS if g["key"] != "sin"]

TIPOS = [
    dict(id=1, grupo="vip", nombre="Gerencia VIP", comision=15, base="Valor neto", alcance=True, bonus=True, activo=True,
         desc="Líderes de comunidad. La comisión más alta, premios por alcance y bonus x2 en sus primeros 5 referidos."),
    dict(id=2, grupo="ven", nombre="Fuerza de Ventas", comision=10, base="Valor neto", alcance=False, bonus=True, activo=True,
         desc="Embajadores enfocados en la venta directa con su código. Bonus x1,5 en sus primeros 3 referidos."),
    dict(id=3, grupo="com", nombre="Comité de Fiestas", comision=8, base="Valor bruto", alcance=True, bonus=False, activo=True,
         desc="Creadoras de contenido y anfitrionas de eventos. Suman coins por el alcance de lo que publican."),
    dict(id=4, grupo=None, nombre="Practicante", comision=5, base="Valor bruto", alcance=False, bonus=False, activo=False,
         desc="Contrato de prueba de 60 días. Se reemplazó por Fuerza de Ventas."),
]
TIPO = {t["grupo"]: t for t in TIPOS if t["grupo"]}

# ── Embajadoras ──────────────────────────────────────────────────────────────
# (id, código, nombre, grupo, cumpleaños, ventas por semana aprox., inicio del contrato)

_BASE = [
    (1, "MICHAEL", "Michael Scott", "vip", "15-mar", 9, date(2026, 1, 5)),
    (2, "DWIGHT", "Dwight Schrute", "vip", "20-ene", 14, date(2026, 1, 5)),
    (3, "JIM", "Jim Halpert", "ven", "01-oct", 11, date(2026, 2, 2)),
    (4, "PAM", "Pam Beesly", "com", "25-mar", 8, date(2026, 4, 1)),
    (5, "ANGELA", "Angela Martin", "com", "25-jun", 4, date(2026, 3, 2)),
    (6, "KEVIN", "Kevin Malone", "ven", "01-jun", 3, date(2026, 5, 4)),
    (7, "OSCAR", "Oscar Martínez", "ven", "08-mar", 5, date(2026, 3, 2)),
    (8, "STANLEY", "Stanley Hudson", "ven", "19-feb", 6, date(2026, 2, 2)),
    (9, "PHYLLIS", "Phyllis Vance", "com", "10-jul", 5, date(2026, 3, 2)),
    (10, "ANDY", "Andy Bernard", "ven", "24-ene", 7, date(2026, 6, 1)),
    (11, "KELLY", "Kelly Kapoor", "vip", "05-feb", 12, date(2026, 2, 2)),
    (12, "RYAN", "Ryan Howard", None, "05-may", 0, date(2026, 7, 1)),
    (13, "ERIN", "Erin Hannon", "com", "01-may", 4, date(2026, 11, 2)),
    (14, "DARRYL", "Darryl Philbin", "ven", "25-oct", 6, date(2026, 4, 1)),
    (15, "TOBY", "Toby Flenderson", None, "22-feb", 0, date(2026, 1, 5)),
    (16, "CREED", "Creed Bratton", None, "08-feb", 0, date(2026, 1, 5)),
    (17, "MEREDITH", "Meredith Palmer", "com", "12-nov", 3, date(2026, 10, 1)),
    (18, "JAN", "Jan Levinson", "vip", "11-may", 7, date(2026, 5, 4)),
]
# Coins que les quedaron a quienes ya no tienen contrato vigente.
_SALDO_FUERA = {"RYAN": 3200, "TOBY": 450, "CREED": 12800}
_FIN_FUERA = {"RYAN": date(2026, 9, 30), "TOBY": date(2026, 6, 30), "CREED": date(2026, 8, 31)}


def _iniciales(nombre):
    return "".join(p[0] for p in nombre.split()[:2]).upper()


def _historial(cod, grupo, inicio):
    """Contratos de la embajadora, del más nuevo al más antiguo."""
    if grupo is None:
        return [dict(tipo="Practicante", inicio=inicio, fin=_FIN_FUERA[cod], estado="Finalizado",
                     nota="Terminó el período de prueba y no se renovó.")]
    actual = dict(tipo=GRUPO[grupo]["nombre"], inicio=inicio, fin=inicio.replace(year=inicio.year + 1) - timedelta(days=1),
                  estado="Vigente", nota="")
    if cod in ("PAM", "JIM", "KELLY"):
        previo = dict(tipo="Practicante", inicio=inicio - timedelta(days=60), fin=inicio - timedelta(days=1),
                      estado="Finalizado", nota="Pasó la prueba: se le asignó un contrato nuevo.")
        return [actual, previo]
    return [actual]


EMBAJADORAS = []
for _id, _cod, _nom, _grp, _cumple, _peso, _ini in _BASE:
    _hist = _historial(_cod, _grp, _ini)
    EMBAJADORAS.append(dict(
        id=_id, codigo=_cod, nombre=_nom, grupo=_grp, cumple=_cumple, peso=_peso,
        iniciales=_iniciales(_nom),
        instagram=f"@{_cod.lower()}.scranton",
        correo=f"{_cod.lower()}@{DOMINIO}",
        telefono=f"+1 570 555 01{_id:02d}",
        direccion=f"{1700 + _id * 3} Slough Avenue, Scranton",
        historial=_hist, contrato=_hist[0],
        link_descuento=f"https://{DOMINIO}/discount/{_cod}",
        link_referido=f"https://{DOMINIO}/?ref={_cod.lower()}",
    ))
EMB = {e["codigo"]: e for e in EMBAJADORAS}

# ── Productos de la tienda ───────────────────────────────────────────────────

PRODUCTOS = [
    ("Resma papel carta 500 hojas", 5990, 10),
    ("Caja 10 resmas papel oficio", 49990, 3),
    ("Cuadernos premium pack x3", 12990, 6),
    ("Taza «Mejor Jefe del Mundo»", 9990, 7),
    ("Velas aromáticas Serenity", 14990, 5),
    ("Remolachas orgánicas 1 kg", 3990, 4),
    ("Tetera de cerámica", 24990, 3),
    ("Agenda 2027 tapa dura", 11990, 6),
    ("Set lápices de dibujo x12", 7990, 5),
    ("Engrapadora metálica", 8990, 4),
]

# ── Pedidos simulados de los últimos 90 días ─────────────────────────────────


def _poisson(rnd, media):
    limite, k, p = pow(2.718281828, -media), 0, 1.0
    while True:
        p *= rnd.random()
        if p <= limite:
            return k
        k += 1


def _pedido(rnd, dia, codigo, grupo):
    items = rnd.choices(PRODUCTOS, weights=[p[2] for p in PRODUCTOS], k=rnd.choice([1, 1, 2, 2, 3]))
    monto = sum(p[1] * rnd.choice([1, 1, 1, 2]) for p in items)
    return dict(fecha=dia, codigo=codigo, grupo=grupo, monto=monto, productos=[p[0] for p in items])


def _generar_pedidos():
    rnd = random.Random(2026)
    pedidos = []
    for atras in range(89, -1, -1):
        dia = HOY - timedelta(days=atras)
        ritmo = (0.7 if dia.weekday() >= 5 else 1.1) * (0.75 + 0.5 * (89 - atras) / 89)
        for e in EMBAJADORAS:
            if e["grupo"] and dia >= e["contrato"]["inicio"]:
                for _ in range(_poisson(rnd, e["peso"] / 7 * ritmo)):
                    pedidos.append(_pedido(rnd, dia, e["codigo"], e["grupo"]))
        for _ in range(_poisson(rnd, 5.5 * ritmo)):
            pedidos.append(_pedido(rnd, dia, None, "sin"))
    return pedidos


PEDIDOS = _generar_pedidos()
PERIODOS = [15, 30, 45, 90]


def _lunes(d):
    return d - timedelta(days=d.weekday())


def resumen(dias):
    """Lo que muestra el dashboard para un período: totales, semanas, ranking y productos."""
    desde = HOY - timedelta(days=dias)
    peds = [p for p in PEDIDOS if p["fecha"] >= desde]
    claves = [g["key"] for g in GRUPOS]
    monto = {k: 0 for k in claves}
    cuenta = {k: 0 for k in claves}
    semanas = {}
    lun = _lunes(desde)
    while lun <= HOY:
        semanas[lun] = dict(lunes=lun, m={k: 0 for k in claves}, n={k: 0 for k in claves})
        lun += timedelta(days=7)
    ranking = {}
    productos = Counter()
    for p in peds:
        g = p["grupo"]
        monto[g] += p["monto"]
        cuenta[g] += 1
        s = semanas[_lunes(p["fecha"])]
        s["m"][g] += p["monto"]
        s["n"][g] += 1
        if p["codigo"]:
            r = ranking.setdefault(p["codigo"], dict(codigo=p["codigo"], grupo=g, ventas=0, referidos=0))
            r["ventas"] += p["monto"]
            r["referidos"] += 1
        productos.update(p["productos"])
    return dict(
        dias=dias, desde=desde, hasta=HOY, monto=monto, cuenta=cuenta,
        semanas=list(semanas.values()),
        ranking=sorted(ranking.values(), key=lambda r: -r["ventas"]),
        productos=productos.most_common(8),
    )


RESUMEN = {d: resumen(d) for d in PERIODOS}

# ── Coins: comisión de las ventas más los premios ────────────────────────────

PREMIOS = [
    dict(id="P-021", fecha=date(2026, 11, 12), codigo="KELLY", coins=15000, categoria="Ganador Reel", motivo="Dundie al reel más visto de octubre"),
    dict(id="P-020", fecha=date(2026, 11, 10), codigo="DWIGHT", coins=20000, categoria="Otras Actividades", motivo="Vendedor del mes"),
    dict(id="P-019", fecha=date(2026, 11, 5), codigo="PAM", coins=10000, categoria="Ganador Reel", motivo="Mejor unboxing ilustrado"),
    dict(id="P-018", fecha=date(2026, 11, 2), codigo="ERIN", coins=5000, categoria="Inicio Embajadora", motivo="Bono de bienvenida"),
    dict(id="P-017", fecha=date(2026, 10, 28), codigo="JIM", coins=8000, categoria="Otras Actividades", motivo="Campaña «Resmas con sorpresa»"),
    dict(id="P-016", fecha=date(2026, 10, 20), codigo="MICHAEL", coins=12000, categoria="Otras Actividades", motivo="Anfitrión de los Dundies 2026"),
    dict(id="P-015", fecha=date(2026, 10, 15), codigo="ANDY", coins=6000, categoria="Ganador Reel", motivo="Reel a capela del catálogo"),
    dict(id="P-014", fecha=date(2026, 10, 9), codigo="STANLEY", coins=4000, categoria="Otras Actividades", motivo="Récord de ventas en el Día del Pretzel"),
    dict(id="P-013", fecha=date(2026, 10, 1), codigo="MEREDITH", coins=5000, categoria="Inicio Embajadora", motivo="Bono de bienvenida"),
    dict(id="P-012", fecha=date(2026, 9, 24), codigo="ANGELA", coins=7000, categoria="Otras Actividades", motivo="Organización de la fiesta de fin de trimestre"),
]
CATEGORIAS_PREMIO = ["Inicio Embajadora", "Ganador Reel", "Otras Actividades"]

_r90 = {r["codigo"]: r for r in RESUMEN[90]["ranking"]}
_r45 = {r["codigo"]: r for r in RESUMEN[45]["ranking"]}
for e in EMBAJADORAS:
    cod = e["codigo"]
    e["premios"] = [p for p in PREMIOS if p["codigo"] == cod]
    e["ventas45"] = _r45.get(cod, {}).get("ventas", 0)
    e["referidos45"] = _r45.get(cod, {}).get("referidos", 0)
    if e["grupo"]:
        comision = _r90.get(cod, {}).get("ventas", 0) * TIPO[e["grupo"]]["comision"] / 100
        e["coins"] = int(round(comision / 10) * 10) + sum(p["coins"] for p in e["premios"])
    else:
        e["coins"] = _SALDO_FUERA[cod]
    # Ventas por semana de los últimos 45 días, para el gráfico de su ficha.
    e["semanas45"] = [
        (s["lunes"], sum(p["monto"] for p in PEDIDOS
                         if p["codigo"] == cod and s["lunes"] <= p["fecha"] < s["lunes"] + timedelta(days=7)
                         and p["fecha"] >= RESUMEN[45]["desde"]))
        for s in RESUMEN[45]["semanas"]]

KPIS = dict(
    vigentes={g["key"]: sum(1 for e in EMBAJADORAS if e["grupo"] == g["key"]) for g in GRUPOS_TIPO},
    fuera=sum(1 for e in EMBAJADORAS if not e["grupo"]),
    coins={g["key"]: sum(e["coins"] for e in EMBAJADORAS if e["grupo"] == g["key"]) for g in GRUPOS_TIPO},
    coins_fuera=sum(e["coins"] for e in EMBAJADORAS if not e["grupo"]),
    coins_total=sum(e["coins"] for e in EMBAJADORAS),
)

# ── Eventos: multiplican la comisión durante unos días ───────────────────────

EVENTOS = [
    dict(id="E-10", nombre="Semana de los Dundies", ponderador=2.0, inicio=date(2026, 12, 14), fin=date(2026, 12, 20),
         participantes=["MICHAEL", "DWIGHT", "KELLY", "JAN"], estado="Programado"),
    dict(id="E-09", nombre="Cyber Monday", ponderador=1.25, inicio=date(2026, 11, 30), fin=date(2026, 12, 2),
         participantes=["ALL"], estado="Programado"),
    dict(id="E-08", nombre="Black Friday", ponderador=1.5, inicio=date(2026, 11, 27), fin=date(2026, 11, 29),
         participantes=["ALL"], estado="Programado"),
    dict(id="E-07", nombre="Olimpiadas de Oficina", ponderador=1.2, inicio=date(2026, 11, 9), fin=date(2026, 11, 22),
         participantes=["JIM", "PAM", "DWIGHT", "KEVIN", "OSCAR"], estado="En curso"),
    dict(id="E-06", nombre="Día del Pretzel", ponderador=1.1, inicio=date(2026, 11, 12), fin=date(2026, 11, 18),
         participantes=["STANLEY", "PHYLLIS", "DARRYL"], estado="En curso"),
]

# ── Mailing ──────────────────────────────────────────────────────────────────

REMITENTE = f"embajadoras@{DOMINIO}"
MAILS = [
    ("15-nov-2026 10:00", "Diario", "DWIGHT", "Tienes 3 referidos nuevos 🎉", "Enviado"),
    ("15-nov-2026 10:00", "Diario", "KELLY", "Tienes 2 referidos nuevos 🎉", "Enviado"),
    ("15-nov-2026 10:00", "Diario", "JIM", "Tienes 1 referido nuevo 🎉", "Enviado"),
    ("14-nov-2026 10:00", "Diario", "CREED", "Tus coins vencen en 15 días", "Error"),
    ("13-nov-2026 17:42", "Anuncio", "STANLEY", "Día del Pretzel: tu comisión sube a x1,1", "Enviado"),
    ("13-nov-2026 17:42", "Anuncio", "PHYLLIS", "Día del Pretzel: tu comisión sube a x1,1", "Enviado"),
    ("13-nov-2026 17:42", "Anuncio", "DARRYL", "Día del Pretzel: tu comisión sube a x1,1", "Enviado"),
    ("12-nov-2026 10:00", "Diario", "KELLY", "Ganaste un premio: 15.000 coins 🏆", "Enviado"),
    ("10-nov-2026 10:00", "Diario", "DWIGHT", "Ganaste un premio: 20.000 coins 🏆", "Enviado"),
    ("09-nov-2026 09:15", "Anuncio", "PAM", "Empiezan las Olimpiadas de Oficina", "Enviado"),
    ("02-nov-2026 12:30", "Bienvenida", "ERIN", "¡Bienvenida al equipo de embajadoras!", "Enviado"),
    ("01-oct-2026 11:05", "Bienvenida", "MEREDITH", "¡Bienvenida al equipo de embajadoras!", "Sin enviar"),
]

# ── Canjes de coins ──────────────────────────────────────────────────────────

CANJES = dict(
    pendientes=[
        ("14-nov-2026", 118, "DWIGHT", "Banco Lackawanna · Cta. Cte.", 60000),
        ("13-nov-2026", 117, "KELLY", "Cooperativa Electric City · Vista", 45000),
        ("11-nov-2026", 116, "JIM", "Banco Lackawanna · Vista", 30000),
    ],
    aprobadas=[
        ("06-nov-2026", 115, "MICHAEL", "Banco Lackawanna · Cta. Cte.", 50000),
        ("30-oct-2026", 114, "PAM", "Cooperativa Electric City · Vista", 25000),
        ("22-oct-2026", 113, "STANLEY", "Banco del Valle · Ahorro", 20000),
        ("15-oct-2026", 112, "JAN", "Banco Lackawanna · Cta. Cte.", 40000),
    ],
    rechazadas=[
        ("03-nov-2026", 111, "CREED", "Datos bancarios incompletos", 12800),
    ],
)

# ── Catálogo de beneficios que se canjean con coins ──────────────────────────

CATALOGO = [
    ("Gift card tienda $10.000", 10000, True),
    ("Gift card tienda $25.000", 25000, True),
    ("Taza «Mejor Jefe del Mundo»", 9000, True),
    ("Velas aromáticas Serenity", 13500, True),
    ("Tetera de cerámica", 22000, True),
    ("Agenda 2027 tapa dura", 10500, True),
    ("Caja sorpresa del Comité de Fiestas", 18000, True),
    ("Entrada doble a los Dundies 2026", 30000, False),
    ("Remolachas orgánicas 1 kg", 3500, False),
]
