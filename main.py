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

MI_WHATSAPP = "3138816737"

class ItemVenta(BaseModel):
    id: int
    cant: int

class Resena(BaseModel):
    nombre: str
    comentario: str
    estrellas: int

@app.post("/finalizar-venta")
def finalizar_venta(items: list[ItemVenta]):
    for item in items:
        prod = supabase.table("productos").select("stock").eq("id", item.id).single().execute()
        if prod.data:
            nuevo = max(0, prod.data["stock"] - item.cant)
            supabase.table("productos").update({"stock": nuevo}).eq("id", item.id).execute()
    return {"ok": True}

@app.post("/api/resenas")
def crear_resena(r: Resena):
    try:
        supabase.table("resenas").insert({"nombre": r.nombre, "comentario": r.comentario, "estrellas": r.estrellas}).execute()
        return {"ok": True}
    except:
        return {"ok": False}

@app.get("/api/resenas")
def get_resenas():
    try:
        res = supabase.table("resenas").select("*").order("created_at", desc=True).limit(20).execute()
        return res.data
    except:
        return []

@app.get("/", response_class=HTMLResponse)
def home():
    data = supabase.table("productos").select("*").execute()
    productos = data.data
    for p in productos:
        if p.get('categoria'): p['categoria'] = p['categoria'].strip()
    productos_json = json.dumps(productos)
    cats = list(set([p.get('categoria','General') for p in productos if p.get('categoria')]))
    btns = "".join([f"<button class='pill' onclick=\"filtrarCat('{c}')\">{c}</button>" for c in cats])

    html = f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FENIX Distribuciones</title>
    <style>
        *{{box-sizing:border-box}} body{{margin:0;font-family:Arial;background:#0f0f10;color:white}}
        .topbar{{display:flex;justify-content:space-between;align-items:center;padding:12px 20px;background:#0f0f10;border-bottom:1px solid #222;position:sticky;top:0;z-index:20}}
        .brand{{display:flex;align-items:center;gap:10px}} .icon{{width:42px;height:42px;border-radius:50%}} .brand b{{color:#FFC107}}
        .btn-cart{{background:#FFC107;color:#000;padding:10px 16px;border-radius:10px;font-weight:800;border:none;cursor:pointer}}
        .hero{{margin:20px;background:#15151a;border-radius:20px;padding:28px 30px;border:1px solid #222}}
        .search-box{{background:#1a1a1e;border:1px solid #2a2a2e;border-radius:12px;padding:12px 16px;display:flex;gap:10px;max-width:400px;margin:10px 20px}} .search-box input{{background:transparent;border:none;color:white;outline:none;width:100%}}
        .pills{{display:flex;gap:8px;flex-wrap:wrap;padding:10px 20px}} .pill{{background:#1a1a1e;border:1px solid #2a2a2e;color:#aaa;padding:8px 16px;border-radius:20px;cursor:pointer}} .pill.active{{background:#FFC107;color:#000;font-weight:700}}
        .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px;padding:20px;max-width:1300px;margin:auto;align-items:stretch}}
        .card{{background:#1a1a1e;border:1px solid #25252b;border-radius:18px;overflow:hidden;display:flex;flex-direction:column;height:100%}}
        .card-img{{height:220px;background:#111;position:relative}} .card-img img{{width:100%;height:100%;object-fit:cover}} .cat-tag{{position:absolute;top:12px;left:12px;background:#FFC107;color:#000;font-size:10px;font-weight:800;padding:5px 10px;border-radius:6px}}
        .card-body{{padding:14px;display:flex;flex-direction:column;flex:1}} .card-title{{margin:0;font-size:14px;min-height:36px}} .card-desc{{color:#9aa0a6;font-size:12px;min-height:32px;margin-top:4px}}
        .card-bottom{{margin-top:auto;padding-top:10px}} .qty-row{{display:flex;align-items:center;gap:8px;margin-top:12px}} .qty-btn{{width:36px;height:36px;border-radius:8px;border:1px solid #333;background:#222;color:white;font-weight:800;cursor:pointer}} .qty-num{{width:36px;text-align:center}} .btn-add{{background:#FFC107;color:#000;border:none;flex:1;padding:10px;border-radius:10px;font-weight:800;cursor:pointer}}
        /* CARRITO CON SCROLL COMPLETO - TODO VISIBLE */
        #modal{ display:none; position:fixed; inset:0; background:rgba(0,0,0,.8); backdrop-filter:blur(6px); z-index:99; justify-content:center; align-items:center; padding:16px; overflow-y:auto; }
        .modal-box{ background:#1e1e24; border:1px solid #333; border-radius:20px; width:100%; max-width:480px; max-height:none; display:flex; flex-direction:column; box-shadow:0 20px 60px rgba(0,0,0,.6); overflow-y:auto; }
        .modal-box::-webkit-scrollbar{ width:6px } .modal-box::-webkit-scrollbar-thumb{ background:#FFC107; border-radius:10px }
        .modal-head{ padding:20px 20px 12px 20px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #2a2a2e; position:sticky; top:0; background:#1e1e24; z-index:2; border-radius:20px 20px 0 0; }
        .modal-head h2{ margin:0; font-size:19px } .close-x{ background:#2a2a32; border:none; color:#aaa; width:32px; height:32px; border-radius:50%; cursor:pointer }
        .modal-list-wrap{ padding:14px 14px; }
        #lista{ background:#121214; border:1px solid #2a2a2e; border-radius:14px; padding:10px; display:flex; flex-direction:column; gap:10px; max-height:none; overflow:visible; }
        .cart-item{ background:#23232a; border:1px solid #333; border-radius:12px; padding:12px; display:flex; align-items:center; gap:12px; }
        .cart-item img{ width:54px; height:54px; border-radius:10px; object-fit:cover; background:#111; flex-shrink:0 }
        .cart-info{ flex:1; min-width:0 } .cart-info b{ font-size:13px; line-height:1.2; display:block } .cart-info small{ color:#888; font-size:11px } .cart-price{ color:#FFC107; font-weight:900; font-size:13px; margin-top:4px }
        .cart-qty{ display:flex; align-items:center; gap:5px; background:#111; border-radius:9px; padding:4px; border:1px solid #333 }
        .cart-qty button{ width:28px; height:28px; border:none; background:#2a2a32; color:white; border-radius:6px; cursor:pointer; font-weight:800 }
        .cart-qty span{ min-width:22px; text-align:center; font-weight:700; font-size:13px }
        .modal-footer{ padding:16px 20px 20px 20px; background:#1a1a20; border-top:1px solid #2a2a2e; border-radius:0 0 20px 20px; }
        .total-row{ display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; } .total-row h3{ margin:0; color:#FFC107 }
        .inp{ width:100%; padding:13px; border-radius:12px; border:1px solid #333; background:#111; color:white; margin-top:10px } .inp:focus{ border-color:#FFC107; outline:none }
        textarea.inp{ min-height:80px }
        .btn-wsp{ width:100%; background:#25D366; color:white; padding:14px; border:none; border-radius:12px; font-weight:900; margin-top:12px; cursor:pointer; font-size:15px }
        .btn-continue{ width:100%; margin-top:10px; background:#2a2a32; color:#aaa; padding:12px; border:none; border-radius:12px; cursor:pointer }

        .reviews{{padding:50px 20px;max-width:800px;margin:40px auto 0;border-top:1px solid #222}}
        .review-form{{background:#1a1a1e;border:1px solid #25252b;border-radius:16px;padding:20px;margin-bottom:24px}}
        .stars-input{{display:flex;gap:8px;font-size:32px;cursor:pointer;margin:10px 0}} .stars-input span{{color:#333}} .stars-input span.active{{color:#FFC107}}
        .reviews-grid{{display:grid;gap:12px}} .review-card{{background:#1a1a1e;border:1px solid #25252b;border-radius:12px;padding:16px}}
        .stars{{color:#FFC107}} .review-name{{color:#FFC107;font-weight:bold;margin-top:8px}}
    </style>
    </head><body>
        <div class="topbar"><div class="brand"><img src="/static/logo.png" class="icon"><div><b>FÉNIX</b><br><small style="color:#aaa">DISTRIBUCIONES</small></div></div><button class="btn-cart" onclick="abrir()">🛒 $<span id="cartTotalTop">0</span> (<span id="cartCountTop">0</span>)</button></div>
        <div class="hero"><h1>Insumos para Barbería</h1><p>Elige la cantidad y haz tu pedido directo a WhatsApp.</p></div>
        <div class="search-box">🔍<input id="busc" placeholder="Buscar productos..." onkeyup="filtrar()"></div>
        <div class="pills"><button class="pill active" onclick="filtrarCat('TODOS')">Todos</button>{btns}</div>
        <div id="grid" class="grid"></div>

        <div class="reviews"><h2>⭐ Califica nuestro servicio</h2><p style="text-align:center;color:#888">Tu opinión ayuda a otros barberos</p>
          <div class="review-form">
            <div class="stars-input" id="starInput"><span onclick="setStars(1)">★</span><span onclick="setStars(2)">★</span><span onclick="setStars(3)">★</span><span onclick="setStars(4)">★</span><span onclick="setStars(5)">★</span></div>
            <input class="inp" id="resenaNombre" placeholder="Tu nombre">
            <textarea class="inp" id="resenaTexto" placeholder="Tu experiencia con FÉNIX..." rows="3"></textarea>
            <button onclick="enviarResena()" style="width:100%;margin-top:12px;background:#FFC107;color:#000;padding:14px;border:none;border-radius:12px;font-weight:800;cursor:pointer">Publicar mi reseña</button>
          </div>
          <div class="reviews-grid" id="reviewsGrid"></div>
        </div>

        <div id="modal">
          <div class="modal-box">
            <div class="modal-head"><h2>Tu pedido - FÉNIX</h2><button class="close-x" onclick="cerrar()">✕</button></div>
            <div class="modal-list-wrap"><div id="lista"></div></div>
            <div class="modal-footer">
              <div class="total-row"><span style="color:#aaa">Total</span><h3>$<span id="totM">0</span></h3></div>
              <input class="inp" id="nom" placeholder="Nombre completo *">
              <input class="inp" id="dir" placeholder="Dirección de entrega *">
              <input class="inp" id="tel" placeholder="Celular *">
              <textarea class="inp" id="nota" placeholder="Nota del pedido (ej: timbrar en apto 302, llegar antes de las 10am)"></textarea>
              <button class="btn-wsp" onclick="enviar()">📲 Enviar pedido por WhatsApp</button>
              <button class="btn-continue" onclick="cerrar()">← Seguir comprando</button>
            </div>
          </div>
        </div>

        <script>
            const prods = {productos_json}; let catA='TODOS'; let cart=[]; let tempQty={{}}; let estrellasSel=5;
            function render(l){{let h=''; l.forEach(p=>{{let img=p.imagen_url||p.imagen||''; if(!img) img='https://via.placeholder.com/400/1a1a1e/FFC107?text='+encodeURIComponent(p.nombre.substring(0,12)); let cat=(p.categoria||'GENERAL').toUpperCase(); let q=tempQty[p.id]||1; h+=`<div class="card"><div class="card-img"><span class="cat-tag">${{cat}}</span><img src="${{img}}"><\/div><div class="card-body"><h3 style="margin:0;font-size:14px;min-height:36px">${{p.nombre}}<\/h3><div style="color:#9aa0a6;font-size:12px;min-height:32px;margin-top:4px">${{p.descripcion||''}}<\/div><div style="margin-top:auto;padding-top:10px"><div style="display:flex;justify-content:space-between"><div><small style="color:#9aa0a6;font-size:11px">Precio<\/small><div style="color:#FFC107;font-weight:800">$${{p.precio}}<\/div><\/div><div style="color:#9aa0a6;font-size:11px">Stock: ${{p.stock}}<\/div><\/div><div class="qty-row"><button class="qty-btn" onclick="cambiarTemp(${{p.id}},-1)">-<\/button><span class="qty-num" id="q-${{p.id}}">${{q}}<\/span><button class="qty-btn" onclick="cambiarTemp(${{p.id}},1)">+<\/button><button class="btn-add" onclick="add(${{p.id}})">Agregar<\/button><\/div><\/div><\/div><\/div>`}}); document.getElementById('grid').innerHTML=h;}}
            function cambiarTemp(id,d){{let v=(tempQty[id]||1)+d; if(v<1) v=1; tempQty[id]=v; let el=document.getElementById('q-'+id); if(el) el.innerText=v;}}
            function filtrar(){{let t=document.getElementById('busc').value.toLowerCase(); let f=prods.filter(p=> p.nombre.toLowerCase().includes(t) && (catA==='TODOS'|| (p.categoria||'').toLowerCase()===catA.toLowerCase())); render(f);}}
            function filtrarCat(c){{catA=c; document.querySelectorAll('.pill').forEach(b=>b.classList.remove('active')); event.target.classList.add('active'); filtrar();}}
            function add(id){{let p=prods.find(x=>x.id===id); let cant=tempQty[id]||1; let ex=cart.find(x=>x.id===id); if(ex) ex.cant+=cant; else cart.push({{...p,cant}}); tempQty[id]=1; up();}}
            function up(){{
              let tot=0,cnt=0; cart.forEach(c=>{{tot+=c.precio*c.cant; cnt+=c.cant}});
              document.getElementById('cartTotalTop').innerText=tot; document.getElementById('totM').innerText=tot.toLocaleString(); document.getElementById('cartCountTop').innerText=cnt;
              let lh=''; cart.forEach((c,i)=>{{
                let img=c.imagen_url||c.imagen||'https://via.placeholder.com/100';
                lh+=`<div class="cart-item">
                  <img src="${{img}}">
                  <div class="cart-info"><b>${{c.nombre}}</b><small>$${{c.precio}} x ${{c.cant}} unidades</small><div class="cart-price">$${{(c.precio*c.cant).toLocaleString()}}</div></div>
                  <div class="cart-qty"><button onclick="cambiarCart(${{i}},-1)">-</button><span>${{c.cant}}</span><button onclick="cambiarCart(${{i}},1)">+</button></div>
                </div>`}});
              document.getElementById('lista').innerHTML=lh||'<div style="text-align:center;color:#666;padding:30px">🛒 Carrito vacío</div>';
            }}
            function cambiarCart(i,d){{cart[i].cant+=d; if(cart[i].cant<1) cart.splice(i,1); up();}}
            function abrir(){{up(); document.getElementById('modal').style.display='flex'}} function cerrar(){{document.getElementById('modal').style.display='none'}}
            async function enviar(){{let n=document.getElementById('nom').value.trim(); let d=document.getElementById('dir').value.trim(); let t=document.getElementById('tel').value.trim(); let nota=document.getElementById('nota').value.trim(); if(!n||!d){{alert('Nombre y dirección obligatorios');return}} if(cart.length===0){{alert('Carrito vacío');return}} await fetch('/finalizar-venta', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body: JSON.stringify(cart.map(c=>({{id:c.id, cant:c.cant}})))}}); let msg=`Hola FENIX! Soy ${{n}}%0ADir: ${{d}}%0ATel: ${{t}}%0A%0APEDIDO:%0A`; cart.forEach(c=>{{msg+=`• ${{c.nombre}} x${{c.cant}} = $${{c.precio*c.cant}}%0A`}}); msg+=`%0ATOTAL: $${{document.getElementById('totM').innerText}}`; if(nota) msg+=`%0A%0ANOTA: ${{nota}}`; window.open(`https://wa.me/{MI_WHATSAPP}?text=${{msg}}`,'_blank'); cart=[]; up(); cerrar(); location.reload();}}
            function setStars(n){{estrellasSel=n; document.querySelectorAll('#starInput span').forEach((s,i)=>{{s.classList.toggle('active', i<n)}});}} setStars(5);
            async function cargarResenas(){{try{{let r=await fetch('/api/resenas'); let data=await r.json(); let html=''; if(!data||data.length==0) html='<p style="color:#666;text-align:center">Aún no hay reseñas</p>'; else data.forEach(res=>{{let stars='★'.repeat(res.estrellas||5); html+=`<div class="review-card"><div class="stars">${{stars}}</div><p>${{res.comentario}}</p><div class="review-name">${{res.nombre}}</div></div>`}}); document.getElementById('reviewsGrid').innerHTML=html;}}catch(e){{}}}}
            async function enviarResena(){{let nom=document.getElementById('resenaNombre').value.trim(); let txt=document.getElementById('resenaTexto').value.trim(); if(!nom||!txt){{alert('Escribe nombre y comentario');return}} await fetch('/api/resenas',{{method:'POST', headers:{{'Content-Type':'application/json'}}, body: JSON.stringify({{nombre:nom, comentario:txt, estrellas:estrellasSel}})}}); document.getElementById('resenaNombre').value=''; document.getElementById('resenaTexto').value=''; setStars(5); cargarResenas();}}
            render(prods); cargarResenas();
        </script>
    </body></html>
    """
    return html
