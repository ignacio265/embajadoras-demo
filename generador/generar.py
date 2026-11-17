"""Genera las páginas estáticas de la demo en ../sitio.

Solo arma HTML: el sitio publicado no lleva JavaScript ni servidor. Se usa este
script para no repetir a mano el menú, el pie y el aviso de demo en cada página.

    python3 generador/generar.py
"""
import hashlib
import re
from html import escape
from itertools import product
from math import ceil
from pathlib import Path
from urllib.parse import quote

from datos import (CANJES, CATALOGO, CATEGORIAS_PREMIO, EMB, EMBAJADORAS, EVENTOS, GRUPO, GRUPOS,
                   GRUPOS_TIPO, HOY, KPIS, MAILS, PERIODOS, PREMIOS, REMITENTE, RESUMEN, TIENDA, TIPO,
                   TIPOS, ddmm, fecha)

# Las páginas viven bajo /demo-embajadoras/ también en su propio sitio de Netlify,
# para que la ruta sea la misma si ardillalab.com las sirve como proxy.
BASE = "/demo-embajadoras/"
SITIO = Path(__file__).resolve().parent.parent / "sitio" / BASE.strip("/")

CALENDAR = "https://calendar.app.google/a8F5saYxdxWwMsWz7"
WHATSAPP = "https://wa.me/56985272032?text=" + quote(
    "Hola, vi la demo de la App Embajadoras en ardillalab.com y me gustaría agendar una reunión")


# ── Formato ──────────────────────────────────────────────────────────────────

def miles(n):
    return f"{n:,.0f}".replace(",", ".")


def clp(n):
    return f"${miles(n)}"


def millones(n):
    return f"${n / 1e6:,.1f} M".replace(".", ",")


def pond(x):
    return "x" + f"{x:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def plural(n, uno, varios):
    return f"{miles(n)} {uno if n == 1 else varios}"


# ── Íconos (trazos simples, heredan el color) ───────────────────────────────

ICONOS = {
    "inicio": '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
    "dashboard": '<path d="M3 3v18h18"/><path d="M8 16v-5M13 16V8M18 16v-8"/>',
    "embajadoras": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "contratos": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/><path d="M8 13h8M8 17h5"/>',
    "premios": '<path d="M8 21h8M12 17v4"/><path d="M7 4h10v5a5 5 0 0 1-10 0V4Z"/><path d="M7 6H4a3 3 0 0 0 3 4M17 6h3a3 3 0 0 1-3 4"/>',
    "catalogo": '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2V5Z"/><path d="M19 19v2H6a2 2 0 0 1-2-2"/><path d="M9 8h6"/>',
    "canjes": '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M5 12v8h14v-8M12 8v12"/><path d="M12 8c-1.5-4-6-4-5 0M12 8c1.5-4 6-4 5 0"/>',
    "contenido": '<rect x="3" y="6" width="13" height="12" rx="2"/><path d="M16 10l5-3v10l-5-3"/>',
    "eventos": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "mailing": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "marca": '<circle cx="12" cy="9" r="5"/><path d="M9 13.5 7 21l5-3 5 3-2-7.5"/>',
    "mas": '<path d="M12 5v14M5 12h14"/>',
    "menos": '<path d="M5 12h14"/>',
    "descargar": '<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/>',
    "calendario": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "chat": '<path d="M21 11.5a8.4 8.4 0 0 1-12.3 7.4L3 21l2.1-5.6A8.4 8.4 0 1 1 21 11.5Z"/>',
    "megafono": '<path d="M3 11v2a1 1 0 0 0 1 1h3l8 5V5L7 10H4a1 1 0 0 0-1 1Z"/><path d="M18 9a4 4 0 0 1 0 6"/>',
    "enviar": '<path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4 20-7Z"/>',
    "editar": '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5Z"/>',
}


def icono(nombre):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONOS[nombre]}</svg>'


# ── Piezas comunes ───────────────────────────────────────────────────────────

def boton_bloqueado(texto, accion, ico=None, clase=""):
    """Botón de acción visible pero inerte: al pasar el mouse dice qué haría."""
    clases = "btn" + (f" {clase}" if clase else "")
    i = icono(ico) if ico else ""
    return (f'<button type="button" class="{clases}" aria-disabled="true" data-accion="{escape(accion)}" '
            f'aria-label="{escape(texto)} (bloqueado en la demo: {escape(accion)})">{i}{escape(texto)}</button>')


def boton_demo(texto, primario=False, ico=None, clase=""):
    """Botón que abre el aviso de «agenda una demo»."""
    clases = "btn" + (" btn-primario" if primario else "") + (f" {clase}" if clase else "")
    i = icono(ico) if ico else ""
    return f'<button type="button" class="{clases}" popovertarget="demo">{i}{escape(texto)}</button>'


def guia(html):
    return f'<aside class="guia"><span class="guia-icono" aria-hidden="true">i</span><p>{html}</p></aside>'


def modal_demo():
    return f"""
<div id="demo" popover class="modal-demo" role="dialog" aria-labelledby="demo-titulo">
  <div class="modal-cuerpo">
    <div class="modal-ardilla">{icono("marca")}</div>
    <h2 id="demo-titulo">¿Deseas conocer más?</h2>
    <p>Esta función está disponible en la versión completa. Agenda una demo ahora y te la muestro funcionando con tu tienda y tu equipo de embajadoras.</p>
    <div class="modal-botones">
      <a class="btn btn-primario" href="{CALENDAR}" target="_blank" rel="noopener">{icono("calendario")}Agendar en Google Calendar</a>
      <a class="btn btn-whatsapp" href="{WHATSAPP}" target="_blank" rel="noopener">{icono("chat")}Escribir por WhatsApp</a>
    </div>
    <button type="button" class="modal-cerrar" popovertarget="demo" popovertargetaction="hide">Seguir explorando</button>
  </div>
</div>"""


TECNOLOGIAS = ["App embebida de Shopify", "TypeScript", "React Router", "Node.js", "PostgreSQL", "Prisma",
               "Webhooks de Shopify", "Google Cloud Run", "Resend", "HTML y CSS"]


def pie():
    chips = "".join(f'<span class="chip">{t}</span>' for t in TECNOLOGIAS)
    return f"""
<footer class="pie">
  <details>
    <summary>Observaciones de la demo</summary>
    <p>Esta demo está escrita solo en HTML y CSS: no guarda nada, no envía correos y todos los datos (tienda, ventas, coins y personas) son simulados.
    Los nombres de las embajadoras son un guiño a la serie The Office. El aplicativo original se instala en la tienda Shopify del cliente y está desarrollado con:</p>
    <div class="chips">{chips}</div>
  </details>
  <span>Desarrollado por <a href="https://ardillalab.com" target="_blank" rel="noopener">ardillalab.com</a></span>
</footer>"""


MENU = [
    ("inicio", "index.html", "Inicio"),
    ("dashboard", "dashboard.html", "Dashboard"),
    ("embajadoras", "embajadoras.html", "Embajadoras"),
    ("contratos", "contratos.html", "Contratos"),
    ("premios", "premios.html", "Premios"),
    ("catalogo", "catalogo.html", "Catálogo"),
    ("canjes", "canjes.html", "Canjes"),
    ("contenido", None, "Plan de contenido"),
    ("eventos", "eventos.html", "Eventos"),
    ("mailing", "mailing.html", "Mailing"),
]


