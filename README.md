# App Embajadoras · demo

**Demo en vivo / Live demo: [ardillalab.com/demo-embajadoras](https://ardillalab.com/demo-embajadoras/)**

[Español](#español) · [English](#english)

---

## Español

Demo navegable de un **programa de embajadoras para tiendas Shopify**. Muestra cómo
una marca administra a su equipo de embajadoras: contratos, comisiones por ventas
referidas, premios, eventos y correos.

Es una versión reducida de un aplicativo real. Aquí **todo es simulado**: la tienda,
las ventas, las coins y las personas (los nombres son un guiño a la serie
*The Office*). Las acciones que modificarían datos no hacen nada: unas dicen qué
harían al pasar el mouse y otras abren el aviso de «agenda una demo».

### Qué se puede recorrer

| Pantalla | Qué muestra |
|---|---|
| **Inicio** | Indicadores del programa y los nueve módulos de la app |
| **Dashboard** | Ventas por período y por grupo, con filtros que funcionan sin JavaScript |
| **Embajadoras** | El equipo, filtrable por grupo, y la ficha de cada embajadora |
| **Contratos** | Tipos de contrato (comisión, alcance, bonus) y contrato de cada embajadora |
| **Premios · Eventos** | Formularios de alta y baja con la tabla de premios y eventos actuales |
| **Mailing** | Correos enviados, correo diario con vista previa y anuncio de eventos |
| **Canjes · Catálogo** | Retiros de coins por estado y beneficios canjeables |

### Cómo está hecha

- **Solo HTML y CSS.** No lleva ni una línea de JavaScript.
  - El aviso de «agenda una demo» usa el atributo nativo `popover`.
  - Las pestañas y los filtros usan radios y casillas con `:checked` y `:has()`.
  - En el dashboard, las barras son cajas de HTML: al desmarcar un grupo se
    reacomodan solas. El total de cada combinación de grupos va escrito de
    antemano y el CSS muestra el que corresponde.
  - Los buscadores usan `datalist`, el autocompletado nativo del navegador.
- **Paleta de [ardillalab.com](https://ardillalab.com)**, con Comfortaa, DM Sans y
  JetBrains Mono.
- **Se adapta al celular**: el menú pasa a una barra horizontal y las tablas se
  desplazan dentro de su tarjeta.
- Las 29 páginas las arma un script en Python, sin dependencias externas
  (`generador/generar.py`), a partir de datos simulados deterministas
  (`generador/datos.py`). Lo que se publica es solo la carpeta `sitio/`.

### El aplicativo original

El sistema real se instala en la tienda Shopify del cliente, embebido en su Admin.
Está construido con **TypeScript**, **React Router** y **Node.js**, **PostgreSQL**
con **Prisma**, webhooks de Shopify para recibir los pedidos, **Resend** para el
correo y **Google Cloud Run** para el despliegue.

### Estructura

```
generador/   datos simulados y script que arma las páginas
sitio/       lo que se publica: HTML y una hoja de estilos, bajo demo-embajadoras/
```

### Uso local

```bash
python3 generador/generar.py
```

```bash
python3 -m http.server 8000 --directory sitio
```

Después abre <http://localhost:8000/demo-embajadoras/>.

### Despliegue

Netlify publica la carpeta `sitio/` sin paso de build (ver `netlify.toml`).

### ¿Te interesa una solución así?

Agenda una conversación en
[Google Calendar](https://calendar.app.google/a8F5saYxdxWwMsWz7) o escribe por
[WhatsApp](https://wa.me/56985272032). Más en [ardillalab.com](https://ardillalab.com).

---

## English

Clickable demo of an **ambassador program for Shopify stores**. It shows how a brand
runs its ambassador team: contracts, commissions on referred sales, rewards, events
and email.

It is a reduced version of a real application. **Everything here is simulated**: the
store, the sales, the coins and the people (the names are a nod to *The Office*).
Actions that would change data do nothing: some explain what they would do on hover,
others open a "book a demo" notice.

### How it is built

- **HTML and CSS only.** Not a single line of JavaScript.
  - The "book a demo" notice uses the native `popover` attribute.
  - Tabs and filters use radios and checkboxes with `:checked` and `:has()`.
  - The dashboard bars are plain HTML boxes, so they restack when a group is
    unchecked. The total for every combination of groups is pre-rendered and CSS
    shows the matching one.
  - Search fields use `datalist`, the browser's native autocomplete.
- All 29 pages are built by a dependency-free Python script
  (`generador/generar.py`) from deterministic mock data (`generador/datos.py`).
  Only the `sitio/` folder is published.

### The original application

The real system is installed in the client's Shopify store, embedded in its Admin.
It is built with **TypeScript**, **React Router** and **Node.js**, **PostgreSQL**
with **Prisma**, Shopify webhooks, **Resend** for email and **Google Cloud Run**.

### Run locally

```bash
python3 generador/generar.py
```

```bash
python3 -m http.server 8000 --directory sitio
```

Then open <http://localhost:8000/demo-embajadoras/>.

---

Desarrollado por / Built by [ardillalab.com](https://ardillalab.com) · [MIT](LICENSE)
