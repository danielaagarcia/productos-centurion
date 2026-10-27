#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del catálogo comercial Centurión (resumido + completo).

Fuente de datos: productos.html (líneas, productos, imágenes, presentaciones,
colores por línea) — así el catálogo queda siempre alineado con la web.

Uso:
    python3 catalogo/build_catalogo.py
Genera:
    assets/catalogo/catalogo-centurion-resumido.pdf
    assets/catalogo/catalogo-centurion-completo.pdf
"""
import os, re, json, subprocess, html as htmlmod
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "catalogo")
BUILD_DIR = os.path.join(ROOT, "catalogo", "_build")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(BUILD_DIR, exist_ok=True)

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# ---------------------------------------------------------------------------
# 1. Extraer datos reales de productos.html
# ---------------------------------------------------------------------------
soup = BeautifulSoup(open(os.path.join(ROOT, "productos.html"), encoding="utf-8").read(), "html.parser")

LINEAS = []
for sec in soup.select(".linea-section"):
    header = sec.select_one(".linea-section-header")
    color = header.select_one(".linea-color-bar")["style"].split("background:")[1].strip()
    nombre = sec.select_one("h2").get_text(strip=True)
    desc = sec.select_one(".linea-desc").get_text(strip=True)
    productos = []
    for card in sec.select(".prod-card"):
        img = card.select_one(".prod-card-img img")
        productos.append({
            "nombre": card.select_one(".prod-card-name").get_text(strip=True),
            "img": img["src"] if img else None,
            "alt": img.get("alt", "") if img else "",
            "pres": [p.get_text(strip=True) for p in card.select(".pres-pill")],
        })
    LINEAS.append({"id": sec["id"], "nombre": nombre, "color": color, "desc": desc, "productos": productos})

TOTAL_PRODUCTOS = sum(len(l["productos"]) for l in LINEAS)

# NOTA: en productos.html, los 4 productos de la línea Salsas usan fotos de
# OTROS productos mal asignadas (frasco-chimichurri.png y frasco-provenzal.png
# son en realidad fotos de sobres de Ají Molido / Albahaca; Salsa Blanca usa
# la foto del Coco Rallado) -- bug preexistente del sitio, no de este script.
# En vez de mostrar una foto incorrecta en un catálogo comercial, se deja el
# espacio como "foto pendiente" para esos productos hasta tener la imagen real.
for _l in LINEAS:
    if _l["id"] == "prod-salsas":
        for _p in _l["productos"]:
            _p["img"] = None

# Exhibidores (de la carpeta assets/img/exhibidores, con nombre comercial y 1 descripcion breve)
EXHIBIDORES = [
    {"img": "assets/img/exhibidores/estanteria.jpg", "nombre": "Estantería de piso para mayoristas",
     "desc": "Exhibición de volumen para locales mayoristas y autoservicios grandes. Varios estantes, capacidad para toda la línea de especias y condimentos."},
    {"img": "assets/img/exhibidores/exhibidor-con-estante.jpg", "nombre": "Exhibidor de piso con estante superior",
     "desc": "Combina exhibición de piso con un estante superior para productos de mayor rotación. Ideal para almacenes y dietéticas."},
    {"img": "assets/img/exhibidores/exhibidor-mediano.jpg", "nombre": "Exhibidor mediano de piso",
     "desc": "Formato intermedio para locales con espacio acotado. Buena visibilidad de marca en punto de venta."},
    {"img": "assets/img/exhibidores/exhibidor-de-mesa.jpg", "nombre": "Exhibidor de mesa mediano",
     "desc": "Para mostrador o mesada. Pensado para productos de consulta rápida junto a la caja."},
    {"img": "assets/img/exhibidores/cajitas-cartulina.jpg", "nombre": "Cajas exhibidoras para góndola",
     "desc": "Caja de cartulina para ubicar sobres directamente en góndola, lista para reponer."},
    {"img": "assets/img/exhibidores/exhibidor-almacen.jpg", "nombre": "Exhibidor para almacén",
     "desc": "Pensado para el mostrador de almacenes de barrio, con los productos de mayor salida al frente."},
    {"img": "assets/img/exhibidores/exhibidor-dietética.jpg", "nombre": "Exhibidor para dietética",
     "desc": "Selección orientada a los productos más pedidos en dietéticas: hierbas, deshidratados y especias."},
    {"img": "assets/img/exhibidores/exhibidor-supermercado.jpg", "nombre": "Exhibidor para supermercado",
     "desc": "Formato de mayor capacidad para cadenas de supermercados e híper, con reposición simplificada."},
]

CONTACTO = {
    "tel": "011-4486-4495",
    "wa_mayorista": "5491163787553",
    "email": "info@productoscenturion.com.ar",
    "ig": "@productoscenturion",
    "web": "productoscenturion.com.ar",
    "ubicacion": "Gran Buenos Aires · Argentina",
    "razon_social": "Sierras Marianas S.A.",
}

FORMATOS = ["25 g", "50 g", "200 g", "250 g", "500 g", "1 Kg", "10 Kg"]

# ---------------------------------------------------------------------------
# 2. CSS compartido (mismos tokens que la web)
# ---------------------------------------------------------------------------
BASE_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --tierra:#8E4735;--mostaza:#C0AE6C;--naranja:#E47F33;--oliva:#888B59;
  --crema:#FAF4EC;--crema2:#F2E8D8;--dark:#1E1810;--dark2:#2C2218;
  --text:#2E2416;--muted:#7A6E60;--border:rgba(142,71,53,.14)
}
@page{size:A4;margin:0}
body{font-family:'Open Sans',sans-serif;color:var(--text);background:#fff}
img{display:block;max-width:100%}
.page{width:210mm;height:297mm;position:relative;overflow:hidden;background:var(--crema);page-break-after:always;padding:16mm 14mm}
.page:last-child{page-break-after:auto}
.pagenum{position:absolute;bottom:10mm;right:14mm;font-family:'Roboto Condensed',sans-serif;font-size:8pt;color:var(--muted);letter-spacing:.5px}
.eyebrow{font-family:'Open Sans Condensed',sans-serif;font-size:9pt;font-weight:700;letter-spacing:2.5px;text-transform:uppercase}
.logo-badge{display:inline-flex;align-items:center;justify-content:center;background:#C8102E;border-radius:0 0 16px 16px;padding:10px 26px 8px;position:relative}
.logo-badge::after{content:'';position:absolute;top:100%;left:0;right:0;height:10px;background:linear-gradient(135deg,transparent 49.5%,#C8102E 50%) left/20px 10px no-repeat,linear-gradient(45deg,transparent 49.5%,#C8102E 50%) right/20px 10px no-repeat}
.logo-badge span{font-family:'Roboto Slab',serif;font-weight:900;font-style:italic;font-size:26pt;color:#FFD400;letter-spacing:-.5px}

/* ---- PORTADA / CONTRA ---- */
.cover{background:var(--dark);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:18px}
.cover .eyebrow{color:var(--mostaza)}
.cover h1{font-family:'Roboto Slab',serif;font-weight:900;font-size:34pt;line-height:1.1;max-width:140mm}
.cover .sub{font-family:'Open Sans',sans-serif;font-weight:300;font-size:12pt;color:rgba(255,255,255,.65);max-width:120mm}
.cover .rule{width:52px;height:3px;background:var(--mostaza)}
.cover .foot{position:absolute;bottom:16mm;font-size:9pt;color:rgba(255,255,255,.4);font-family:'Open Sans Condensed',sans-serif;letter-spacing:2px;text-transform:uppercase}
.back{background:var(--dark);color:#fff;display:flex;flex-direction:column;justify-content:center;gap:28px}
.back h2{font-family:'Roboto Slab',serif;font-size:22pt;color:#fff}
.back .msg{font-style:italic;color:var(--mostaza);font-family:'Roboto Slab',serif;font-size:13pt}
.back .contact-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px 28px;margin-top:12px}
.back .contact-item{border-left:2px solid var(--mostaza);padding-left:12px}
.back .contact-item .k{font-family:'Open Sans Condensed',sans-serif;font-size:8.5pt;letter-spacing:2px;text-transform:uppercase;color:var(--mostaza);margin-bottom:3px}
.back .contact-item .v{font-size:11pt;color:#fff}
.back .legal{font-size:8pt;color:rgba(255,255,255,.35);margin-top:20px;line-height:1.6}

/* ---- INDICE ---- */
.indice h2{font-family:'Roboto Slab',serif;font-size:24pt;color:var(--dark);margin-bottom:4px}
.indice .sub{color:var(--muted);font-size:10.5pt;margin-bottom:28px}
.indice-list{display:flex;flex-direction:column}
.indice-row{display:flex;align-items:center;gap:14px;padding:13px 0;border-bottom:1px solid var(--border)}
.indice-dot{width:14px;height:14px;border-radius:4px;flex-shrink:0}
.indice-name{font-family:'Roboto Slab',serif;font-weight:700;font-size:13pt;color:var(--dark);flex:0 0 auto;width:62mm}
.indice-leader{flex:1;border-bottom:1px dotted var(--border);margin:0 10px 4px}
.indice-count{font-family:'Roboto Condensed',sans-serif;font-size:9pt;color:var(--muted);width:24mm}
.indice-page{font-family:'Roboto Slab',serif;font-weight:700;font-size:11pt;color:var(--tierra);width:10mm;text-align:right}

/* ---- APERTURA DE LINEA ---- */
.linea-open .topband{height:30mm;margin:-16mm -14mm 10mm;display:flex;align-items:center;justify-content:center;position:relative}
.linea-open .eyebrow{color:var(--tierra);margin-bottom:6px}
.linea-open h2{font-family:'Roboto Slab',serif;font-weight:900;font-size:30pt;color:var(--dark);text-transform:uppercase;letter-spacing:.5px}
.linea-open .rule{width:46px;height:3px;margin:10px 0 14px}
.linea-open .desc{font-size:11pt;font-weight:600;color:var(--text);max-width:80mm;line-height:1.5;margin-bottom:10mm}
.linea-open .cols{display:grid;grid-template-columns:72mm 1fr;gap:12mm}
.linea-open .hero-frame{border:1.5px dashed;border-radius:2px;padding:14px;position:relative}
.linea-open .hero-frame img{width:100%;height:56mm;object-fit:contain}
.linea-open .hero-frame .noimg{height:56mm;display:flex;align-items:center;justify-content:center;text-align:center;font-family:'Open Sans Condensed',sans-serif;font-size:8.5pt;letter-spacing:1px;text-transform:uppercase;color:var(--muted)}
.linea-open .hero-name{font-family:'Open Sans Condensed',sans-serif;font-weight:700;font-size:10pt;letter-spacing:1px;text-transform:uppercase;text-align:center;margin-top:10px;border-top:2px solid;padding-top:8px}
.linea-open .hero-pres{text-align:center;font-family:'Roboto Condensed',sans-serif;font-size:8.5pt;color:var(--muted);margin-top:4px}
.linea-open .list-label{font-family:'Open Sans Condensed',sans-serif;font-weight:700;font-size:9pt;letter-spacing:1.5px;text-transform:uppercase;color:var(--tierra);margin-bottom:8px;border-bottom:2px solid var(--tierra);padding-bottom:6px}
.linea-open .list-flow{font-size:10.5pt;line-height:2;color:var(--text)}
.linea-open .list-flow .sep{color:var(--mostaza);margin:0 6px}

/* ---- GRILLA DE PRODUCTOS (catalogo completo) ---- */
.prodpage .headbar{display:flex;align-items:center;gap:10px;margin-bottom:9mm;border-bottom:2px solid;padding-bottom:8px}
.prodpage .headbar h3{font-family:'Roboto Slab',serif;font-weight:700;font-size:16pt;color:var(--dark);text-transform:uppercase}
.prodpage .headbar .tag{margin-left:auto;font-family:'Open Sans Condensed',sans-serif;font-size:8.5pt;color:var(--muted);letter-spacing:1px}
.pgrid{display:grid;grid-template-columns:1fr 1fr;gap:8mm 8mm}
.pcard{border:1px solid var(--border);border-radius:4px;padding:10px;display:flex;flex-direction:column}
.pcard .pimg{height:36mm;display:flex;align-items:center;justify-content:center;margin-bottom:8px}
.pcard .pimg img{max-height:100%;max-width:100%;object-fit:contain}
.pcard .pimg .noimg{text-align:center;font-family:'Open Sans Condensed',sans-serif;font-size:7.5pt;letter-spacing:1px;text-transform:uppercase;color:var(--muted)}
.pcard .pbar{height:3px;margin-bottom:8px}
.pcard .pname{font-family:'Roboto Slab',serif;font-weight:700;font-size:10.5pt;color:var(--dark);margin-bottom:4px}
.pcard .ppres{display:flex;flex-wrap:wrap;gap:4px}
.pcard .ppill{font-family:'Roboto Condensed',sans-serif;font-size:7.5pt;color:var(--muted);background:var(--crema2);border-radius:3px;padding:2px 6px}

/* ---- FORMATOS / COLLAGE ---- */
.formatos h2{font-family:'Roboto Slab',serif;font-size:22pt;color:var(--dark);margin-bottom:6px}
.formatos .sub{color:var(--muted);font-size:10.5pt;max-width:120mm;margin-bottom:12mm;line-height:1.6}
.formatos .fgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:8mm;margin-bottom:12mm}
.formatos .fcard{text-align:center}
.formatos .fcard .fimg{height:38mm;display:flex;align-items:center;justify-content:center;background:var(--crema2);border-radius:6px;margin-bottom:8px}
.formatos .fcard .fimg img{max-height:80%;max-width:80%;object-fit:contain}
.formatos .fcard .flabel{font-family:'Open Sans Condensed',sans-serif;font-size:9pt;font-weight:700;letter-spacing:.5px;color:var(--muted);text-transform:uppercase}
.formatos .range{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;border-top:1px solid var(--border);padding-top:10mm}
.formatos .range span{font-family:'Roboto Slab',serif;font-weight:700;font-size:12pt;color:var(--tierra);background:var(--crema2);border-radius:20px;padding:8px 18px}
.formatos .note{text-align:center;color:var(--muted);font-size:9pt;margin-top:10mm;font-style:italic}

/* ---- EXHIBIDORES ---- */
.exhib h2{font-family:'Roboto Slab',serif;font-size:22pt;color:var(--dark);margin-bottom:6px}
.exhib .sub{color:var(--muted);font-size:10.5pt;max-width:130mm;margin-bottom:10mm;line-height:1.6}
.exhib .egrid{display:grid;grid-template-columns:1fr 1fr;gap:7mm}
.exhib .ecard{border:1px solid var(--border);border-radius:5px;overflow:hidden}
.exhib .ecard .eimg{height:42mm;background:var(--crema2)}
.exhib .ecard .eimg img{width:100%;height:100%;object-fit:cover}
.exhib .ecard .ebody{padding:10px 12px}
.exhib .ecard .ename{font-family:'Roboto Slab',serif;font-weight:700;font-size:10.5pt;color:var(--dark);margin-bottom:4px}
.exhib .ecard .edesc{font-size:8.5pt;color:var(--muted);line-height:1.6}

/* ---- PLACEHOLDER (identidad / packaging a incorporar) ---- */
.idpack h2{font-family:'Roboto Slab',serif;font-size:22pt;color:var(--dark);margin-bottom:6px}
.idpack .sub{color:var(--muted);font-size:10.5pt;max-width:130mm;margin-bottom:10mm;line-height:1.6}
.idpack .igrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6mm}
.idpack .iph{height:44mm;border:2px dashed var(--mostaza);border-radius:6px;background:var(--crema2);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:10px;gap:4px}
.idpack .iph .t{font-family:'Open Sans Condensed',sans-serif;font-weight:700;font-size:8pt;letter-spacing:1px;text-transform:uppercase;color:var(--tierra)}
.idpack .iph .s{font-size:7.5pt;color:var(--muted)}
"""

