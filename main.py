import os, json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from supabase import create_client
from pydantic import BaseModel

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
app = FastAPI()

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Formato internacional con código de país para Colombia (+57)
MI_WHATSAPP = "573138816737"

class ItemVenta(BaseModel):
    id: int
    cant: int

class Resena(BaseModel):
    nombre: str
    comentario: str
    estrellas: int

@app.post("/finalizar-venta")
def finalizar_venta(items: list[ItemVenta]):
    ids = [i.id for i in items]
    # Consulta optimizada en 1 solo request
    res = supabase.table("productos").select("id, stock").in_("id", ids).execute()
    stock_map = {p["id"]: p["stock"] for p in (res.data or [])}

    for item in items:
        if item.id in stock_map:
            nuevo = max(0, stock_map[item.id] - item.cant)
            supabase.table("productos").update({"stock": nuevo}).eq("id", item.id).execute()
    return {"ok": True}

@app.post("/api/resenas")
def crear_resena(r: Resena):
    try:
        supabase.table("resenas").insert({"nombre": r.nombre, "comentario": r.comentario, "estrellas": r.estrellas}).execute()
        return {"ok": True}
    except Exception as e:
        print(f"Error al guardar reseña: {e}")
        return {"ok": False}

@app.get("/api/resenas")
def get_resenas():
    try:
        res = supabase.table("resenas").select("*").order("created_at", desc=True).limit(20).execute()
        return res.data or []
    except Exception as e:
        print(f"Error al obtener reseñas: {e}")
        return []