def menu(activo):
    items = []
    for clave, href, texto in MENU:
        if href is None:  # módulo que solo existe en la versión completa
            items.append(f'<button type="button" class="nav-item" popovertarget="demo">{icono(clave)}'
                         f'<span>{texto}</span><span class="candado" aria-hidden="true">🔒</span></button>')
        else:
            cls = "nav-item activo" if activo == clave else "nav-item"
            actual = ' aria-current="page"' if activo == clave else ""
            items.append(f'<a href="{href}" class="{cls}"{actual}>{icono(clave)}<span>{texto}</span></a>')
        if clave == "inicio":
            items.append('<div class="menu-sep"></div>')
    return f'<nav class="sidebar" aria-label="Menú principal">{"".join(items)}</nav>'


def version_css():
    """Marca de versión de la hoja: cambia cuando cambia el CSS y evita la caché vieja."""
    return hashlib.sha1((SITIO / "css" / "estilos.css").read_bytes()).hexdigest()[:8]


def pagina(nombre, titulo, cuerpo, activo, estilo=""):
    extra = f"<style>{estilo}</style>\n" if estilo else ""
    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)} · App Embajadoras</title>
<meta name="description" content="Demo navegable de un programa de embajadoras para tiendas Shopify: contratos, comisiones, premios, eventos y mailing. Datos simulados.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@600;700&family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="css/estilos.css?v={version_css()}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect width='24' height='24' rx='6' fill='%23E8872A'/%3E%3Ccircle cx='12' cy='10' r='4' fill='none' stroke='white' stroke-width='2'/%3E%3Cpath d='M9.5 13.5 8 19l4-2 4 2-1.5-5.5' fill='none' stroke='white' stroke-width='2' stroke-linejoin='round'/%3E%3C/svg%3E">
{extra}</head>
<body>
<header class="topbar">
  <a class="marca" href="index.html">
    <span class="marca-icono">{icono("marca")}</span>
    <span class="marca-texto">App <span>Embajadoras</span></span>
  </a>
  <div class="topbar-der">
    <span class="pastilla-demo">Modo demo · datos simulados</span>
    <span class="user-chip" title="Tienda de la demo">
      <span class="avatar" aria-hidden="true">PS</span><span class="user-chip-nombre">{TIENDA}</span>
    </span>
  </div>
</header>
<div class="layout">
{menu(activo)}
<main class="content">
{cuerpo}
</main>
</div>
{pie()}
{modal_demo()}
</body>
</html>
"""
    # Todo enlace interno va absoluto con BASE: así no depende de si la URL con
    # que se abrió la página termina o no en barra.
    html = re.sub(r'href="(?!https?:|data:|#|/)', f'href="{BASE}', html)
    (SITIO / nombre).write_text(html, encoding="utf-8")


def insignia_grupo(clave):
    if clave is None:
        return '<span class="grupo gb-fuera">Fuera de contrato</span>'
    return f'<span class="grupo gb-{clave}">{GRUPO[clave]["nombre"]}</span>'


def color_avatar(e):
    return f'var(--g-{e["grupo"]}-tx)' if e["grupo"] else "var(--ink-subtle)"


def persona(e, enlace=True):
    interior = (f'<span class="avatar" style="background:{color_avatar(e)}" aria-hidden="true">{e["iniciales"]}</span>'
                f'<span><b>{escape(e["nombre"])}</b><small class="mono">{e["codigo"]}</small></span>')
    if enlace:
        return f'<a class="persona" href="embajadora-{e["codigo"].lower()}.html">{interior}</a>'
    return f'<span class="persona">{interior}</span>'


def tabs(nombre, pestanas, acciones="", activa=0):
    """Pestañas con radios: `pestanas` es una lista de (rótulo, contenido)."""
    radios = "".join(
        f'<input type="radio" name="{nombre}" id="{nombre}-{i}"{" checked" if i == activa else ""}>'
        for i in range(len(pestanas)))
    rotulos = "".join(f'<label for="{nombre}-{i}">{r}</label>' for i, (r, _) in enumerate(pestanas))
    paneles = "".join(f'<div class="tab-panel">{c}</div>' for _, c in pestanas)
    return (f'<div class="tabs">{radios}<div class="barra-estados"><div class="segmentado">{rotulos}</div>'
            f'<div class="cabecera-acciones">{acciones}</div></div>{paneles}</div>')


def campo(rotulo, valor, tipo="text", clase="", ayuda=""):
    """Campo de muestra: se ve con un valor de ejemplo y no se puede editar."""
    cls = "campo" + (f" {clase}" if clase else "")
    nota = f"<small>{ayuda}</small>" if ayuda else ""
    if tipo == "select":
        control = f'<select disabled><option>{escape(valor)}</option></select>'
    elif tipo == "textarea":
        control = f'<textarea rows="4" disabled>{escape(valor)}</textarea>'
    else:
        control = f'<input type="text" value="{escape(valor)}" disabled>'
    return f'<label class="{cls}"><span>{rotulo}</span>{control}{nota}</label>'


def buscador(rotulo, lista_id, opciones, marcador="Escribe para buscar..."):
    """Buscador con sugerencias nativas (datalist). No filtra nada: es de muestra."""
    ops = "".join(f'<option value="{escape(o)}">' for o in opciones)
    return (f'<label class="campo"><span>{rotulo}</span>'
            f'<input type="search" list="{lista_id}" placeholder="{marcador}" autocomplete="off"></label>'
            f'<datalist id="{lista_id}">{ops}</datalist>')


# ── Inicio ───────────────────────────────────────────────────────────────────

def pag_inicio():
    r45 = RESUMEN[45]
    con_codigo = sum(v for k, v in r45["monto"].items() if k != "sin")
    n_codigo = sum(v for k, v in r45["cuenta"].items() if k != "sin")
    vigentes = sum(KPIS["vigentes"].values())
    pendientes = len(CANJES["pendientes"])
    proximo = min((e for e in EVENTOS if e["estado"] == "Programado"), key=lambda e: e["inicio"])

    modulos = [
        ("m-teal", "dashboard", "dashboard.html", "Dashboard", "Métricas y ventas del equipo", ""),
        ("m-blue", "embajadoras", "embajadoras.html", "Embajadoras", "Agrega, consulta y edita", ""),
        ("m-indigo", "contratos", "contratos.html", "Contratos", "Gestiona grupos y sus recompensas por referidos y alcance", ""),
        ("m-green", "premios", "premios.html", "Premios", "Añade recompensas personalizadas a tu equipo", ""),
        ("m-amber", "catalogo", "catalogo.html", "Catálogo embajadores", "Gestiona los beneficios disponibles para canjear", ""),
        ("m-pink", "canjes", "canjes.html", "Canjes", "Revisa los canjes de coins por crédito de tienda y retiros",
         f'<span class="insignia insignia-pend">{pendientes} pendientes</span>'),
        ("m-rose", "contenido", None, "Plan de Contenido", "Ve y planifica tus colaboraciones",
         '<span class="insignia insignia-demo">Versión completa</span>'),
        ("m-purple", "eventos", "eventos.html", "Eventos", "Planifica eventos como Cyberdays", ""),
        ("m-orange", "mailing", "mailing.html", "Mailing", "Envía correos a tu equipo", ""),
    ]
    cartas = []
    for color, ico, href, titulo, sub, extra in modulos:
        interior = f'{extra}{icono(ico)}<b>{titulo}</b><small>{sub}</small>'
        if href:
            cartas.append(f'<a class="modulo {color}" href="{href}">{interior}</a>')
        else:
            cartas.append(f'<button type="button" class="modulo {color}" popovertarget="demo">{interior}</button>')

    cuerpo = f"""
