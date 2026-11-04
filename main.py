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

@app.post("/finalizar-venta")
def finalizar_venta(items: list[ItemVenta]):
    for item in items:
        prod = supabase.table("productos").select("stock").eq("id", item.id).single().execute()
        if prod.data:
            nuevo = max(0, prod.data["stock"] - item.cant)
            supabase.table("productos").update({"stock": nuevo}).eq("id", item.id).execute()
    return {"ok": True}

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
        .brand{{display:flex;align-items:center;gap:10px}} .icon{{width:42px;height:42px;border-radius:50%;background:#111;object-fit:cover}} .brand b{{color:#FFC107}} .brand small{{color:#aaa;font-size:11px}}
        .btn-cart{{background:#FFC107;color:#000;padding:10px 16px;border-radius:10px;font-weight:800;border:none;cursor:pointer}}
        .hero{{margin:20px;background:#15151a;border-radius:20px;padding:28px 30px;border:1px solid #222}} .badge{{background:#2a2210;color:#FFC107;padding:6px 12px;border-radius:20px;font-size:11px;font-weight:700}} .hero h1{{font-size:32px;margin:12px 0 8px}} .hero p{{color:#9aa0a6}}
        .search-box{{background:#1a1a1e;border:1px solid #2a2a2e;border-radius:12px;padding:12px 16px;display:flex;gap:10px;flex:1;max-width:400px;margin:0 20px}} .search-box input{{background:transparent;border:none;color:white;outline:none;width:100%}}
        .pills{{display:flex;gap:8px;flex-wrap:wrap;padding:10px 20px}} .pill{{background:#1a1a1e;border:1px solid #2a2a2e;color:#aaa;padding:8px 16px;border-radius:20px;cursor:pointer}} .pill.active{{background:#FFC107;color:#000;font-weight:700}}
        .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px;padding:20px;max-width:1300px;margin:auto;align-items:stretch}}
        /* --- TARJETAS NIVELADAS --- */
        .card{{background:#1a1a1e;border:1px solid #25252b;border-radius:18px;overflow:hidden;display:flex;flex-direction:column;height:100%}}
        .card-img{{height:200px;background:#111;position:relative;flex-shrink:0}} .card-img img{{width:100%;height:100%;object-fit:cover}} .cat-tag{{position:absolute;top:12px;left:12px;background:#FFC107;color:#000;font-size:10px;font-weight:800;padding:5px 10px;border-radius:6px}}
        .card-body{{padding:14px;display:flex;flex-direction:column;flex:1}}
        .card-title{{margin:0;font-size:14px;line-height:1.3;min-height:36px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
        .card-desc{{color:#9aa0a6;font-size:12px;min-height:32px;margin-top:4px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
        .card-bottom{{margin-top:auto;padding-top:10px}}
        .price-row{{display:flex;justify-content:space-between;align-items:end}}
        .qty-row{{display:flex;align-items:center;gap:8px;margin-top:12px}} .qty-btn{{width:36px;height:36px;border-radius:8px;border:1px solid #333;background:#222;color:white;font-weight:800;cursor:pointer}} .qty-num{{width:36px;text-align:center;font-weight:700}} .btn-add{{background:#FFC107;color:#000;border:none;flex:1;padding:10px;border-radius:10px;font-weight:800;cursor:pointer;height:36px}}
        #modal{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:40;justify-content:center;align-items:center;padding:12px}}
        .modal-box{{background:#1a1a1e;border:1px solid #2a2a2e;border-radius:16px;max-width:420px;width:95%;max-height:90vh;display:flex;flex-direction:column;padding:22px;gap:10px}}
        #lista{{flex:1;overflow-y:auto;max-height:38vh;padding-right:8px}} #lista::-webkit-scrollbar{{width:6px}} #lista::-webkit-scrollbar-thumb{{background:#333;border-radius:10px}}
        .cart-item{{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #2a2a2e}}
        .inp{{width:100%;padding:10px;border-radius:8px;border:1px solid #2a2a2e;background:#111;color:white;margin-top:6px}}
        .reviews{{padding:50px 20px;max-width:1300px;margin:40px auto 0;border-top:1px solid #222}}
        .reviews h2{{text-align:center;font-size:26px;margin:0}} .reviews .sub{{text-align:center;color:#888;margin:8px 0 28px}}
        .reviews-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}}
        .review-card{{background:#1a1a1e;border:1px solid #25252b;border-radius:16px;padding:18px;position:relative}}
        .stars{{color:#FFC107;margin-bottom:8px}} .review-name{{color:#FFC107;font-weight:bold;margin-top:10px}} .review-role{{font-size:11px;color:#666}}
        .verified{{position:absolute;top:14px;right:14px;background:#112a11;color:#25D366;font-size:10px;padding:4px 8px;border-radius:20px;border:1px solid #1f4a1f}}
    </style>
    </head><body>
        <div class="topbar"><div class="brand"><img src="/static/logo.png" onerror="this.src='https://via.placeholder.com/42/FFC107/000?text=F'" class="icon"><div><b>FÉNIX</b><br><small>DISTRIBUCIONES</small></div></div><div class="actions"><button class="btn-cart" onclick="abrir()">🛒 $<span id="cartTotalTop">0</span> (<span id="cartCountTop">0</span>)</button></div></div>
        <div class="hero"><span class="badge">CATÁLOGO </span><h1>Insumos para Barbería de Alta Calidad</h1><p>Elige la cantidad y haz tu pedido directo a WhatsApp.</p></div>
        <div class="search-box">🔍<input id="busc" placeholder="Buscar productos..." onkeyup="filtrar()"></div>
        <div class="pills"><button class="pill active" onclick="filtrarCat('TODOS')">Todos</button>{btns}</div>
        <div id="grid" class="grid"></div>
        <div class="reviews"><h2>⭐ Lo que dicen nuestros clientes</h2><p class="sub">Más de 200 barberos confían en FÉNIX</p><div class="reviews-grid"><div class="review-card"><span class="verified">✓ Verificado</span><div class="stars">★★★★★</div><p>"Excelente calidad en las cuchillas Dorco y entrega super rápida en Bogotá."</p><div class="review-name">Andrés M.</div><div class="review-role">Barbería La 93</div></div><div class="review-card"><span class="verified">✓ Verificado</span><div class="stars">★★★★★</div><p>"Precios competitivos y la capa profesional salió buenísima."</p><div class="review-name">Cristian D.</div><div class="review-role">Fades & Co</div></div><div class="review-card"><span class="verified">✓ Verificado</span><div class="stars">★★★★★</div><p>"Pido cada 15 días por WhatsApp y siempre llega completo."</p><div class="review-name">Yenifer L.</div><div class="review-role">Studio Barber</div></div></div></div>
        <div id="modal"><div class="modal-box"><h2>Tu pedido - FÉNIX</h2><div id="lista"></div><h3>Total: $<span id="totM">0</span></h3><input class="inp" id="nom" placeholder="Nombre *"><input class="inp" id="dir" placeholder="Dirección *"><input class="inp" id="tel" placeholder="Celular"><textarea class="inp" id="nota" placeholder="Nota (opcional)" rows="2"></textarea><button onclick="enviar()" style="width:100%;background:#25D366;color:white;padding:14px;border:none;border-radius:10px;font-weight:800;margin-top:8px">📲 Enviar pedido por WhatsApp</button><button onclick="cerrar()" style="width:100%;margin-top:8px;background:#2a2a2e;color:white;padding:12px;border:none;border-radius:10px">Seguir comprando</button></div></div>
        <script>
            const prods = {productos_json}; let catA='TODOS'; let cart=[]; let tempQty={{}};
            function render(l){{
              let h=''; 
              l.forEach(p=>{{
                let img=p.imagen_url||'https://via.placeholder.com/400'; 
                let cat=(p.categoria||'GENERAL').toUpperCase(); 
                let q=tempQty[p.id]||1; 
                h+=`<div class="card">
                  <div class="card-img"><span class="cat-tag">${{cat}}</span><img src="${{img}}"></div>
                  <div class="card-body">
                    <h3 class="card-title">${{p.nombre}}</h3>
                    <div class="card-desc">${{p.descripcion||''}}</div>
                    <div class="card-bottom">
                      <div class="price-row">
                        <div><small style="color:#9aa0a6;font-size:11px">Precio</small><div style="color:#FFC107;font-weight:800">$${{p.precio}}</div></div>
                        <div style="color:#9aa0a6;font-size:11px">Stock: ${{p.stock}}</div>
                      </div>
                      <div class="qty-row"><button class="qty-btn" onclick="cambiarTemp(${{p.id}},-1)">-</button><span class="qty-num" id="q-${{p.id}}">${{q}}</span><button class="qty-btn" onclick="cambiarTemp(${{p.id}},1)">+</button><button class="btn-add" onclick="add(${{p.id}})">Agregar</button></div>
                    </div>
                  </div>
                </div>` 
              }}); 
              document.getElementById('grid').innerHTML=h; 
            }}
            function cambiarTemp(id,d){{ let v=(tempQty[id]||1)+d; if(v<1) v=1; tempQty[id]=v; let el=document.getElementById('q-'+id); if(el) el.innerText=v; }}
            function filtrar(){{ let t=document.getElementById('busc').value.toLowerCase(); let f=prods.filter(p=> p.nombre.toLowerCase().includes(t) && (catA==='TODOS'|| (p.categoria||'').toLowerCase()===catA.toLowerCase())); render(f); }}
            function filtrarCat(c){{ catA=c; document.querySelectorAll('.pill').forEach(b=>b.classList.remove('active')); event.target.classList.add('active'); filtrar(); }}
            function add(id){{ let p=prods.find(x=>x.id===id); let cant=tempQty[id]||1; let ex=cart.find(x=>x.id===id); if(ex) ex.cant+=cant; else cart.push({{...p,cant}}); tempQty[id]=1; up(); render(prods); }}
            function up(){{ let tot=0,cnt=0; cart.forEach(c=>{{tot+=c.precio*c.cant; cnt+=c.cant}}); document.getElementById('cartTotalTop').innerText=tot; document.getElementById('totM').innerText=tot; document.getElementById('cartCountTop').innerText=cnt; let lh=''; cart.forEach((c,i)=>{{lh+=`<div class="cart-item"><div><b>${{c.nombre}}</b><br><small>$${{c.precio}} x ${{c.cant}}</small></div><div style="display:flex;align-items:center;gap:6px"><button class="qty-btn" onclick="cambiarCart(${{i}},-1)">-</button><span>${{c.cant}}</span><button class="qty-btn" onclick="cambiarCart(${{i}},1)">+</button></div><div style="color:#FFC107">$${{c.precio*c.cant}}</div></div>`}}); document.getElementById('lista').innerHTML=lh||'Vacío'; }}
            function cambiarCart(i,d){{ cart[i].cant+=d; if(cart[i].cant<1) cart.splice(i,1); up(); }}
            function abrir(){{document.getElementById('modal').style.display='flex'}} function cerrar(){{document.getElementById('modal').style.display='none'}}
            async function enviar(){{
                let n=document.getElementById('nom').value.trim(); let d=document.getElementById('dir').value.trim(); let t=document.getElementById('tel').value.trim(); let nota=document.getElementById('nota').value.trim();
                if(!n||!d){{alert('Nombre y dirección obligatorios');return}}
                if(cart.length===0){{alert('Carrito vacío');return}}
                await fetch('/finalizar-venta', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body: JSON.stringify(cart.map(c=>({{id:c.id, cant:c.cant}})))}});
                let msg=`Hola FENIX! Soy ${{n}}%0ADir: ${{d}}%0ATel: ${{t}}%0A%0APEDIDO:%0A`; 
                cart.forEach(c=>{{msg+=`• ${{c.nombre}} x${{c.cant}} = $${{c.precio*c.cant}}%0A`}}); 
                msg+=`%0ATOTAL: $${{document.getElementById('totM').innerText}}`;
                if(nota) msg+=`%0A%0ANOTA: ${{nota}}`;
                window.open(`https://wa.me/{MI_WHATSAPP}?text=${{msg}}`,'_blank');
                cart=[]; up(); cerrar(); location.reload();
            }}
            render(prods);
        </script>
    </body></html>
    """
    return html