@app.get("/", response_class=HTMLResponse)
def home():
    data = supabase.table("productos").select("*").execute()
    productos = data.data or []
    for p in productos:
        if p.get('categoria'): p['categoria'] = p['categoria'].strip()
    productos_json = json.dumps(productos)
    cats = sorted(list(set([p.get('categoria','General') for p in productos if p.get('categoria')])))
    btns = "".join([f"<button class='pill' onclick=\"filtrarCat('{c}', this)\">{c}</button>" for c in cats])

    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
        <title>FENIX Distribuciones</title>
        <style>
            *{box-sizing:border-box} body{margin:0;font-family:Arial,sans-serif;background:#0f0f10;color:white}
            .topbar{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:#0f0f10;border-bottom:1px solid #222;position:sticky;top:0;z-index:20}
            .brand{display:flex;align-items:center;gap:10px} .icon{width:42px;height:42px;border-radius:50%} .brand b{color:#FFC107}
            .btn-cart{background:#FFC107;color:#000;padding:10px 14px;border-radius:10px;font-weight:800;border:none;cursor:pointer}
            .hero{margin:16px;background:#15151a;border-radius:20px;padding:22px;border:1px solid #222}
            .search-box{background:#1a1a1e;border:1px solid #2a2a2e;border-radius:12px;padding:12px 16px;display:flex;gap:10px;max-width:400px;margin:10px 16px} .search-box input{background:transparent;border:none;color:white;outline:none;width:100%;font-size:16px}
            .pills{display:flex;gap:8px;flex-wrap:wrap;padding:10px 16px} .pill{background:#1a1a1e;border:1px solid #2a2a2e;color:#aaa;padding:8px 14px;border-radius:20px;cursor:pointer} .pill.active{background:#FFC107;color:#000;font-weight:700}
            .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(165px,1fr));gap:12px;padding:12px;max-width:1300px;margin:auto} @media(min-width:700px){.grid{grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px;padding:20px}}
            .card{background:#1a1a1e;border:1px solid #25252b;border-radius:16px;overflow:hidden;display:flex;flex-direction:column;height:100%}
            .card-img{height:180px;background:#111;position:relative} @media(min-width:700px){.card-img{height:210px}} .card-img img{width:100%;height:100%;object-fit:cover} .cat-tag{position:absolute;top:8px;left:8px;background:#FFC107;color:#000;font-size:9px;font-weight:800;padding:4px 8px;border-radius:6px}
            .card-body{padding:10px;display:flex;flex-direction:column;flex:1} .qty-row{display:flex;align-items:center;gap:6px;margin-top:10px} .qty-btn{width:32px;height:32px;border-radius:8px;border:1px solid #333;background:#222;color:white;font-weight:800;cursor:pointer} .qty-num{width:28px;text-align:center} .btn-add{background:#FFC107;color:#000;border:none;flex:1;padding:9px;border-radius:9px;font-weight:800;cursor:pointer;font-size:13px}

            #modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.88);z-index:9999;padding:12px;align-items:center;justify-content:center;overflow:hidden}
            .modal-box{background:#23232a;border:1px solid #444;border-radius:20px;width:100%;max-width:480px;max-height:88vh;overflow-y:auto;overflow-x:hidden;-webkit-overflow-scrolling:touch;display:flex;flex-direction:column;transform:translateZ(0)}
            .modal-box::-webkit-scrollbar{width:6px} .modal-box::-webkit-scrollbar-thumb{background:#FFC107;border-radius:10px}
            .modal-head{padding:16px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;background:#23232a;flex-shrink:0}
            .modal-head h2{margin:0;font-size:17px} .close-x{background:#2a2a32;border:1px solid #333;color:#fff;width:34px;height:34px;border-radius:50%;cursor:pointer;flex-shrink:0}
            #lista{padding:12px;display:flex;flex-direction:column;gap:10px;flex-shrink:0}
            .cart-item{background:#2a2a32;border:1px solid #3a3a44;border-radius:12px;padding:10px;display:flex;align-items:center;gap:10px}
            .cart-item img{width:50px;height:50px;border-radius:8px;object-fit:cover;background:#111;flex-shrink:0}
            .cart-info{flex:1;min-width:0} .cart-info b{font-size:13px;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap} .cart-info small{color:#888;font-size:11px} .cart-price{color:#FFC107;font-weight:900;font-size:13px;margin-top:2px}
            .cart-qty{display:flex;align-items:center;gap:4px;background:#111;border-radius:8px;padding:3px;border:1px solid #333} .cart-qty button{width:28px;height:28px;border:none;background:#2a2a32;color:white;border-radius:6px;font-weight:800;cursor:pointer} .cart-qty span{min-width:18px;text-align:center;font-size:13px;font-weight:700}
            .modal-footer{padding:14px 16px 18px 16px;background:#1a1a20;border-top:1px solid #333;border-radius:0 0 20px 20px;flex-shrink:0}
            .total-row{display:flex;justify-content:space-between;align-items:center} .total-row h3{margin:0;color:#FFC107;font-size:18px}
            .inp{width:100%;padding:14px;border-radius:12px;border:1px solid #444;background:#0f0f10;color:white;margin-top:10px;font-size:16px} .inp:focus{border-color:#FFC107;outline:none} textarea.inp{min-height:85px;resize:none}
            .btn-wsp{width:100%;background:#25D366;color:white;padding:15px;border:none;border-radius:12px;font-weight:900;margin-top:12px;font-size:15px;cursor:pointer}
            .btn-continue{width:100%;margin-top:10px;background:#2a2a32;color:#bbb;padding:12px;border:1px solid #444;border-radius:12px;cursor:pointer}
            .reviews{padding:30px 16px;max-width:800px;margin:30px auto 0;border-top:1px solid #222}
            .review-form{background:#1a1a1e;border:1px solid #25252b;border-radius:16px;padding:16px;margin-bottom:20px}
            .stars-input{display:flex;gap:8px;font-size:32px;margin:10px 0} .stars-input span{color:#333;cursor:pointer} .stars-input span.active{color:#FFC107}
            .reviews-grid{display:grid;gap:10px} .review-card{background:#1a1a1e;border:1px solid #25252b;border-radius:12px;padding:14px}
            .stars{color:#FFC107} .review-name{color:#FFC107;font-weight:bold;margin-top:6px;font-size:13px}
            
            #loader{position:fixed;inset:0;background:black;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:9999;transition:opacity 0.5s}
            .fenix-volando{width:180px;animation:volar 2.2s ease-in-out infinite}
            @keyframes volar{
                0%{transform:translateX(-40px) translateY(0) rotate(-3deg);}
                25%{transform:translateX(-10px) translateY(-18px) rotate(2deg) scaleY(0.95);}
                50%{transform:translateX(20px) translateY(0) rotate(-2deg);}
                75%{transform:translateX(40px) translateY(-18px) rotate(3deg) scaleY(0.95);}
                100%{transform:translateX(-40px) translateY(0) rotate(-3deg);}
            }
            .barra{width:160px;height:4px;background:#222;border-radius:4px;overflow:hidden;margin-top:10px}
            .progreso{width:100%;height:100%;background:#FFC107;animation:carga 1.5s ease-in-out infinite}
            @keyframes carga{0%{transform:translateX(-100%)}100%{transform:translateX(100%)}}
        </style>
    </head>
    <body>
        <div id="loader">
            <img src="/static/fenix.png" class="fenix-volando" alt="Fenix">
            <p style="margin-top:15px;color:#aaa;font-size:14px">Cargando catálogo...</p>
            <div class="barra"><div class="progreso"></div></div>
        </div>

        <div class="topbar">
            <div class="brand">
                <img src="/static/logo.png" class="icon" alt="Logo">
                <div><b>FÉNIX</b><br><small style="color:#aaa">DISTRIBUCIONES</small></div>
            </div>
            <button class="btn-cart" onclick="abrir()">🛒 $<span id="cartTotalTop">0</span> (<span id="cartCountTop">0</span>)</button>
        </div>

        <div class="hero">
            <h1 style="margin:0 0 6px 0;font-size:22px">Insumos para Barbería</h1>
            <p style="margin:0;color:#aaa;font-size:14px">Elige la cantidad y haz tu pedido directo a WhatsApp.</p>
        </div>

        <div class="search-box">🔍<input id="busc" placeholder="Buscar productos..." onkeyup="filtrar()"></div>
        <div class="pills"><button class="pill active" onclick="filtrarCat('TODOS', this)">Todos</button>__BTNS__</div>
        <div id="grid" class="grid"></div>

        <div class="reviews">
            <h2 style="text-align:center">⭐ Califica nuestro servicio</h2>
            <div class="review-form">
                <div class="stars-input" id="starInput">
                    <span onclick="setStars(1)">★</span><span onclick="setStars(2)">★</span><span onclick="setStars(3)">★</span><span onclick="setStars(4)">★</span><span onclick="setStars(5)">★</span>
                </div>
                <input class="inp" id="resenaNombre" placeholder="Tu nombre">
                <textarea class="inp" id="resenaTexto" placeholder="Tu experiencia..." rows="3"></textarea>
                <button onclick="enviarResena()" style="width:100%;margin-top:12px;background:#FFC107;color:#000;padding:14px;border:none;border-radius:12px;font-weight:800;cursor:pointer">Publicar mi reseña</button>
            </div>
            <div class="reviews-grid" id="reviewsGrid"></div>
        </div>

        <div id="modal">
          <div class="modal-box">
            <div class="modal-head"><h2>Tu pedido - FÉNIX</h2><button class="close-x" onclick="cerrar()">✕</button></div>
            <div id="lista"></div>
            <div class="modal-footer">
              <div class="total-row"><span style="color:#aaa">Total a pagar</span><h3>$<span id="totM">0</span></h3></div>
              <input class="inp" id="nom" placeholder="Nombre completo *">
              <input class="inp" id="dir" placeholder="Dirección de entrega *">
              <input class="inp" id="tel" placeholder="Celular *">
              <textarea class="inp" id="nota" placeholder="Nota del pedido (ej: timbrar en apto 302)"></textarea>
              <button class="btn-wsp" onclick="enviar()">📲 Enviar pedido por WhatsApp</button>
              <button class="btn-continue" onclick="cerrar()">← Seguir comprando</button>
            </div>
          </div>
        </div>

        <script>
            const prods = __PRODUCTOS_JSON__;
            let catA = 'TODOS'; 
            let cart = []; 
            let tempQty = {}; 
            let estrellasSel = 5;

            function render(l){
              let h = ''; 
              l.forEach(function(p){
                let img = p.imagen_url || p.imagen || '';
                if(!img) img = 'https://via.placeholder.com/400/1a1a1e/FFC107?text=' + encodeURIComponent(p.nombre.substring(0,12));
                let cat = (p.categoria || 'GENERAL').toUpperCase(); 
                let q = tempQty[p.id] || 1;
                let precioFormateado = Number(p.precio).toLocaleString();
                h += '<div class="card"><div class="card-img"><span class="cat-tag">'+cat+'</span><img src="'+img+'" loading="lazy"></div><div class="card-body"><h3 style="margin:0;font-size:13px;min-height:32px">'+p.nombre+'</h3><div style="color:#9aa0a6;font-size:11px;min-height:28px;margin-top:4px">'+(p.descripcion||'')+'</div><div style="margin-top:auto;padding-top:8px"><div style="display:flex;justify-content:space-between"><div><small style="color:#9aa0a6;font-size:10px">Precio</small><div style="color:#FFC107;font-weight:800;font-size:13px">$'+precioFormateado+'</div></div><div style="color:#9aa0a6;font-size:10px">Stock: '+p.stock+'</div></div><div class="qty-row"><button class="qty-btn" onclick="cambiarTemp('+p.id+',-1)">-</button><span class="qty-num" id="q-'+p.id+'">'+q+'</span><button class="qty-btn" onclick="cambiarTemp('+p.id+',1)">+</button><button class="btn-add" onclick="add('+p.id+')">Agregar</button></div></div></div></div>';
              }); 
              if(h === '') h = '<p style="text-align:center;grid-column:1/-1;color:#666;padding:40px">No se encontraron productos</p>';
              document.getElementById('grid').innerHTML = h;
            }

            function cambiarTemp(id, d){
              let v = (tempQty[id] || 1) + d; 
              if(v < 1) v = 1; 
              tempQty[id] = v; 
              let el = document.getElementById('q-' + id); 
              if(el) el.innerText = v;
            }

            function filtrar(){
              let t = document.getElementById('busc').value.toLowerCase(); 
              let f = prods.filter(function(p){
                return p.nombre.toLowerCase().includes(t) && (catA === 'TODOS' || (p.categoria || '').toLowerCase() === catA.toLowerCase())
              }); 
              render(f);
            }

            function filtrarCat(c, btnElement){
              catA = c; 
              document.querySelectorAll('.pill').forEach(function(b){ b.classList.remove('active'); }); 
              if(btnElement) btnElement.classList.add('active'); 
              filtrar();
            }

            function add(id){
              let p = prods.find(function(x){ return x.id === id; }); 
              if(!p) return;
              let cant = tempQty[id] || 1; 
              let ex = cart.find(function(x){ return x.id === id; }); 
              if(ex) ex.cant += cant; 
              else cart.push(Object.assign({}, p, {cant: cant})); 
              tempQty[id] = 1; 
              up(); 
              render(prods);
            }

            function up(){
              let tot = 0, cnt = 0; 
              cart.forEach(function(c){ tot += c.precio * c.cant; cnt += c.cant; });
              document.getElementById('cartTotalTop').innerText = tot.toLocaleString(); 
              document.getElementById('totM').innerText = tot.toLocaleString(); 
              document.getElementById('cartCountTop').innerText = cnt;
              let lh = ''; 
              cart.forEach(function(c, i){
                let img = c.imagen_url || c.imagen || 'https://via.placeholder.com/100';
                lh += '<div class="cart-item"><img src="'+img+'"><div class="cart-info"><b>'+c.nombre+'</b><small>$'+Number(c.precio).toLocaleString()+' x '+c.cant+'</small><div class="cart-price">$'+(c.precio * c.cant).toLocaleString()+'</div></div><div class="cart-qty"><button onclick="cambiarCart('+i+',-1)">-</button><span>'+c.cant+'</span><button onclick="cambiarCart('+i+',1)">+</button></div></div>';
              });
              if(lh === '') lh = '<div style="text-align:center;color:#666;padding:30px">🛒 Carrito vacío</div>';
              document.getElementById('lista').innerHTML = lh;
            }

            function cambiarCart(i, d){
              cart[i].cant += d; 
              if(cart[i].cant < 1) cart.splice(i, 1); 
              up();
            }

            function abrir(){
              up(); 
              document.getElementById('modal').style.display = 'flex'; 
              document.body.style.overflow = 'hidden';
            }

            function cerrar(){
              document.getElementById('modal').style.display = 'none'; 
              document.body.style.overflow = '';
            }

            async function enviar(){
              let n = document.getElementById('nom').value.trim(); 
              let d = document.getElementById('dir').value.trim(); 
              let t = document.getElementById('tel').value.trim(); 
              let nota = document.getElementById('nota').value.trim();

              if(!n || !d){ alert('Por favor ingresa tu Nombre y Dirección de entrega.'); return; }
              if(cart.length === 0){ alert('El carrito está vacío.'); return; }

              // Descontar stock en base de datos
              try {
                await fetch('/finalizar-venta', {
                  method: 'POST', 
                  headers: {'Content-Type':'application/json'}, 
                  body: JSON.stringify(cart.map(function(c){ return {id: c.id, cant: c.cant}; }))
                });
              } catch(e) {
                console.error("Error al actualizar inventario:", e);
              }

              // Construcción segura del texto para WhatsApp
              let textoMsg = `Hola FÉNIX! Soy ${n}\n`;
              textoMsg += `📍 Dir: ${d}\n`;
              if(t) textoMsg += `📞 Tel: ${t}\n`;
              textoMsg += `\n🛒 PEDIDO:\n`;
              
              cart.forEach(function(c){
                textoMsg += `• ${c.nombre} x${c.cant} = $${(c.precio * c.cant).toLocaleString()}\n`;
              });
              
              textoMsg += `\n💰 TOTAL: $${document.getElementById('totM').innerText}`;
              if(nota) textoMsg += `\n\n📝 NOTA: ${nota}`;

              const urlWsp = `https://wa.me/__WHATSAPP__?text=${encodeURIComponent(textoMsg)}`;
              window.open(urlWsp, '_blank');

              cart = []; 
              up(); 
              cerrar(); 
              location.reload();
            }

            function setStars(n){
              estrellasSel = n; 
              document.querySelectorAll('#starInput span').forEach(function(s, i){ s.classList.toggle('active', i < n); });
            }
            setStars(5);

            async function cargarResenas(){
              try {
                let r = await fetch('/api/resenas'); 
                let data = await r.json(); 
                let html = ''; 
                if(!data || data.length === 0){
                  html = '<p style="color:#666;text-align:center">Aún no hay reseñas. ¡Sé el primero!</p>';
                } else {
                  data.forEach(function(res){
                    let stars = '★'.repeat(res.estrellas || 5); 
                    html += `<div class="review-card"><div class="stars">${stars}</div><p style="margin:6px 0;font-size:14px">${res.comentario}</p><div class="review-name">${res.nombre}</div></div>`;
                  });
                }
                document.getElementById('reviewsGrid').innerHTML = html;
              } catch(e){
                console.error(e);
              }
            }

            async function enviarResena(){
              let nom = document.getElementById('resenaNombre').value.trim(); 
              let txt = document.getElementById('resenaTexto').value.trim(); 
              if(!nom || !txt){ alert('Escribe tu nombre y comentario para publicar.'); return; }

              await fetch('/api/resenas', {
                method: 'POST', 
                headers: {'Content-Type':'application/json'}, 
                body: JSON.stringify({nombre: nom, comentario: txt, estrellas: estrellasSel})
              });

              document.getElementById('resenaNombre').value = ''; 
              document.getElementById('resenaTexto').value = ''; 
              setStars(5); 
              cargarResenas();
            }

            render(prods); 
            cargarResenas(); 
            up();

            document.getElementById('modal').addEventListener('click', function(e){ 
              if(e.target.id === 'modal') cerrar(); 
            });

            setTimeout(() => {
              const l = document.getElementById('loader');
              if(l){
                l.style.opacity = '0'; 
                setTimeout(() => l.style.display = 'none', 500);
              }
            }, 1000);
        </script>
    </body>
    </html>
    """
    html = html_template.replace("__PRODUCTOS_JSON__", productos_json).replace("__BTNS__", btns).replace("__WHATSAPP__", MI_WHATSAPP)
    return html