<div class="cabecera">
  <div>
    <h1>Programa de <span>Embajadoras</span></h1>
    <p class="cabecera-meta">{TIENDA} · actualizado el {fecha(HOY)}</p>
  </div>
</div>
{guia("<strong>Todo el programa de embajadoras en un solo lugar.</strong> Cada embajadora tiene un contrato, un código de descuento "
      "y un saldo de coins que crece con las ventas que refiere. Las ventas llegan solas desde la tienda; aquí se administra el equipo, "
      "sus premios y sus correos.")}
<section class="kpis">
  <div class="tarjeta kpi"><div class="kpi-rotulo">Embajadoras vigentes</div><div class="kpi-valor">{vigentes}</div><div class="kpi-nota">{KPIS["fuera"]} fuera de contrato</div></div>
  <div class="tarjeta kpi"><div class="kpi-rotulo">Ventas con código · 45 días</div><div class="kpi-valor">{millones(con_codigo)}</div><div class="kpi-nota">{miles(n_codigo)} ventas referidas</div></div>
  <div class="tarjeta kpi"><div class="kpi-rotulo">Coins generadas</div><div class="kpi-valor">{miles(KPIS["coins_total"])}</div><div class="kpi-nota">saldo de todo el equipo</div></div>
  <div class="tarjeta kpi"><div class="kpi-rotulo">Próximo evento</div><div class="kpi-valor">{escape(proximo["nombre"])}</div><div class="kpi-nota">desde el {fecha(proximo["inicio"])} · comisión {pond(proximo["ponderador"])}</div></div>
</section>
<section class="modulos">{"".join(cartas)}</section>
"""
    pagina("index.html", "Inicio", cuerpo, "inicio")


# ── Dashboard ────────────────────────────────────────────────────────────────

CLAVES = [g["key"] for g in GRUPOS]


def panel_periodo(dias):
    r = RESUMEN[dias]
    rango = f'{r["desde"].strftime("%d/%m/%Y")} al {r["hasta"].strftime("%d/%m/%Y")}'

    # Un total por cada combinación de grupos: el CSS muestra el que corresponde.
    totales = ""
    for bits in product("10", repeat=len(CLAVES)):
        sel = [k for k, b in zip(CLAVES, bits) if b == "1"]
        if not sel:
            continue
        monto = sum(r["monto"][k] for k in sel)
        n = sum(r["cuenta"][k] for k in sel)
        totales += (f'<div class="tot c-{"".join(bits)}"><div class="ventas-total">{clp(monto)}</div>'
                    f'<div class="ventas-sub">{plural(n, "venta", "ventas")}</div></div>')
    por_grupo = "".join(
        f'<div class="ventas-grupo gb-{k} g-{k}"><span>{GRUPO[k]["emoji"]} {GRUPO[k]["nombre"]}</span>'
        f'<b>{clp(r["monto"][k])}</b><small>{plural(r["cuenta"][k], "venta", "ventas")}</small></div>' for k in CLAVES)

    # Barras apiladas por semana: son cajas de HTML, así se reacomodan solas al ocultar un grupo.
    tope = ceil(max(sum(s["m"].values()) for s in r["semanas"]) / 2e6) * 2e6  # múltiplo de 2 M: marcas redondas
    alto = 240
    columnas = ""
    for s in r["semanas"]:
        segs = "".join(f'<i class="seg g-{k}" style="height:{s["m"][k] / tope * alto:.1f}px"></i>' for k in CLAVES)
        lineas = "".join(
            f'<span class="g-{k}"><i class="c-{k}"></i>{GRUPO[k]["nombre"]}: {clp(s["m"][k])} · {plural(s["n"][k], "venta", "ventas")}</span>'
            for k in CLAVES)
        columnas += f'<div class="col">{segs}<div class="tip"><b>Semana del {ddmm(s["lunes"])}</b>{lineas}</div></div>'
    eje_x = "".join(f'<span>{ddmm(s["lunes"])}</span>' for s in r["semanas"])
    eje_y = "".join(f'<span style="bottom:{p}%">{millones(tope * p / 100) if p else "$0"}</span>' for p in (0, 25, 50, 75, 100))
    leyenda = "".join(f'<span class="g-{k}"><i class="c-{k}"></i>{GRUPO[k]["nombre"]}</span>' for k in CLAVES)

    distri = "".join(f'<i class="c-{k} g-{k}" style="flex-grow:{r["monto"][k] // 1000}" title="{GRUPO[k]["nombre"]}: {clp(r["monto"][k])}"></i>' for k in CLAVES)
    distri_ley = "".join(
        f'<div class="distri-item gb-{k} g-{k}"><span><i class="c-{k}"></i>{GRUPO[k]["nombre"]}</span><b>{clp(r["monto"][k])}</b></div>'
        for k in CLAVES)

    filas_rank = "".join(
        f'<tr class="g-{x["grupo"]}"><td class="pos"></td><td>{persona(EMB[x["codigo"]])}</td>'
        f'<td>{insignia_grupo(x["grupo"])}</td><td class="num ventas">{clp(x["ventas"])}</td>'
        f'<td class="num">{x["referidos"]}</td></tr>' for x in r["ranking"])
    max_prod = r["productos"][0][1]
    filas_prod = "".join(
        f'<tr><td class="centro muted">{i}</td><td>{escape(nombre)}<div class="prod-barra"><b style="width:{n / max_prod * 100:.0f}%"></b></div></td>'
        f'<td class="num"><b>{miles(n)}</b></td></tr>' for i, (nombre, n) in enumerate(r["productos"], 1))

    return f"""
