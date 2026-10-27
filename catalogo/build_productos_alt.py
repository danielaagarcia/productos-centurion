#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera productos-alt.html: una reversión de productos.html con una
estructura de página inspirada en alicante.com.ar/productos/ (grilla de
píldoras con ícono por línea arriba, y cada línea como una franja de color
ancha en vez de sidebar + encabezado fino) pero con la identidad visual
propia de Centurión (tierra/mostaza/crema, tipografías y colores por línea
ya definidos en productos.html). Misma fuente de datos que productos.html
y que el catálogo PDF, para que las tres piezas queden alineadas.

Uso: python3 catalogo/build_productos_alt.py
"""
import os
import html as htmlmod
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "productos.html")
OUT = os.path.join(ROOT, "productos-alt.html")

soup = BeautifulSoup(open(SRC, encoding="utf-8").read(), "html.parser")

# ---------------------------------------------------------------------------
# 1. Datos (mismo parseo que el generador del catálogo)
# ---------------------------------------------------------------------------
LINEAS = []
for sec in soup.select(".linea-section"):
    header = sec.select_one(".linea-section-header")
    color = header.select_one(".linea-color-bar")["style"].split("background:")[1].strip()
    nombre = sec.select_one("h2").get_text(strip=True)
    desc = sec.select_one(".linea-desc").get_text(strip=True)
    productos = []
    for card in sec.select(".prod-card"):
        img = card.select_one(".prod-card-img img")
        pres = [p.get_text(strip=True) for p in card.select(".pres-pill")]
        productos.append({
            "nombre": card.select_one(".prod-card-name").get_text(strip=True),
            "img": img["src"] if img else None,
            "alt": img.get("alt", "") if img else "",
            "pres": pres,
        })
    LINEAS.append({"id": sec["id"], "nombre": nombre, "color": color, "desc": desc, "productos": productos})

TOTAL_PRODUCTOS = sum(len(l["productos"]) for l in LINEAS)

# Mismo bug de datos que en el catálogo: estas 2 imágenes son en realidad
# fotos de sobres mal asignadas a la línea Salsas (ver catalogo/build_catalogo.py)
for l in LINEAS:
    if l["id"] == "prod-salsas":
        for p in l["productos"]:
            p["img"] = None

# Ícono lineal simple por línea (mismo estilo que los íconos ya usados en el sitio)
ICONS = {
    "prod-especias": '<path d="M9 3c3 0 4.2 2.1 4.2 2.1S16 12.5 12 18.5c-2 3-6.7 2-7.6-1.8C2.8 11.8 6 3 9 3z"/><path d="M9 3c1-1.2 3-2 4-1"/>',
    "prod-hierbas": '<path d="M4 20C4 10 12 4 20 4c0 8-6 16-16 16z"/><path d="M4 20 14 10"/>',
    "prod-condimentos": '<path d="M8 2h8l-1 4H9z"/><path d="M8 6h8l1 13.5A2 2 0 0 1 15 22H9a2 2 0 0 1-2-2.5z"/><circle cx="10" cy="11" r=".7" fill="currentColor" stroke="none"/><circle cx="14" cy="11" r=".7" fill="currentColor" stroke="none"/><circle cx="12" cy="14.5" r=".7" fill="currentColor" stroke="none"/>',
    "prod-deshidratados": '<circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/>',
    "prod-salsas": '<path d="M9 2h6v3.2l2 2.3V20a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2V7.5l2-2.3z"/><path d="M7 12h10"/>',
    "prod-reposteria": '<path d="M12 2v8"/><path d="M8 10c-2.2 0-3.3 2-3.3 4.3S6.5 18 8 18M16 10c2.2 0 3.3 2 3.3 4.3S17.5 18 16 18M12 10c-1.3 1.6-1.3 6.4 0 10M12 10c1.3 1.6 1.3 6.4 0 10"/><path d="M8 20h8"/>',
    "prod-instantaneos": '<path d="M3 11h18l-1.6 7.2A2 2 0 0 1 17.5 20h-11a2 2 0 0 1-1.9-1.8z"/><path d="M12 11V8M9 5c0-1 1-1.2 1-2.2M12 5c0-1 1-1.2 1-2.2M15 5c0-1 1-1.2 1-2.2"/>',
    "prod-postres": '<path d="M6 3h12l-1.1 15.2A2 2 0 0 1 14.9 20H9.1a2 2 0 0 1-2-1.8z"/><path d="M6 8h12"/><path d="M12 8v-5"/>',
    "prod-frutos": '<path d="M12 9c3.3 0 5.3 2.6 5.3 6a5.3 5.3 0 0 1-10.6 0c0-3.4 2-6 5.3-6z"/><path d="M8.3 9c0-2.2 1.3-4 3.7-4s3.7 1.8 3.7 4"/>',
}

# ---------------------------------------------------------------------------
# 2. HTML base: tomamos el <head>, navbar, mob-nav y footer TAL CUAL de
#    productos.html para mantener coherencia de marca y enlaces activos.
# ---------------------------------------------------------------------------
head_html = str(soup.head)
navbar = soup.select_one("nav.navbar")
mobnav = soup.select_one(".mob-nav")
footer = soup.select_one("footer")
wafloat = soup.select_one("a.wa-float")

navbar_html = str(navbar).replace('class="nav-active"', '').replace(
    'href="productos.html"', 'href="productos.html"'
)
# marcar activo el link de Productos y actualizar el link de "Productos" a esta pagina alternativa internamente (misma URL de nav, el usuario llega por la nueva)
navbar_html = str(navbar)
mobnav_html = str(mobnav)
footer_html = str(footer)
wafloat_html = str(wafloat)

CSS_EXTRA = """
@font-face{font-family:'Fertigo Pro';src:url('assets/fonts/FertigoPro-Regular.woff2') format('woff2');font-weight:400;font-style:normal;font-display:swap}
/* ======= REVERSIÓN ESTILO "LÍNEAS" (alt) ======= */
.alt-hero{background:var(--dark2);padding:108px 0 40px;text-align:center}
.alt-hero .eyebrow{color:var(--mostaza);justify-content:center}
.alt-hero h1{font-family:'Roboto Slab',serif;font-weight:900;font-size:clamp(26px,4vw,40px);color:#fff;margin:10px 0 8px}
.alt-hero p{color:rgba(255,255,255,.55);font-size:14px;max-width:520px;margin:0 auto}
.alt-pillbar{background:linear-gradient(135deg,var(--crema2),#fff);border-bottom:1px solid var(--border);padding:26px 0}
.alt-pillgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px}
.alt-pill{display:flex;align-items:center;gap:10px;background:#fff;border:1px solid var(--border);border-radius:10px;padding:12px 16px;text-decoration:none;color:var(--dark);font-family:'Roboto Slab',serif;font-weight:700;font-size:13px;transition:all .2s;box-shadow:0 2px 6px rgba(30,24,16,.04)}
.alt-pill:hover{border-color:var(--tierra);transform:translateY(-1px);box-shadow:0 6px 16px rgba(142,71,53,.12)}
.alt-pill svg{width:20px;height:20px;stroke:var(--tierra);fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;flex-shrink:0}
.alt-pill span{line-height:1.25}
.alt-wrap{background:var(--crema2)}
.alt-linea{padding:46px 0 10px;scroll-margin-top:84px}
.alt-head{display:flex;flex-direction:column;align-items:center;text-align:center;margin-bottom:14px}
.alt-head-icon{width:58px;height:58px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin-bottom:16px;box-shadow:0 2px 10px rgba(30,24,16,.07)}
.alt-head-icon svg{width:27px;height:27px;fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.alt-head h2{font-family:'Fertigo Pro','Roboto Slab',serif;font-weight:400;font-size:34px;color:var(--dark);letter-spacing:.3px;line-height:1.1;margin-bottom:12px}
.alt-head-rule{width:54px;height:3px;border-radius:2px}
.alt-desc{text-align:center;color:var(--muted);font-size:13px;max-width:460px;margin:14px auto 30px}

/* ---- Carrusel de productos por línea ---- */
.alt-carousel{position:relative}
.alt-grid{display:flex;gap:22px;overflow-x:auto;scroll-snap-type:x proximity;padding:4px 2px 20px;scroll-behavior:smooth;-webkit-overflow-scrolling:touch;scrollbar-width:thin;scrollbar-color:var(--tierra) transparent}
.alt-grid::-webkit-scrollbar{height:6px}
.alt-grid::-webkit-scrollbar-track{background:transparent}
.alt-grid::-webkit-scrollbar-thumb{background:var(--tierra);border-radius:3px}
.alt-card{flex:0 0 340px;scroll-snap-align:start;text-align:center}
.alt-card-img{position:relative;height:360px;display:flex;align-items:center;justify-content:center;background:#fff;border-radius:14px;margin-bottom:16px;box-shadow:0 2px 10px rgba(30,24,16,.06);transition:transform .2s}
.alt-card:hover .alt-card-img{transform:translateY(-3px);box-shadow:0 10px 22px rgba(30,24,16,.1)}
.alt-card-img img{max-height:330px;max-width:290px;object-fit:contain;filter:drop-shadow(0 6px 12px rgba(0,0,0,.14))}
.alt-card-img .noimg{font-family:'Open Sans Condensed',sans-serif;font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--muted)}
.alt-card-dot{position:absolute;top:10px;left:10px;width:10px;height:10px;border-radius:50%}
.alt-card-name{font-family:'Roboto Slab',serif;font-weight:700;font-size:16px;color:var(--dark);margin-bottom:8px;line-height:1.3}
.alt-card-pres{display:flex;flex-wrap:wrap;gap:4px;justify-content:center;margin-bottom:10px}
.alt-card-cta{font-family:'Open Sans Condensed',sans-serif;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--tierra);text-decoration:none}
.alt-card-cta:hover{text-decoration:underline}
.alt-car-nav{position:absolute;top:150px;width:46px;height:46px;border-radius:50%;background:#fff;border:1px solid var(--border);display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 6px 16px rgba(30,24,16,.14);z-index:5;transition:all .15s}
.alt-car-nav:hover{border-color:var(--tierra);transform:translateY(-1px)}
.alt-car-nav svg{width:20px;height:20px;stroke:var(--tierra);fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.alt-car-prev{left:-23px}
.alt-car-next{right:-23px}

/* ---- Navegación vertical fija (scrollspy) ---- */
.alt-dotnav{position:fixed;right:20px;top:50%;transform:translateY(-50%);z-index:80;display:flex;flex-direction:column;align-items:center;gap:13px}
.alt-dotnav a{position:relative;width:11px;height:11px;border-radius:50%;box-shadow:0 0 0 2px rgba(255,255,255,.7);transition:transform .2s,box-shadow .2s}
.alt-dotnav a:hover,.alt-dotnav a.active{transform:scale(1.35)}
.alt-dotnav a.active{box-shadow:0 0 0 2px rgba(255,255,255,.9),0 0 0 3.5px currentColor}
.alt-dotnav a span{position:absolute;right:22px;top:50%;transform:translateY(-50%);white-space:nowrap;background:var(--dark);color:#fff;font-family:'Open Sans Condensed',sans-serif;font-weight:700;font-size:11px;letter-spacing:.6px;text-transform:uppercase;padding:6px 11px;border-radius:5px;opacity:0;pointer-events:none;transition:opacity .15s}
.alt-dotnav a:hover span{opacity:1}
@media(max-width:1300px){.alt-dotnav{display:none}}
@media(max-width:768px){
  .alt-hero{padding:92px 0 32px}
  .alt-head-icon{width:48px;height:48px;margin-bottom:12px}
  .alt-head-icon svg{width:22px;height:22px}
  .alt-head h2{font-size:25px}
  .alt-card{flex:0 0 80%}
  .alt-card-img{height:290px}
  .alt-card-img img{max-height:260px;max-width:230px}
  .alt-car-nav{display:none}
}
"""

PILLS = "".join(
    f'<a href="#{l["id"]}" class="alt-pill"><svg viewBox="0 0 24 24">{ICONS.get(l["id"],"")}</svg><span>{l["nombre"]}</span></a>'
    for l in LINEAS
)

DOTNAV = "".join(
    f'<a href="#{l["id"]}" data-target="{l["id"]}" style="background:{l["color"]};color:{l["color"]}"><span>{l["nombre"]}</span></a>'
    for l in LINEAS
)

def card_html(p, color):
    img_html = f'<img src="{p["img"]}" alt="{htmlmod.escape(p["alt"])}" loading="lazy">' if p["img"] else '<div class="noimg">Foto<br>pendiente</div>'
    pres = "".join(f'<span class="pres-pill">{x}</span>' for x in p["pres"])
    return f"""<div class="alt-card fi">
      <div class="alt-card-img"><div class="alt-card-dot" style="background:{color}"></div>{img_html}</div>
      <div class="alt-card-name">{p['nombre']}</div>
      <div class="alt-card-pres">{pres}</div>
      <a href="contacto.html" class="alt-card-cta">Consultar precio &#8594;</a>
    </div>"""

ARROW_L = '<svg viewBox="0 0 24 24"><path d="M15 18l-6-6 6-6"/></svg>'
ARROW_R = '<svg viewBox="0 0 24 24"><path d="M9 18l6-6-6-6"/></svg>'

sections = []
for l in LINEAS:
    cards = "".join(card_html(p, l["color"]) for p in l["productos"])
    grid_id = f"grid-{l['id']}"
    nav_html = ""
    if len(l["productos"]) > 3:
        nav_html = f"""<button type="button" class="alt-car-nav alt-car-prev" data-target="{grid_id}" aria-label="Anterior">{ARROW_L}</button><button type="button" class="alt-car-nav alt-car-next" data-target="{grid_id}" aria-label="Siguiente">{ARROW_R}</button>"""
    sections.append(f"""
<div class="alt-linea" id="{l['id']}">
  <div class="container">
    <div class="alt-head fi">
      <div class="alt-head-icon" style="background:color-mix(in srgb, {l['color']} 14%, #fff)">
        <svg viewBox="0 0 24 24" style="stroke:{l['color']}">{ICONS.get(l['id'],'')}</svg>
      </div>
      <h2>{l['nombre']}</h2>
      <div class="alt-head-rule" style="background:{l['color']}"></div>
    </div>
    <p class="alt-desc fi">{l['desc']}</p>
    <div class="alt-carousel fi">
      {nav_html}
      <div class="alt-grid" id="{grid_id}">{cards}</div>
    </div>
  </div>
</div>""")

body_main = f"""
<section class="alt-hero">
  <div class="container">
    <div class="eyebrow" style="display:flex;align-items:center;gap:10px">Catálogo completo</div>
    <h1>Nuestras líneas de producto</h1>
    <p>{len(LINEAS)} líneas, {TOTAL_PRODUCTOS}+ referencias. Sin precios en la web — consultá por WhatsApp o descargá el catálogo mayorista.</p>
  </div>
</section>

<div class="alt-pillbar">
  <div class="container"><div class="alt-pillgrid">{PILLS}</div></div>
</div>

<nav class="alt-dotnav" aria-label="Navegación por línea">{DOTNAV}</nav>

<div class="alt-wrap">
{''.join(sections)}
  <div class="container">
    <div class="prod-cta-band fi" style="margin:20px 0 60px">
      <h2>Consultá precios y condiciones mayoristas</h2>
      <p>Sin precios en la web. Descargá el catálogo o escribinos.</p>
      <div class="prod-cta-btns">
        <a href="assets/catalogo/catalogo-centurion-resumido.pdf" target="_blank" class="btn btn-naranja btn-lg">Descargar catálogo PDF</a>
        <a href="assets/catalogo/catalogo-centurion-completo.pdf" target="_blank" class="btn btn-outline-w btn-lg">Catálogo completo (todas las referencias)</a>
        <a href="https://api.whatsapp.com/send?phone=5491163787553&text=Hola!+Quiero+precios+mayoristas+de+Centurión." target="_blank" class="btn btn-wa btn-lg">Consultar por WhatsApp</a>
      </div>
    </div>
  </div>
</div>
"""

# título/descripcion propios para esta version alternativa
head_html = head_html.replace(
    "<title>" + soup.title.get_text() + "</title>",
    "<title>Productos | Centurión — por línea</title>"
) if soup.title else head_html

# insertamos el CSS extra justo antes de </style> del head copiado
if "</style>" in head_html:
    head_html = head_html.replace("</style>", CSS_EXTRA + "</style>", 1)

SCRIPT = """
<script>
window.addEventListener('scroll',()=>{document.getElementById('navbar').classList.toggle('scrolled',window.scrollY>40)},{passive:true})
document.getElementById('ham').addEventListener('click',()=>{document.getElementById('mob-nav').classList.toggle('open')})
function closeMob(){document.getElementById('mob-nav').classList.remove('open')}
const obs=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting)e.target.classList.add('vis')});},{threshold:0.05})
document.querySelectorAll('.fi').forEach(el=>obs.observe(el))
document.querySelectorAll('.alt-car-nav').forEach(btn=>{
  btn.addEventListener('click',()=>{
    const grid=document.getElementById(btn.dataset.target);
    const card=grid.querySelector('.alt-card');
    const step=card?(card.getBoundingClientRect().width+22)*2:560;
    grid.scrollBy({left:btn.classList.contains('alt-car-prev')?-step:step,behavior:'smooth'});
  });
});
const dotLinks=document.querySelectorAll('.alt-dotnav a');
if(dotLinks.length){
  const spy=new IntersectionObserver(entries=>{
    entries.forEach(entry=>{
      if(entry.isIntersecting){
        dotLinks.forEach(a=>a.classList.remove('active'));
        const link=document.querySelector('.alt-dotnav a[data-target="'+entry.target.id+'"]');
        if(link)link.classList.add('active');
      }
    });
  },{rootMargin:'-45% 0px -45% 0px',threshold:0});
  document.querySelectorAll('.alt-linea').forEach(s=>spy.observe(s));
}
</script>
"""

doc = f"""<!doctype html>
<html lang="es">
{head_html}
<body>
{navbar_html}
{mobnav_html}
{body_main}
{footer_html}
{wafloat_html}
{SCRIPT}
</body>
</html>"""

open(OUT, "w", encoding="utf-8").write(doc)
print("OK:", OUT)