FONT_LINK = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400;600;700;900&family=Open+Sans:ital,wght@0,300;0,400;0,600;1,300&family=Open+Sans+Condensed:wght@300;700&family=Roboto+Condensed:wght@400;700&display=swap" rel="stylesheet">'


def logo_html(on_dark=True):
    return '<div class="logo-badge"><span>Centurión</span></div>'


def page(content, klass="", pagenum=None, extra_style=""):
    pn = f'<div class="pagenum">PÁG. {pagenum}</div>' if pagenum else ""
    return f'<section class="page {klass}" style="{extra_style}">{content}{pn}</section>'


def cover_page(subtitle, foot="CATÁLOGO COMERCIAL · USO MAYORISTA"):
    return page(f"""
      {logo_html()}
      <div class="rule"></div>
      <div class="eyebrow">Sierras Marianas S.A. · Desde 1959</div>
      <h1>Catálogo {subtitle}</h1>
      <p class="sub">Especias, condimentos, hierbas aromáticas, repostería, salsas y alimentos instantáneos. {len(LINEAS)} líneas, {TOTAL_PRODUCTOS}+ referencias.</p>
      <div class="foot">{foot}</div>
    """, klass="cover")


def back_page():
    items = [
        ("Teléfono", CONTACTO["tel"]),
        ("WhatsApp mayorista", "011 6378-7553"),
        ("Email", CONTACTO["email"]),
        ("Instagram", CONTACTO["ig"]),
        ("Web", CONTACTO["web"]),
        ("Ubicación", CONTACTO["ubicacion"]),
    ]
    grid = "".join(f'<div class="contact-item"><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in items)
    return page(f"""
      {logo_html()}
      <h2>Seguimos creciendo desde 1959</h2>
      <p class="msg">"Producto de calidad, precio justo, trato directo."</p>
      <div class="contact-grid">{grid}</div>
      <div class="legal">{CONTACTO['razon_social']} · {CONTACTO['ubicacion']} · Industria Argentina.<br>
      Catálogo de referencia — no incluye precios. Precios y condiciones comerciales se comunican por separado y pueden actualizarse sin previo aviso.<br>
      Las imágenes de packaging son ilustrativas; el producto final puede variar levemente en diseño de etiqueta.</div>
    """, klass="back")


def indice_page(line_pages, pagenum):
    rows = ""
    for l in LINEAS:
        rows += f"""<div class="indice-row">
          <div class="indice-dot" style="background:{l['color']}"></div>
          <div class="indice-name">{l['nombre']}</div>
          <div class="indice-leader"></div>
          <div class="indice-count">{len(l['productos'])} productos</div>
          <div class="indice-page">{line_pages[l['id']]}</div>
        </div>"""
    return page(f"""
      <div class="indice">
        <div class="eyebrow" style="color:var(--tierra)">Mapa de líneas</div>
        <h2>Índice</h2>
        <p class="sub">{len(LINEAS)} líneas de producto · {TOTAL_PRODUCTOS}+ referencias</p>
        <div class="indice-list">{rows}</div>
      </div>
    """, pagenum=pagenum)


def linea_open_page(l, pagenum):
    # preferimos como foto destacada el primer producto de la linea que SI tenga imagen
    hero = next((p for p in l["productos"] if p["img"]), l["productos"][0] if l["productos"] else None)
    hero_block = ""
    if hero:
        pres_txt = " · ".join(hero["pres"]) if hero["pres"] else "Consultar presentaciones"
        img_html = f'<img src="{hero["img"]}" alt="{htmlmod.escape(hero["alt"])}">' if hero["img"] else '<div class="noimg">Foto<br>pendiente</div>'
        hero_block = f"""<div class="hero-frame" style="border-color:{l['color']}">
          {img_html}
          <div class="hero-name" style="border-color:{l['color']};color:{l['color']}">{hero['nombre']}</div>
          <div class="hero-pres">{pres_txt}</div>
        </div>"""
    names = " <span class='sep'>•</span> ".join(p["nombre"] for p in l["productos"])
    return page(f"""
      <div class="linea-open">
        <div class="topband" style="background:{l['color']}">{logo_html()}</div>
        <div class="eyebrow">Línea</div>
        <h2>{l['nombre']}</h2>
        <div class="rule" style="background:{l['color']}"></div>
        <p class="desc">{l['desc']}</p>
        <div class="cols">
          {hero_block}
          <div>
            <div class="list-label">Productos de la línea</div>
            <div class="list-flow">{names}</div>
          </div>
        </div>
      </div>
    """, pagenum=pagenum)


def product_grid_page(l, chunk, idx, total_chunks, pagenum):
    cards = ""
    for p in chunk:
        pres = "".join(f'<span class="ppill">{x}</span>' for x in (p["pres"] or ["Consultar"]))
        img_html = f'<img src="{p["img"]}" alt="{htmlmod.escape(p["alt"])}">' if p["img"] else '<div class="noimg">Foto<br>pendiente</div>'
        cards += f"""<div class="pcard">
          <div class="pimg">{img_html}</div>
          <div class="pbar" style="background:{l['color']}"></div>
          <div class="pname">{p['nombre']}</div>
          <div class="ppres">{pres}</div>
        </div>"""
    tag = f"{l['nombre']} · {idx}/{total_chunks}" if total_chunks > 1 else l["nombre"]
    return page(f"""
      <div class="prodpage">
        <div class="headbar" style="border-color:{l['color']}"><h3>{l['nombre']}</h3><span class="tag">{tag}</span></div>
        <div class="pgrid">{cards}</div>
      </div>
    """, pagenum=pagenum)


def formatos_page(pagenum):
    # elegimos 3 formas de envase representativas ya existentes como foto real
    muestras = [
        ("assets/img/productos/sobre-pimenton.png", "Sobres flexibles"),
        ("assets/img/productos/caja-pure-papas.png", "Cajas / estuches"),
        ("assets/img/productos/caja-sopa-esparrago.png", "Estuches gastronómicos"),
    ]
    fcards = "".join(f'<div class="fcard"><div class="fimg"><img src="{src}" alt="{lbl}"></div><div class="flabel">{lbl}</div></div>' for src, lbl in muestras)
    rng = "".join(f"<span>{f}</span>" for f in FORMATOS)
    return page(f"""
      <div class="formatos">
        <div class="eyebrow" style="color:var(--tierra)">Presentaciones</div>
        <h2>Formatos disponibles</h2>
        <p class="sub">La mayoría de nuestros sobres se presenta en 25 g. Según el producto y el canal, también ofrecemos los siguientes gramajes:</p>
        <div class="fgrid">{fcards}</div>
        <div class="range">{rng}</div>
        <p class="note">Los formatos disponibles varían según el producto. Consultá el detalle en cada línea o con tu vendedor.</p>
      </div>
    """, pagenum=pagenum)


def exhibidores_pages(pagenum_start):
    chunks = [EXHIBIDORES[i:i+4] for i in range(0, len(EXHIBIDORES), 4)]
    out = []
    for ci, chunk in enumerate(chunks):
        cards = "".join(f"""<div class="ecard">
            <div class="eimg"><img src="{e['img']}" alt="{e['nombre']}"></div>
            <div class="ebody"><div class="ename">{e['nombre']}</div><div class="edesc">{e['desc']}</div></div>
          </div>""" for e in chunk)
        head = """<div class="eyebrow" style="color:var(--tierra)">Materiales de exhibición</div><h2>Exhibidores para el punto de venta</h2><p class="sub">Materiales de exhibición disponibles para distribuidores y comercios, pensados para cada tipo de local.</p>""" if ci == 0 else '<div class="eyebrow" style="color:var(--tierra)">Materiales de exhibición</div><h2>Exhibidores (cont.)</h2>'
        out.append(page(f'<div class="exhib">{head}<div class="egrid">{cards}</div></div>', pagenum=pagenum_start + ci))
    return out


def identidad_page(pagenum):
    items = [
        ("Recetas en el packaging", "Simple Chef: ideas de uso impresas en cada sobre"),
        ("Ingredientes", "Detalle de composición en el envase"),
        ("Industria Argentina", "Sello de origen nacional"),
        ("Producto en góndola", "Cómo se ve la línea en el local"),
        ("Caja / estuche exhibidor", "Presentación de venta en el mostrador"),
        ("Exhibidor en mesada de almacén", "Material de punto de venta en uso"),
    ]
    cards = "".join(f'<div class="iph"><div class="t">{t}</div><div class="s">{s}</div></div>' for t, s in items)
    return page(f"""
      <div class="idpack">
        <div class="eyebrow" style="color:var(--tierra)">Marca e identidad</div>
        <h2>Nuestra presencia en el punto de venta</h2>
        <p class="sub">Espacio reservado para fotografía real de producto en uso — packaging, góndola y materiales de exhibición. Se incorpora cuando esté disponible.</p>
        <div class="igrid">{cards}</div>
      </div>
    """, pagenum=pagenum)


# ---------------------------------------------------------------------------
# 3. Armado de paginas — CATALOGO RESUMIDO
# ---------------------------------------------------------------------------
def build_resumido():
    # plan de paginas: 1 portada, 2 indice, 3..3+n-1 lineas, luego contra
    n = len(LINEAS)
    line_pages = {l["id"]: 3 + i for i, l in enumerate(LINEAS)}
    back_pn = 3 + n
    pages = [cover_page("Resumido 2026")]
    pages.append(indice_page(line_pages, pagenum=2))
    for l in LINEAS:
        pages.append(linea_open_page(l, pagenum=line_pages[l["id"]]))
    pages.append(back_page())
    html_doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">{FONT_LINK}<style>{BASE_CSS}</style></head><body>{''.join(pages)}</body></html>"""
    html_doc = html_doc.replace('src="assets/', 'src="../../assets/')
    out_html = os.path.join(BUILD_DIR, "resumido.html")
    open(out_html, "w", encoding="utf-8").write(html_doc)
    return out_html


# ---------------------------------------------------------------------------
# 4. Armado de paginas — CATALOGO COMPLETO
# ---------------------------------------------------------------------------
def chunk_list(lst, n):
    return [lst[i:i+n] for i in range(0, len(lst), n)]


def build_completo():
    CHUNK = 6
    # Paso 1: planificar numeros de pagina
    pn = 3  # 1 portada, 2 indice
    line_pages = {}
    plan = []  # (tipo, line, chunk_info)
    for l in LINEAS:
        line_pages[l["id"]] = pn
        plan.append(("open", l, None))
        pn += 1
        chunks = chunk_list(l["productos"], CHUNK)
        for i, ch in enumerate(chunks):
            plan.append(("grid", l, (ch, i + 1, len(chunks))))
            pn += 1
    formatos_pn = pn; pn += 1
    exhib_chunks = [EXHIBIDORES[i:i+4] for i in range(0, len(EXHIBIDORES), 4)]
    exhib_pn_start = pn; pn += len(exhib_chunks)
    idpack_pn = pn; pn += 1
    back_pn = pn

    pages = [cover_page("Completo 2026", foot="CATÁLOGO COMERCIAL · USO MAYORISTA · VERSIÓN COMPLETA")]
    pages.append(indice_page(line_pages, pagenum=2))
    for tipo, l, info in plan:
        if tipo == "open":
            pages.append(linea_open_page(l, pagenum=line_pages[l["id"]]))
        else:
            ch, idx, total = info
            # calcular pagenum real para este chunk
            pass
    # segunda pasada real con pagenum correctos (recalculamos igual que el plan)
    pages = [cover_page("Completo 2026", foot="CATÁLOGO COMERCIAL · USO MAYORISTA · VERSIÓN COMPLETA")]
    pages.append(indice_page(line_pages, pagenum=2))
    pn = 3
    for l in LINEAS:
        pages.append(linea_open_page(l, pagenum=pn)); pn += 1
        chunks = chunk_list(l["productos"], CHUNK)
        for i, ch in enumerate(chunks):
            pages.append(product_grid_page(l, ch, i + 1, len(chunks), pagenum=pn)); pn += 1
    pages.append(formatos_page(pagenum=formatos_pn))
    pages.extend(exhibidores_pages(pagenum_start=exhib_pn_start))
    pages.append(identidad_page(pagenum=idpack_pn))
    pages.append(back_page())

    html_doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">{FONT_LINK}<style>{BASE_CSS}</style></head><body>{''.join(pages)}</body></html>"""
    html_doc = html_doc.replace('src="assets/', 'src="../../assets/')
    out_html = os.path.join(BUILD_DIR, "completo.html")
    open(out_html, "w", encoding="utf-8").write(html_doc)
    return out_html


def html_to_pdf(html_path, pdf_out, port):
    rel = os.path.relpath(html_path, ROOT)
    url = f"http://127.0.0.1:{port}/{rel}"
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={pdf_out}", "--print-to-pdf-no-header",
           "--run-all-compositor-stages-before-draw", "--virtual-time-budget=8000",
           url]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    import sys, time, http.server, threading, socketserver

    os.chdir(ROOT)
    PORT = 8971
    handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(0.5)
    try:
        r_html = build_resumido()
        c_html = build_completo()
        html_to_pdf(r_html, os.path.join(OUT_DIR, "catalogo-centurion-resumido.pdf"), PORT)
        html_to_pdf(c_html, os.path.join(OUT_DIR, "catalogo-centurion-completo.pdf"), PORT)
        print("OK: PDFs generados en", OUT_DIR)
    finally:
        httpd.shutdown()