<div class="per per-{dias}">
  <div class="tarjeta dash-vacio">Marca al menos un grupo para ver sus ventas.</div>
  <div class="dash-cuerpo">
    <section class="tarjeta ventas-card">
      <div class="kpi-rotulo">Ventas del período · {rango}</div>
      {totales}
      <div class="ventas-grupos">{por_grupo}</div>
    </section>
    <section class="tarjeta bloque">
      <h2>Ventas por semana</h2>
      <p class="bloque-nota">Cada barra es una semana (parte el lunes). Pasa el mouse sobre una barra para ver su detalle.</p>
      <div class="grafico-scroll">
        <div class="grafico-barras">
          <div class="ejes-y" aria-hidden="true">{eje_y}</div>
          <div class="barras">{columnas}</div>
          <div class="barras-eje" aria-hidden="true">{eje_x}</div>
        </div>
      </div>
      <div class="leyenda">{leyenda}</div>
    </section>
    <section class="tarjeta bloque">
      <h2>Distribución por grupo</h2>
      <p class="bloque-nota">Qué parte de la venta del período aporta cada grupo marcado.</p>
      <div class="distri">{distri}</div>
      <div class="distri-leyenda">{distri_ley}</div>
    </section>
    <div class="dos-col">
      <section class="tarjeta tabla-card">
        <div class="tabla-titulo"><h2>Ranking de embajadoras</h2><span class="muted">según los grupos marcados</span></div>
        <div class="tabla-scroll"><table class="ranking">
          <thead><tr><th class="centro">#</th><th>Embajadora</th><th>Grupo</th><th class="num">Ventas</th><th class="num">Refs.</th></tr></thead>
          <tbody>{filas_rank}</tbody>
        </table></div>
      </section>
      <section class="tarjeta tabla-card">
        <div class="tabla-titulo"><h2>Productos más vendidos</h2><span class="muted">todas las ventas del período</span></div>
        <div class="tabla-scroll"><table>
          <thead><tr><th class="centro">#</th><th>Producto</th><th class="num">Unidades</th></tr></thead>
          <tbody>{filas_prod}</tbody>
        </table></div>
      </section>
    </div>
  </div>
</div>"""


def pag_dashboard():
    kpis = "".join(
        f'<div class="tarjeta kpi kpi-color gb-{g["key"]}"><div class="kpi-rotulo">{g["nombre"]}</div>'
        f'<div class="kpi-valor">{KPIS["vigentes"][g["key"]]}</div><div class="kpi-nota">vigentes</div></div>'
        for g in GRUPOS_TIPO)
    kpis += (f'<div class="tarjeta kpi kpi-color gb-fuera"><div class="kpi-rotulo">Fuera de contrato</div>'
             f'<div class="kpi-valor">{KPIS["fuera"]}</div><div class="kpi-nota">total</div></div>')
    desglose = "".join(f'<span>{g["nombre"]}: <b>{miles(KPIS["coins"][g["key"]])}</b></span>' for g in GRUPOS_TIPO)
    desglose += f'<span>Fuera de contrato: <b>{miles(KPIS["coins_fuera"])}</b></span>'

    radios = "".join(f'<input type="radio" name="periodo" id="p{d}"{" checked" if d == 45 else ""}>' for d in PERIODOS)
    casillas = "".join(
        f'<input type="checkbox" id="g-{g["key"]}"{" checked" if g["key"] != "sin" else ""}>' for g in GRUPOS)
    rot_periodos = "".join(f'<label for="p{d}">Últimos {d} días</label>' for d in PERIODOS)
    rot_grupos = "".join(
        f'<label class="chip-grupo" for="g-{g["key"]}"><span class="caja" aria-hidden="true">✓</span>{g["emoji"]} {g["nombre"]}</label>'
        for g in GRUPOS)

    # Reglas que muestran el total de la combinación de grupos marcada.
    reglas = ""
    for bits in product("10", repeat=len(CLAVES)):
        if "1" not in bits:
            continue
        cond = "".join(f':has(#g-{k}{":checked" if b == "1" else ":not(:checked)"})' for k, b in zip(CLAVES, bits))
        reglas += f'.dash{cond} .tot.c-{"".join(bits)}{{display:block}}'

    cuerpo = f"""
<div class="cabecera"><h1>Dashboard <span>· Métricas del equipo</span></h1></div>
{guia("<strong>Cómo vende tu equipo de embajadoras.</strong> Elige un período y marca los grupos que quieres comparar: "
      "los totales, el gráfico, la distribución y el ranking cambian con tu selección. Cada venta se atribuye al contrato "
      "que tenía la embajadora ese día.")}
<section class="kpis kpis-grupos">{kpis}</section>
<section class="tarjeta coins-card gb-coins">
  <div class="kpi-rotulo">Total de coins generadas</div>
  <div class="kpi-valor">{miles(KPIS["coins_total"])}</div>
  <div class="coins-desglose">{desglose}</div>
</section>
<div class="dash">
  {radios}{casillas}
  <section class="tarjeta dash-filtros">
    <div class="filtro-fila"><span class="filtro-rotulo">Período</span><div class="segmentado">{rot_periodos}</div></div>
    <div class="filtro-fila"><span class="filtro-rotulo">Grupos</span>{rot_grupos}</div>
  </section>
  {"".join(panel_periodo(d) for d in PERIODOS)}
</div>
"""
    pagina("dashboard.html", "Dashboard", cuerpo, "dashboard", estilo=reglas)


# ── Embajadoras: lista y ficha ───────────────────────────────────────────────

def pag_embajadoras():
    filas = ""
    for e in EMBAJADORAS:
        cls = f'e-{e["grupo"] or "fuera"}'
        c = e["contrato"]
        fin = fecha(c["fin"]) if c["estado"] == "Vigente" else f'terminó el {fecha(c["fin"])}'
        filas += (f'<tr class="{cls}"><td class="mono muted">{e["id"]:02d}</td><td>{persona(e)}</td>'
                  f'<td>{insignia_grupo(e["grupo"])}</td><td>{e["instagram"]}</td>'
                  f'<td class="num">{clp(e["ventas45"]) if e["ventas45"] else "—"}</td>'
                  f'<td class="num">{e["referidos45"] or "—"}</td><td class="num coins">{miles(e["coins"])}</td>'
                  f'<td>{fin}</td>'
                  f'<td><a class="btn btn-chico" href="embajadora-{e["codigo"].lower()}.html">Ver ficha</a></td></tr>')
    cuenta = {k: sum(1 for e in EMBAJADORAS if (e["grupo"] or "fuera") == k) for k in ("vip", "ven", "com", "fuera")}
    chips = f'<label class="chip-filtro" for="fe-todas">Todas <b>{len(EMBAJADORAS)}</b></label>'
    chips += "".join(f'<label class="chip-filtro" for="fe-{g["key"]}">{g["nombre"]} <b>{cuenta[g["key"]]}</b></label>' for g in GRUPOS_TIPO)
    chips += f'<label class="chip-filtro" for="fe-fuera">Fuera de contrato <b>{cuenta["fuera"]}</b></label>'
    radios = '<input type="radio" name="fe" id="fe-todas" checked>' + "".join(
        f'<input type="radio" name="fe" id="fe-{k}">' for k in ("vip", "ven", "com", "fuera"))

    cuerpo = f"""
<div class="cabecera">
  <h1>Embajadoras <span>· Equipo</span></h1>
  <div class="cabecera-acciones">
    {boton_demo("Modificar embajadora", ico="editar")}
    {boton_demo("Agregar embajadora", primario=True, ico="mas")}
  </div>
</div>
{guia("<strong>Quién es parte del programa.</strong> Cada embajadora tiene su código de descuento, su grupo (el tipo de contrato vigente) "
      "y su saldo de coins. Filtra por grupo o entra a una ficha para ver su rendimiento, sus premios y su contrato.")}
