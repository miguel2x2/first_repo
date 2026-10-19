from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from urllib.parse import quote
import os
import json

app = Flask(__name__)
# Cambia esta clave por una frase larga y privada antes de publicar la tienda.
app.secret_key = os.environ.get("SECRET_KEY", "cambia-esta-clave-secreta-antes-de-publicar")

# IMPORTANTE: escribe tu número de WhatsApp en formato internacional, solo números.
# Ejemplo de Perú: 51987654321 (51 = Perú; luego el número de celular).
NUMERO_WHATSAPP = os.environ.get("WHATSAPP_NUMBER", "51987654321")

PRODUCTOS = [
    {"id": 1, "nombre": "Audífonos Bluetooth", "categoria": "Tecnología", "precio": 149.00,
     "descripcion": "Sonido envolvente para música, llamadas y uso diario.",
     "imagen": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e"},
    {"id": 2, "nombre": "Reloj inteligente", "categoria": "Tecnología", "precio": 199.00,
     "descripcion": "Un compañero práctico para tus actividades diarias.",
     "imagen": "https://images.unsplash.com/photo-1523275335684-37898b6baf30"},
    {"id": 3, "nombre": "Mochila urbana", "categoria": "Accesorios", "precio": 89.00,
     "descripcion": "Diseño cómodo y versátil para estudiar o trabajar.",
     "imagen": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62"},
    {"id": 4, "nombre": "Zapatillas deportivas", "categoria": "Moda", "precio": 129.00,
     "descripcion": "Estilo casual para acompañarte todos los días.",
     "imagen": "https://images.unsplash.com/photo-1542291026-7eec264c27ff"},
    {"id": 5, "nombre": "Botella térmica", "categoria": "Hogar", "precio": 39.90,
     "descripcion": "Ideal para llevar tu bebida a la oficina, clases o paseos.",
     "imagen": "https://images.unsplash.com/photo-1602143407151-7111542de6e8"},
    {"id": 6, "nombre": "Lámpara de escritorio", "categoria": "Hogar", "precio": 59.90,
     "descripcion": "Ilumina tu espacio de estudio o trabajo con estilo.",
     "imagen": "https://images.unsplash.com/photo-1507470423591-5b3c0c9a5f5b"},
    {"id": 7, "nombre": "Gafas de sol", "categoria": "Accesorios", "precio": 49.90,
     "descripcion": "Un accesorio sencillo para completar tu look.",
     "imagen": "https://images.unsplash.com/photo-1511499767150-a48a237f0083"},
    {"id": 8, "nombre": "Camiseta básica", "categoria": "Moda", "precio": 35.00,
     "descripcion": "Una prenda versátil para combinar fácilmente.",
     "imagen": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab"},
]

# Imágenes de respaldo por si alguna URL no carga.
IMAGEN_RESPALDO = "https://images.unsplash.com/photo-1490481651871-ab68de25d43d"


def producto_por_id(producto_id):
    return next((p for p in PRODUCTOS if p["id"] == producto_id), None)


def obtener_carrito():
    carrito = session.get("carrito", {})
    resultado = []
    for id_texto, cantidad in carrito.items():
        try:
            producto = producto_por_id(int(id_texto))
            cantidad = int(cantidad)
        except (ValueError, TypeError):
            continue
        if producto and cantidad > 0:
            item = dict(producto)
            item["cantidad"] = min(cantidad, 99)
            item["subtotal"] = round(item["precio"] * item["cantidad"], 2)
            resultado.append(item)
    return resultado


def total_carrito():
    return round(sum(item["subtotal"] for item in obtener_carrito()), 2)


BASE_HTML = r"""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ titulo }} | MiTienda</title>
  <meta name="description" content="Encuentra productos útiles a precios increíbles en MiTienda.">
  <style>
    :root { --azul:#1458d4; --azul-oscuro:#102a56; --fondo:#f5f7fb; --texto:#18243a; --muted:#65738b; --borde:#e3e9f2; --verde:#16a34a; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Inter,Segoe UI,Arial,sans-serif; background:var(--fondo); color:var(--texto); }
    a { color:inherit; text-decoration:none; }
    .topbar { background:#fff; border-bottom:1px solid var(--borde); position:sticky; top:0; z-index:5; }
    .nav { max-width:1160px; margin:auto; padding:16px 22px; display:flex; align-items:center; justify-content:space-between; gap:18px; }
    .brand { display:flex; align-items:center; gap:10px; font-size:22px; font-weight:800; color:var(--azul-oscuro); }
    .brand-icon { background:var(--azul); color:#fff; border-radius:12px; width:40px; height:40px; display:grid; place-items:center; font-size:22px; }
    .navlinks { display:flex; align-items:center; gap:22px; color:#34445e; font-weight:600; font-size:14px; }
    .cart-pill { background:#eaf1ff; color:var(--azul); border-radius:20px; padding:9px 13px; }
    .container { max-width:1160px; margin:28px auto; padding:0 22px; }
    .hero { border-radius:24px; overflow:hidden; padding:48px; min-height:250px; display:flex; align-items:center; background:linear-gradient(110deg,#102a56 0%,#1458d4 65%,#2f8cf0 100%); color:#fff; box-shadow:0 14px 34px #15366a20; }
    .hero h1 { font-size:clamp(32px,5vw,48px); line-height:1.08; margin:0 0 14px; max-width:570px; }
    .hero p { max-width:550px; line-height:1.7; color:#e3edff; margin:0 0 22px; }
    .hero-badge { display:inline-block; border:1px solid #ffffff60; background:#ffffff16; padding:7px 12px; border-radius:99px; font-size:12px; margin-bottom:15px; }
    .section-head { display:flex; justify-content:space-between; align-items:end; gap:14px; margin:30px 0 18px; }
    h2 { margin:0; font-size:25px; }
    .muted { color:var(--muted); }
    .products { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:18px; }
    .card { background:#fff; border:1px solid var(--borde); border-radius:18px; overflow:hidden; transition:transform .18s,box-shadow .18s; }
    .card:hover { transform:translateY(-3px); box-shadow:0 12px 25px #18243a10; }
    .product-img { width:100%; height:190px; object-fit:cover; display:block; background:#eaf0f8; }
    .card-body { padding:16px; }
    .category { font-size:11px; text-transform:uppercase; letter-spacing:.08em; color:var(--azul); font-weight:800; }
    .card h3 { font-size:16px; margin:8px 0; }
    .description { color:var(--muted); font-size:13px; line-height:1.5; min-height:39px; }
    .price { font-weight:850; color:var(--azul); font-size:20px; margin:12px 0; }
    .btn { border:0; display:inline-flex; align-items:center; justify-content:center; gap:8px; cursor:pointer; border-radius:10px; padding:12px 16px; font-weight:750; font-size:14px; transition:filter .15s; }
    .btn:hover { filter:brightness(.96); }
    .btn-primary { background:var(--azul); color:#fff; }
    .btn-light { background:#edf3ff; color:var(--azul); }
    .btn-whatsapp { background:var(--verde); color:#fff; }
    .btn-block { width:100%; }
    .panel { background:#fff; border:1px solid var(--borde); border-radius:18px; padding:24px; }
    .flash { padding:12px 15px; border-radius:10px; background:#fff7db; color:#7b5200; margin-bottom:16px; }
    .cart-row { display:grid; grid-template-columns:1fr 110px 100px 110px 90px; align-items:center; gap:12px; padding:16px 0; border-bottom:1px solid var(--borde); }
    .cart-row:last-child { border-bottom:0; }
    .qty-form { display:flex; align-items:center; gap:6px; }
    .qty-form input { width:58px; padding:8px; border:1px solid var(--borde); border-radius:8px; }
    .cart-total { text-align:right; font-size:25px; font-weight:850; margin:22px 0; }
    .checkout-grid { display:grid; grid-template-columns:1.2fr .8fr; gap:20px; }
    label { display:block; font-size:13px; font-weight:700; margin:14px 0 6px; }
    input, textarea { width:100%; border:1px solid #d7dfeb; border-radius:10px; padding:12px; font:inherit; }
    textarea { min-height:85px; resize:vertical; }
    .footer { text-align:center; color:var(--muted); font-size:13px; padding:30px 15px; }
    .empty { text-align:center; padding:45px 15px; }
    .empty .emoji { font-size:44px; }
    @media(max-width:900px) { .products { grid-template-columns:repeat(2,minmax(0,1fr)); } .checkout-grid { grid-template-columns:1fr; } .cart-row { grid-template-columns:1fr 80px 80px; } .cart-row .hide-mobile { display:none; } }
    @media(max-width:560px) { .nav { padding:12px 15px; } .brand { font-size:18px; } .navlinks { gap:10px; font-size:12px; } .navlinks .optional { display:none; } .container { padding:0 14px; margin:18px auto; } .hero { padding:30px 24px; min-height:230px; } .products { gap:10px; } .product-img { height:145px; } .card-body { padding:12px; } .card h3 { font-size:14px; } .price { font-size:18px; } .btn { padding:10px 11px; font-size:12px; } .panel { padding:16px; } }
  </style>
</head>
<body>
<header class="topbar">
  <nav class="nav">
    <a class="brand" href="{{ url_for('inicio') }}"><span class="brand-icon">🛍</span><span>MiTienda<small style="display:block;font-size:10px;font-weight:500;color:#65738b">Todo lo que necesitas, en un solo lugar</small></span></a>
    <div class="navlinks">
      <a href="{{ url_for('inicio') }}">Inicio</a>
      <a class="optional" href="{{ url_for('inicio') }}#productos">Productos</a>
      <a class="cart-pill" href="{{ url_for('ver_carrito') }}">🛒 Carrito ({{ cantidad_carrito }})</a>
    </div>
  </nav>
</header>
<main class="container">
  {% with mensajes = get_flashed_messages() %}
    {% if mensajes %}{% for mensaje in mensajes %}<div class="flash">{{ mensaje }}</div>{% endfor %}{% endif %}
  {% endwith %}
  {{ contenido|safe }}
</main>
<footer class="footer">© {{ anio }} MiTienda · Atención personalizada por WhatsApp</footer>
</body>
</html>
"""


def render_pagina(titulo, contenido, **kwargs):
    return render_template_string(
        BASE_HTML, titulo=titulo, contenido=render_template_string(contenido, **kwargs),
        cantidad_carrito=sum(i["cantidad"] for i in obtener_carrito()),
        anio=__import__("datetime").datetime.now().year
    )


INICIO_HTML = r"""
<section class="hero">
  <div>
    <span class="hero-badge">✨ TU TIENDA ONLINE</span>
    <h1>Compra fácil.<br>Vive mejor.</h1>
    <p>Encuentra productos útiles, accesorios y tecnología a precios increíbles. Haz tu pedido en pocos pasos y coordina por WhatsApp.</p>
    <a class="btn btn-primary" href="#productos">Ver productos&nbsp; →</a>
  </div>
</section>
<div class="section-head" id="productos">
  <div><h2>Productos destacados</h2><div class="muted" style="margin-top:6px">Una selección para tu día a día</div></div>
  <span class="muted">{{ productos|length }} productos</span>
</div>
<section class="products">
{% for p in productos %}
  <article class="card">
    <img class="product-img" src="{{ p.imagen }}" alt="{{ p.nombre }}" loading="lazy" onerror="this.onerror=null;this.src='{{ respaldo }}'">
    <div class="card-body">
      <div class="category">{{ p.categoria }}</div>
      <h3>{{ p.nombre }}</h3>
      <div class="description">{{ p.descripcion }}</div>
      <div class="price">S/ {{ "%.2f"|format(p.precio) }}</div>
      <form method="post" action="{{ url_for('agregar', producto_id=p.id) }}">
        <button class="btn btn-primary btn-block" type="submit">＋ Agregar al carrito</button>
      </form>
    </div>
  </article>
{% endfor %}
</section>
"""


CARRITO_HTML = r"""
<div class="section-head"><div><h2>Tu carrito</h2><div class="muted" style="margin-top:6px">Revisa tus productos antes de enviar el pedido.</div></div></div>
{% if carrito %}
<div class="panel">
  <div class="cart-row" style="font-size:12px;font-weight:800;color:#65738b">
    <div>PRODUCTO</div><div>PRECIO</div><div>CANTIDAD</div><div class="hide-mobile">SUBTOTAL</div><div></div>
  </div>
  {% for item in carrito %}
  <div class="cart-row">
    <div><strong>{{ item.nombre }}</strong><div class="muted" style="font-size:12px">{{ item.categoria }}</div></div>
    <div>S/ {{ "%.2f"|format(item.precio) }}</div>
    <form class="qty-form" method="post" action="{{ url_for('actualizar', producto_id=item.id) }}">
      <input type="number" name="cantidad" min="1" max="99" value="{{ item.cantidad }}" aria-label="Cantidad">
      <button class="btn btn-light" type="submit">OK</button>
    </form>
    <div class="hide-mobile">S/ {{ "%.2f"|format(item.subtotal) }}</div>
    <form method="post" action="{{ url_for('eliminar', producto_id=item.id) }}"><button class="btn btn-light" type="submit">Quitar</button></form>
  </div>
  {% endfor %}
  <div class="cart-total">Total: S/ {{ "%.2f"|format(total) }}</div>
  <div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap">
    <a class="btn btn-light" href="{{ url_for('inicio') }}">← Seguir comprando</a>
    <a class="btn btn-primary" href="{{ url_for('finalizar') }}">Continuar pedido →</a>
  </div>
</div>
{% else %}
<div class="panel empty"><div class="emoji">🛒</div><h2>Tu carrito está vacío</h2><p class="muted">Agrega productos para comenzar tu pedido.</p><a class="btn btn-primary" href="{{ url_for('inicio') }}">Explorar productos</a></div>
{% endif %}
"""


FINALIZAR_HTML = r"""
<div class="section-head"><div><h2>Datos para tu pedido</h2><div class="muted" style="margin-top:6px">Completa tus datos y luego envía el resumen por WhatsApp.</div></div></div>
<div class="checkout-grid">
  <section class="panel">
    <form method="post" action="{{ url_for('enviar_whatsapp') }}">
      <label for="nombre">Nombre y apellido *</label><input id="nombre" name="nombre" required maxlength="80" placeholder="Ej. Ana Pérez">
      <label for="telefono">Tu teléfono (opcional)</label><input id="telefono" name="telefono" maxlength="25" placeholder="Ej. 987 654 321">
      <label for="entrega">Distrito o lugar de entrega *</label><input id="entrega" name="entrega" required maxlength="120" placeholder="Ej. Arequipa, Cercado">
      <label for="nota">Indicaciones adicionales (opcional)</label><textarea id="nota" name="nota" maxlength="400" placeholder="Color, talla, referencia de entrega, etc."></textarea>
      <p class="muted" style="font-size:12px">El pedido se enviará a WhatsApp para confirmar disponibilidad, envío y forma de pago.</p>
      <button class="btn btn-whatsapp btn-block" type="submit">🟢 Preparar pedido en WhatsApp</button>
    </form>
  </section>
  <aside class="panel">
    <h3 style="margin-top:0">Resumen de compra</h3>
    {% for item in carrito %}
      <div style="display:flex;justify-content:space-between;gap:10px;padding:12px 0;border-bottom:1px solid #e3e9f2">
        <span>{{ item.nombre }} × {{ item.cantidad }}</span><strong>S/ {{ "%.2f"|format(item.subtotal) }}</strong>
      </div>
    {% endfor %}
    <div style="display:flex;justify-content:space-between;font-size:21px;font-weight:850;margin-top:18px"><span>Total</span><span>S/ {{ "%.2f"|format(total) }}</span></div>
    <p class="muted" style="font-size:12px">Los precios son de ejemplo. Confirma el stock y el costo de envío por WhatsApp.</p>
  </aside>
</div>
"""


@app.route("/")
def inicio():
    return render_pagina("Inicio", INICIO_HTML, productos=PRODUCTOS, respaldo=IMAGEN_RESPALDO)


@app.route("/agregar/<int:producto_id>", methods=["POST"])
def agregar(producto_id):
    producto = producto_por_id(producto_id)
    if not producto:
        flash("No encontramos ese producto.")
        return redirect(url_for("inicio"))
    carrito = session.get("carrito", {})
    clave = str(producto_id)
    carrito[clave] = min(int(carrito.get(clave, 0)) + 1, 99)
    session["carrito"] = carrito
    flash("Producto agregado al carrito.")
    return redirect(request.referrer or url_for("inicio"))


@app.route("/carrito")
def ver_carrito():
    return render_pagina("Carrito", CARRITO_HTML, carrito=obtener_carrito(), total=total_carrito())


@app.route("/actualizar/<int:producto_id>", methods=["POST"])
def actualizar(producto_id):
    try:
        cantidad = int(request.form.get("cantidad", "1"))
    except ValueError:
        cantidad = 1
    carrito = session.get("carrito", {})
    if producto_por_id(producto_id) and cantidad > 0:
        carrito[str(producto_id)] = min(cantidad, 99)
        session["carrito"] = carrito
    else:
        flash("La cantidad no es válida.")
    return redirect(url_for("ver_carrito"))


@app.route("/eliminar/<int:producto_id>", methods=["POST"])
def eliminar(producto_id):
    carrito = session.get("carrito", {})
    carrito.pop(str(producto_id), None)
    session["carrito"] = carrito
    flash("Producto quitado del carrito.")
    return redirect(url_for("ver_carrito"))


@app.route("/finalizar")
def finalizar():
    carrito = obtener_carrito()
    if not carrito:
        flash("Primero agrega algún producto al carrito.")
        return redirect(url_for("inicio"))
    return render_pagina("Finalizar pedido", FINALIZAR_HTML, carrito=carrito, total=total_carrito())


@app.route("/enviar-whatsapp", methods=["POST"])
def enviar_whatsapp():
    carrito = obtener_carrito()
    if not carrito:
        flash("Tu carrito está vacío.")
        return redirect(url_for("inicio"))

    nombre = request.form.get("nombre", "").strip()[:80]
    telefono = request.form.get("telefono", "").strip()[:25]
    entrega = request.form.get("entrega", "").strip()[:120]
    nota = request.form.get("nota", "").strip()[:400]
    if not nombre or not entrega:
        flash("Completa tu nombre y el lugar de entrega.")
        return redirect(url_for("finalizar"))

    lineas = [
        "¡Hola! Quiero realizar este pedido en MiTienda.",
        "",
        f"Nombre: {nombre}",
    ]
    if telefono:
        lineas.append(f"Teléfono del cliente: {telefono}")
    lineas += [f"Lugar de entrega: {entrega}", "", "Productos:"]
    for item in carrito:
        lineas.append(f"- {item['nombre']} x {item['cantidad']} = S/ {item['subtotal']:.2f}")
    lineas += ["", f"TOTAL: S/ {total_carrito():.2f}"]
    if nota:
        lineas += ["", f"Indicaciones: {nota}"]
    lineas += ["", "Por favor, confírmame stock, costo de envío y medios de pago."]
    mensaje = quote("\n".join(lineas))

    numero = "".join(c for c in NUMERO_WHATSAPP if c.isdigit())
    if len(numero) < 10 or numero == "51987654321":
        flash("Configura tu número real de WhatsApp en la variable NUMERO_WHATSAPP dentro de app.py.")
        return redirect(url_for("finalizar"))

    session["carrito"] = {}
    return redirect(f"https://wa.me/{numero}?text={mensaje}")


if __name__ == "__main__":
    # Abre la web localmente. Para publicar en internet, sigue el README.
    app.run(debug=True, host="127.0.0.1", port=5000)