<div class="tarjeta buscador">
  {buscador("Buscar embajadora", "dl-emb", [f'{e["codigo"]} | {e["nombre"]}' for e in EMBAJADORAS], "Nombre o código...")}
  {boton_bloqueado("Buscar", "Abriría la ficha de la embajadora elegida", clase="tip-der")}
</div>
<div class="filtro-emb">
  {radios}
  <div class="chips-filtro">{chips}</div>
  <div class="tarjeta tabla-card">
    <div class="tabla-scroll"><table>
      <thead><tr><th>ID</th><th>Embajadora</th><th>Grupo</th><th>Instagram</th><th class="num">Ventas 45 días</th><th class="num">Referidos</th><th class="num">Coins</th><th>Contrato hasta</th><th></th></tr></thead>
      <tbody>{filas}</tbody>
    </table></div>
    <div class="tabla-pie">Ventas y referidos de los últimos 45 días. Las coins son el saldo actual de cada embajadora.</div>
  </div>
</div>
"""
    pagina("embajadoras.html", "Embajadoras", cuerpo, "embajadoras")


def grafico_area(semanas):
    """Ventas por semana de una embajadora: un área en SVG, dibujada de antemano."""
    ancho, alto, izq, der, arr, aba = 640, 230, 54, 14, 12, 28
    tope = max(ceil(max(v for _, v in semanas) / 100000) * 100000, 100000)
    paso = (ancho - izq - der) / (len(semanas) - 1)
    pts = [(izq + i * paso, arr + (alto - arr - aba) * (1 - v / tope)) for i, (_, v) in enumerate(semanas)]
    base = alto - aba
    linea = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{izq},{base} {linea} {pts[-1][0]:.1f},{base}"
    guias = ""
    for p in (0, 0.5, 1):
        y = arr + (alto - arr - aba) * (1 - p)
        rot = "$0" if not p else f"${tope * p / 1000:,.0f} mil".replace(",", ".")
        guias += f'<line class="g-linea" x1="{izq}" y1="{y:.1f}" x2="{ancho - der}" y2="{y:.1f}"/><text class="g-eje" x="{izq - 8}" y="{y + 4:.1f}" text-anchor="end">{rot}</text>'
    ejes = "".join(f'<text class="g-eje" x="{x:.1f}" y="{alto - 8}" text-anchor="middle">{ddmm(d)}</text>' for (d, _), (x, _) in zip(semanas, pts))
    puntos = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#22C55E"><title>Semana del {ddmm(d)}: {clp(v)}</title></circle>'
                     for (d, v), (x, y) in zip(semanas, pts))
    return (f'<svg class="grafico" viewBox="0 0 {ancho} {alto}" role="img" aria-label="Ventas por semana de los últimos 45 días">{guias}'
            f'<polygon points="{area}" fill="#22C55E" fill-opacity=".18"/>'
            f'<polyline points="{linea}" fill="none" stroke="#22C55E" stroke-width="2.5" stroke-linejoin="round"/>{puntos}{ejes}</svg>')


def tabla_historial(e):
    estados = {"Vigente": "estado-ok", "Finalizado": "estado-gris", "Programado": "estado-prog"}
    filas = "".join(
        f'<tr><td><b>{c["tipo"]}</b></td><td>{fecha(c["inicio"])}</td><td>{fecha(c["fin"])}</td>'
        f'<td><span class="estado {estados[c["estado"]]}">{c["estado"]}</span></td><td class="largo muted">{c["nota"] or "—"}</td></tr>'
        for c in e["historial"])
    return (f'<div class="tabla-scroll"><table><thead><tr><th>Tipo de contrato</th><th>Inicio</th><th>Fin</th><th>Estado</th><th>Notas</th></tr></thead>'
            f'<tbody>{filas}</tbody></table></div>')


def pag_ficha(e):
    c = e["contrato"]
    vigente = c["estado"] == "Vigente"
    if e["premios"]:
        premios = '<ul class="lista-premios">' + "".join(
            f'<li><span>{escape(p["motivo"])}<small>{fecha(p["fecha"])} · {p["categoria"]}</small></span><b class="coins">+{miles(p["coins"])}</b></li>'
            for p in e["premios"]) + "</ul>"
    else:
        premios = '<p class="muted" style="margin:0">Sin premios registrados.</p>'
    if e["referidos45"]:
        ventas = (f'<div class="resumen-ventas"><small>Ventas de {escape(e["nombre"])} en los últimos 45 días</small>'
                  f'<b>{clp(e["ventas45"])} · {plural(e["referidos45"], "referido", "referidos")}</b></div>{grafico_area(e["semanas45"])}')
    else:
        ventas = '<p class="muted" style="margin:0;padding:30px 0;text-align:center">Sin ventas en los últimos 45 días.</p>'
    tipo = TIPO.get(e["grupo"])
    comision = f'{tipo["comision"]} % sobre el {tipo["base"].lower()}' if tipo else "—"

    cuerpo = f"""
<div class="migas"><a href="embajadoras.html">Embajadoras</a> › {escape(e["nombre"])}</div>
<div class="cabecera">
  <h1>Centro de control — <span>{escape(e["nombre"])}</span></h1>
  <div class="cabecera-acciones">
    {boton_bloqueado("Descargar referidos", "Descargaría una planilla Excel con todas las ventas referidas por la embajadora", ico="descargar", clase="tip-abajo")}
    {boton_demo("Modificar embajadora", ico="editar")}
  </div>
</div>
<div class="ficha">
  <section class="tarjeta perfil">
    <div class="avatar avatar-xl" style="background:{color_avatar(e)}" aria-hidden="true">{e["iniciales"]}</div>
    <h2>{escape(e["nombre"])}</h2>
    {insignia_grupo(e["grupo"])}
    <div class="stats">
      <div class="stat"><small>Ventas 45 días</small><b>{clp(e["ventas45"])}</b></div>
      <div class="stat"><small>Coins</small><b>{miles(e["coins"])}</b></div>
      <div class="stat"><small>Referidos</small><b>{e["referidos45"]}</b></div>
      <div class="stat"><small>Código</small><b class="mono">{e["codigo"]}</b></div>
    </div>
    <dl class="detalles">
      <div><dt>Instagram</dt><dd>{e["instagram"]}</dd></div>
      <div><dt>Correo</dt><dd>{e["correo"]}</dd></div>
      <div><dt>Teléfono</dt><dd>{e["telefono"]}</dd></div>
      <div><dt>Cumpleaños</dt><dd>{e["cumple"]}</dd></div>
      <div><dt>Dirección</dt><dd>{e["direccion"]}</dd></div>
      <div class="apilar"><dt>Link con descuento</dt><dd class="mono">{e["link_descuento"]}</dd></div>
      <div class="apilar"><dt>Link sin descuento (7 días)</dt><dd class="mono">{e["link_referido"]}</dd></div>
    </dl>
    <div class="perfil-botones">
      {boton_bloqueado("Contactar por WhatsApp", "Abriría WhatsApp con un mensaje para la embajadora", ico="chat", clase="tip-izq")}
    </div>
  </section>
  <div class="apilado">
    <section class="tarjeta panel">
      <h2>Rendimiento</h2>
      {ventas}
    </section>
    <section class="tarjeta panel">
      <h2>Premios ganados ({len(e["premios"])})</h2>
      {premios}
    </section>
    <section class="tarjeta tabla-card">
      <div class="tabla-titulo">
        <h2>Contrato</h2>
        <span class="muted">{"Comisión: " + comision if vigente else "Sin contrato vigente"}</span>
      </div>
      {tabla_historial(e)}
      <div class="tabla-pie" style="display:flex;gap:8px;flex-wrap:wrap">
        {boton_demo("Cambiar contrato", clase="btn-chico") if vigente else ""}
        {boton_demo("Dar fin a contrato", clase="btn-chico btn-peligro") if vigente else ""}
        {boton_demo("Asignar nuevo contrato", clase="btn-chico")}
      </div>
    </section>
  </div>
</div>
"""
    pagina(f"embajadora-{e['codigo'].lower()}.html", e["nombre"], cuerpo, "embajadoras")


# ── Contratos ────────────────────────────────────────────────────────────────

def pag_contratos():
    def sino(x):
        return '<span class="si">✓</span>' if x else '<span class="no">—</span>'

    filas_tipos = ""
    for t in TIPOS:
        estado = "Activo" if t["activo"] else "Inactivo"
        ayuda = "Activo: en la versión completa, un clic lo desactiva" if t["activo"] else "Inactivo: en la versión completa, un clic lo activa"
        n = sum(1 for e in EMBAJADORAS if e["contrato"]["tipo"] == t["nombre"] and e["contrato"]["estado"] == "Vigente")
        filas_tipos += (f'<tr class="{"" if t["activo"] else "apagada"}"><td class="mono">{t["id"]}</td>'
                        f'<td><b>{t["nombre"]}</b><span class="sub">{t["desc"]}</span></td>'
                        f'<td class="num">{t["comision"]} %</td><td>{t["base"]}</td>'
                        f'<td class="centro">{sino(t["alcance"])}</td><td class="centro">{sino(t["bonus"])}</td>'
                        f'<td class="num">{n}</td>'
                        f'<td><span class="toggle{" on" if t["activo"] else ""}" title="🔒 {ayuda}"><i></i>{estado}</span></td></tr>')
    panel_tipos = f"""
<div class="tarjeta tabla-card">
  <div class="tabla-scroll"><table>
    <thead><tr><th>ID</th><th>Nombre</th><th class="num">Comisión</th><th>Comisión en</th><th class="centro">Alcance</th><th class="centro">Bonus</th><th class="num">Vigentes</th><th>Estado</th></tr></thead>
    <tbody>{filas_tipos}</tbody>
  </table></div>
  <div class="tabla-pie">Una vez creado, un tipo de contrato no se edita: si hay que cambiarlo, se desactiva y se crea uno nuevo. Así los contratos ya firmados no cambian.</div>
</div>"""

    estados = {"Vigente": "estado-ok", "Finalizado": "estado-gris"}
    filas_c = ""
    for e in EMBAJADORAS:
        c = e["contrato"]
        t = TIPO.get(e["grupo"])
        filas_c += (f'<tr><td>{persona(e)}</td><td>{c["tipo"]}</td><td>{fecha(c["inicio"])}</td><td>{fecha(c["fin"])}</td>'
                    f'<td class="num">{str(t["comision"]) + " %" if t else "—"}</td>'
                    f'<td><span class="estado {estados[c["estado"]]}">{c["estado"]}</span></td>'
                    f'<td>{boton_demo("Administrar", clase="btn-chico")}</td></tr>')
    panel_contratos = f"""
<div class="tarjeta tabla-card">
  <div class="tabla-scroll"><table>
    <thead><tr><th>Embajadora</th><th>Tipo de contrato</th><th>Inicio</th><th>Fin</th><th class="num">Comisión</th><th>Estado</th><th></th></tr></thead>
    <tbody>{filas_c}</tbody>
  </table></div>
  <div class="tabla-pie">Administrar permite cambiar el contrato, darle fin o asignar uno nuevo. El historial completo está en la ficha de cada embajadora.</div>
</div>"""

    cuerpo = f"""
<div class="cabecera"><h1>Contratos <span>· Grupos y recompensas</span></h1></div>
{guia("<strong>Las reglas con que gana cada embajadora.</strong> Un tipo de contrato define la comisión, sobre qué monto se calcula, "
      "si premia el alcance del contenido y si hay bonus por los primeros referidos. Cada embajadora tiene un contrato con fechas, "
      "y sus ventas se pagan según el contrato que tenía el día de la venta.")}
{tabs("ct", [("Tipos de contrato", panel_tipos), ("Contratos por embajadora", panel_contratos)],
      acciones=boton_demo("Agregar nuevo tipo", primario=True, ico="mas"))}
"""
    pagina("contratos.html", "Contratos", cuerpo, "contratos")


# ── Premios ──────────────────────────────────────────────────────────────────

def tabla_premios(quitar=False):
    filas = ""
    for p in PREMIOS:
        accion = f'<td>{boton_demo("Quitar", clase="btn-chico btn-peligro", ico="menos")}</td>' if quitar else ""
        filas += (f'<tr><td class="mono">{p["id"]}</td><td>{fecha(p["fecha"])}</td><td>{persona(EMB[p["codigo"]])}</td>'
                  f'<td>{p["categoria"]}</td><td class="largo">{escape(p["motivo"])}</td>'
                  f'<td class="num coins">{miles(p["coins"])}</td>{accion}</tr>')
    total = sum(p["coins"] for p in PREMIOS)
    return f"""
<div class="tarjeta tabla-card">
  <div class="tabla-titulo"><h2>Premios actuales ({len(PREMIOS)})</h2><span class="muted">{miles(total)} coins entregadas</span></div>
  <div class="tabla-scroll"><table>
    <thead><tr><th>ID</th><th>Fecha</th><th>Embajadora</th><th>Categoría</th><th>Motivo</th><th class="num">Coins</th>{"<th></th>" if quitar else ""}</tr></thead>
    <tbody>{filas}</tbody>
  </table></div>
</div>"""


def pag_premios():
    agregar = f"""
<div class="apilado">
  <section class="tarjeta panel">
    <h2>Nuevo premio</h2>
    <div class="form-demo">
      {buscador("Buscar embajadora", "dl-emb", [f'{e["codigo"]} | {e["nombre"]}' for e in EMBAJADORAS], "Código o nombre...")}
      {campo("Fecha", fecha(HOY))}
      {campo("Coins", "10.000")}
      {campo("Categoría", CATEGORIAS_PREMIO[1], tipo="select")}
      {campo("Descripción", "Motivo del premio...", clase="campo-full")}
      <div class="form-botones">{boton_demo("Guardar registro", primario=True)}</div>
    </div>
  </section>
  {tabla_premios()}
</div>"""
    quitar = f"""
<div class="apilado">
  <div class="tarjeta buscador" style="margin-bottom:0">
    {buscador("Buscar registro", "dl-premios", [f'{p["id"]} · {p["codigo"]} · {p["motivo"]}' for p in PREMIOS], "ID, embajadora o motivo...")}
    {boton_demo("Confirmar baja", clase="btn-peligro")}
  </div>
  {tabla_premios(quitar=True)}
</div>"""
    cuerpo = f"""
<div class="cabecera"><h1>Premios <span>· Recompensas del equipo</span></h1></div>
{guia("<strong>Coins que se entregan por fuera de las ventas.</strong> Un bono de bienvenida, el mejor reel del mes o una actividad especial. "
      "Al agregar o quitar un premio tienes a la vista los premios actuales, para no duplicar ni borrar el que no era.")}
{tabs("pr", [("Agregar premio", agregar), ("Quitar premio", quitar)])}
"""
    pagina("premios.html", "Premios", cuerpo, "premios")


# ── Eventos ──────────────────────────────────────────────────────────────────

def participantes(ev):
    if ev["participantes"] == ["ALL"]:
        return '<span class="chip chip-azul">Todas las embajadoras</span>'
    return " ".join(f'<span class="chip chip-azul">{c}</span>' for c in ev["participantes"])


def tabla_eventos(quitar=False):
    estados = {"En curso": "estado-curso", "Programado": "estado-prog"}
    filas = ""
    for ev in EVENTOS:
        accion = f'<td>{boton_demo("Quitar", clase="btn-chico btn-peligro", ico="menos")}</td>' if quitar else ""
        filas += (f'<tr><td class="mono">{ev["id"]}</td><td><b>{escape(ev["nombre"])}</b></td>'
                  f'<td class="num"><b>{pond(ev["ponderador"])}</b></td><td>{fecha(ev["inicio"])} al {fecha(ev["fin"])}</td>'
                  f'<td class="largo">{participantes(ev)}</td>'
                  f'<td><span class="estado {estados[ev["estado"]]}">{ev["estado"]}</span></td>{accion}</tr>')
    return f"""
<div class="tarjeta tabla-card">
  <div class="tabla-titulo"><h2>Eventos actuales ({len(EVENTOS)})</h2><span class="muted">activos y programados</span></div>
  <div class="tabla-scroll"><table>
    <thead><tr><th>ID</th><th>Evento</th><th class="num">Ponderador</th><th>Vigencia</th><th>Participantes</th><th>Estado</th>{"<th></th>" if quitar else ""}</tr></thead>
    <tbody>{filas}</tbody>
  </table></div>
</div>"""


def pag_eventos():
    agregar = f"""
<div class="apilado">
  <section class="tarjeta panel">
    <h2>Nuevo evento</h2>
    <div class="form-demo">
      {campo("Descripción del evento", "Ej: Cyber Monday")}
      {campo("Ponderador", "1,25", ayuda="1 = comisión normal. 1,25 = 25 % de comisión adicional.")}
      {campo("Fecha de inicio", "30-nov-2026")}
      {campo("Fecha de fin", "02-dic-2026")}
      {buscador("Participantes", "dl-part", ["0 - ALL (todas las embajadoras)"] + [f'{e["id"]} - {e["codigo"]} · {e["nombre"]}' for e in EMBAJADORAS], "Busca ID o código...")}
      <div class="form-botones">{boton_demo("Guardar evento", primario=True)}</div>
    </div>
  </section>
  {tabla_eventos()}
</div>"""
    quitar = f"""
<div class="apilado">
  <div class="tarjeta buscador" style="margin-bottom:0">
    {buscador("Buscar evento", "dl-eventos", [f'{ev["id"]} · {ev["nombre"]}' for ev in EVENTOS], "ID o nombre...")}
    {boton_demo("Confirmar baja", clase="btn-peligro")}
  </div>
  {tabla_eventos(quitar=True)}
</div>"""
    cuerpo = f"""
<div class="cabecera">
  <h1>Eventos <span>· Comisión extra por fechas</span></h1>
  <div class="cabecera-acciones"><a class="btn" href="mailing-anunciar.html">{icono("megafono")}Anunciar evento</a></div>
</div>
{guia("<strong>Días en que vender paga más.</strong> Un evento multiplica la comisión de sus participantes durante su vigencia: "
      "un Cyber, un lanzamiento o una competencia interna. Al agregar o quitar un evento ves los eventos actuales, con sus fechas y participantes.")}
{tabs("ev", [("Agregar evento", agregar), ("Quitar evento", quitar)])}
"""
    pagina("eventos.html", "Eventos", cuerpo, "eventos")


# ── Mailing ──────────────────────────────────────────────────────────────────

def pag_mailing(nombre, activa):
    estados = {"Enviado": "estado-ok", "Sin enviar": "estado-curso", "Error": "estado-mal"}
    filas = "".join(
        f'<tr><td>{f}</td><td>{tipo}</td><td><b class="mono">{cod}</b> · {EMB[cod]["correo"]}</td>'
        f'<td class="largo">{escape(asunto)}</td><td><span class="estado {estados[est]}">{est}</span></td></tr>'
        for f, tipo, cod, asunto, est in MAILS)
    historial = f"""
<div class="tarjeta tabla-card">
  <div class="tabla-titulo"><h2>Mails enviados</h2><span class="muted">los últimos correos a embajadoras</span></div>
  <div class="tabla-scroll"><table>
    <thead><tr><th>Fecha</th><th>Tipo</th><th>Para</th><th>Asunto</th><th>Estado</th></tr></thead>
    <tbody>{filas}</tbody>
  </table></div>
  <div class="tabla-pie">Cada correo queda registrado con su estado. Si uno falla, aquí se ve el motivo para reenviarlo.</div>
</div>"""

    pam = EMB["PAM"]
    diario = f"""
<div class="apilado">
  <div class="nota-caja"><strong>Cada día a las 10:00</strong> se envía a cada embajadora solo lo que le corresponde: sus referidos nuevos,
    los premios que ganó y un aviso 15 días antes de que venzan sus coins. Si no tiene novedades, no recibe correo.
    Último envío: {fecha(HOY)} a las 10:00.</div>
  <div style="display:flex;gap:8px;flex-wrap:wrap">
    {boton_bloqueado("Cambiar hora del envío", "Guardaría la nueva hora del correo diario", clase="tip-izq")}
    {boton_demo("Enviar ahora el correo diario", ico="enviar")}
  </div>
  <section class="tarjeta panel">
    <h2>Así lo recibe una embajadora</h2>
    <div class="correo">
      <div class="correo-cab"><span>De: <b>{TIENDA}</b> &lt;{REMITENTE}&gt;</span><span>Para: {pam["correo"]}</span><span>Asunto: <b>Tienes 2 referidos nuevos 🎉</b></span></div>
      <div class="correo-cuerpo">
        <h3>¡Hola, Pam!</h3>
        <p>Ayer dos personas compraron con tu código <b class="mono">PAM</b>. Así va tu mes:</p>
        <div class="correo-cifras">
          <div class="gb-vip"><b>{pam["referidos45"]}</b><small>referidos en 45 días</small></div>
          <div class="gb-coins"><b>{miles(pam["coins"])}</b><small>coins disponibles</small></div>
          <div class="gb-ven"><b>{pond(1.2)}</b><small>Olimpiadas de Oficina</small></div>
        </div>
        <p>Recuerda que hasta el 22 de noviembre tus ventas suman con comisión {pond(1.2)} por las Olimpiadas de Oficina.</p>
        <p class="correo-pie">Recibes este correo porque eres embajadora de {TIENDA}.</p>
      </div>
    </div>
  </section>
</div>"""

    ev = next(e for e in EVENTOS if e["nombre"] == "Black Friday")
    anunciar = f"""
<section class="tarjeta panel">
  <h2>Anunciar un evento</h2>
  <div class="form-demo">
    {campo("Asunto del correo", "Black Friday: tu comisión sube a x1,5", clase="campo-full")}
    {campo("Evento", f'{ev["nombre"]} ({fecha(ev["inicio"])} al {fecha(ev["fin"])})', tipo="select", clase="campo-full")}
    <div class="nota-caja campo-full"><strong>Vigencia:</strong> {fecha(ev["inicio"])} al {fecha(ev["fin"])} ·
      <strong>Ponderador:</strong> {pond(ev["ponderador"])} · <strong>Participantes:</strong> todas las embajadoras ({sum(KPIS["vigentes"].values())})</div>
    {campo("Mensaje", "Este viernes parte Black Friday. Durante tres días, cada venta con tu código suma un 50 % más de coins. "
           "Te dejamos el material para tus historias en el enlace de siempre.", tipo="textarea", clase="campo-full")}
    {campo("Imagen del evento (opcional)", "https://cdn.shopify.com/...")}
    {campo("Correo para la prueba", REMITENTE)}
    <div class="form-botones">
      {boton_bloqueado("Enviar prueba", "Enviaría el anuncio solo al correo de prueba, para revisarlo antes", clase="tip-der")}
      {boton_demo("Enviar a participantes", primario=True, ico="enviar")}
    </div>
  </div>
</section>"""

    cuerpo = f"""
<div class="cabecera">
  <h1>Mailing <span>· Correos al equipo</span></h1>
  <div class="cabecera-acciones">{boton_demo("Enviar mail de bienvenida", primario=True, ico="enviar")}</div>
</div>
{guia(f"<strong>El programa avisa solo.</strong> Las embajadoras reciben por correo sus referidos, premios y eventos sin que nadie los redacte uno a uno. "
      f"Envío activo desde <strong>{REMITENTE}</strong>.")}
{tabs("ml", [("Mails enviados", historial), ("Correo diario", diario), ("Anunciar evento", anunciar)], activa=activa)}
"""
    pagina(nombre, "Mailing", cuerpo, "mailing")


# ── Canjes y catálogo ────────────────────────────────────────────────────────

def pag_canjes():
    def panel(clave, rotulo, banner, estado_cls, estado_txt, col_banco):
        lista = CANJES[clave]
        total = sum(x[4] for x in lista)
        filas = "".join(
            f'<tr><td>{f}</td><td><b>#{n}</b></td><td>{persona(EMB[cod])}</td><td class="muted">{banco}</td>'
            f'<td class="num coins">{miles(coins)}</td><td class="num">{clp(coins)}</td>'
            f'<td><span class="estado {estado_cls}">{estado_txt}</span></td><td>{boton_demo("Ver", clase="btn-chico")}</td></tr>'
            for f, n, cod, banco, coins in lista)
        return f"""
<div class="banner-kpi {banner}"><div><small>{rotulo}</small><b>{miles(total)}</b></div><span>{plural(len(lista), "solicitud", "solicitudes")}</span></div>
<div class="tarjeta tabla-card">
  <div class="tabla-scroll"><table>
    <thead><tr><th>Fecha</th><th>Nº</th><th>Embajadora</th><th>{col_banco}</th><th class="num">Coins</th><th class="num">Monto bruto</th><th>Estado</th><th></th></tr></thead>
    <tbody>{filas}</tbody>
  </table></div>
</div>"""

    n = {k: len(v) for k, v in CANJES.items()}
    cuerpo = f"""
<div class="cabecera"><h1>Canjes <span>· Retiros de coins</span></h1></div>
{guia("<strong>Cuando una embajadora cobra sus coins.</strong> Puede pedir un retiro en dinero o cambiarlas por crédito en la tienda. "
      "Cada solicitud se revisa aquí: al aprobarla, las coins se descuentan de su saldo.")}
{tabs("cj", [
    (f"Pendientes <b>{n['pendientes']}</b>", panel("pendientes", "Total de coins pendientes", "b-pend", "estado-curso", "Pendiente", "Banco")),
    (f"Aprobadas <b>{n['aprobadas']}</b>", panel("aprobadas", "Total de coins aprobadas", "b-ok", "estado-ok", "Aprobada", "Banco")),
    (f"Rechazadas <b>{n['rechazadas']}</b>", panel("rechazadas", "Total de coins rechazadas", "b-mal", "estado-mal", "Rechazada", "Motivo")),
])}
"""
    pagina("canjes.html", "Canjes", cuerpo, "canjes")


def pag_catalogo():
    filas = "".join(
        f'<tr class="{"" if visible else "apagada"}"><td><b>{escape(nombre)}</b></td><td class="num coins">{miles(coins)}</td>'
        f'<td><span class="estado {"estado-ok" if visible else "estado-gris"}">{"Visible" if visible else "Oculto"}</span></td>'
        f'<td>{boton_demo("Ocultar" if visible else "Mostrar", clase="btn-chico")}</td></tr>'
        for nombre, coins, visible in CATALOGO)
    cuerpo = f"""
<div class="cabecera"><h1>Catálogo <span>· Beneficios para canjear</span></h1></div>
{guia("<strong>En qué pueden gastar sus coins.</strong> Los productos y gift cards que las embajadoras ven en su portal, con su precio en coins. "
      "Un beneficio oculto deja de aparecer en el portal sin borrarse.")}
<div class="tarjeta tabla-card">
  <div class="tabla-scroll"><table>
    <thead><tr><th>Beneficio</th><th class="num">Precio en coins</th><th>Estado en el portal</th><th></th></tr></thead>
    <tbody>{filas}</tbody>
  </table></div>
  <div class="tabla-pie">Los beneficios salen de los productos de la tienda: no hay que cargarlos dos veces.</div>
</div>
"""
    pagina("catalogo.html", "Catálogo", cuerpo, "catalogo")


def pag_404():
    cuerpo = """
<div class="tarjeta vacio-404">
  <h1>Esta pantalla no existe</h1>
  <p class="muted">La demo muestra solo una parte del aplicativo.</p>
  <a class="btn btn-primario" href="index.html">Volver al inicio</a>
</div>
"""
    pagina("404.html", "No encontrada", cuerpo, "")


def main():
    SITIO.mkdir(parents=True, exist_ok=True)
    for viejo in SITIO.glob("*.html"):
        viejo.unlink()
    pag_inicio()
    pag_dashboard()
    pag_embajadoras()
    for e in EMBAJADORAS:
        pag_ficha(e)
    pag_contratos()
    pag_premios()
    pag_eventos()
    pag_mailing("mailing.html", 0)
    pag_mailing("mailing-anunciar.html", 2)
    pag_canjes()
    pag_catalogo()
    pag_404()
    print(f"{len(list(SITIO.glob('*.html')))} páginas en {SITIO}")


if __name__ == "__main__":
    main()
