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

class Pedido(BaseModel):
    nombre: str
    direccion: str
    celular: str
    items: dict
    total: int

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FENIX Distribuciones</title>
<style>
*{box-sizing:border-box} body{margin:0;font-family:Inter,Arial;background:#0f0f10;color:white;overflow-x:hidden}
.topbar{display:flex;justify-content:space-between;align-items:center;padding:12px 20px;background:#0f0f10;border-bottom:1px solid #222;position:sticky;top:0;z-index:20}
.brand{display:flex;align-items:center;gap:10px} .icon{width:42px;height:42px;border-radius:50%;background:#111;object-fit:cover} .brand b{color:#FFC107}
.btn-cart{background:#FFC107;color:#000;padding:10px 16px;border-radius:10px;font-weight:800;border:none;cursor:pointer}
.hero{margin:20px;background:linear-gradient(180deg,#1a1a1e,#15151a);border-radius:20px;padding:28px 30px;border:1px solid #222} .badge{background:#2a2210;color:#FFC107;padding:6px 12px;border-radius:20px;font-size:11px;letter-spacing:1px}
.search-box{background:#1a1a1e;border:1px solid #2a2a2e;border-radius:12px;padding:12px 16px;display:flex;gap:10px;flex:1;max-width:400px;margin:0 20px} .search-box input{background:transparent;border:none;color:white;width:100%;outline:none}
.pills{display:flex;gap:8px;flex-wrap:wrap;padding:10px 20px} .pill{background:#1a1a1e;border:1px solid #2a2a2e;color:#aaa;padding:8px 16px;border-radius:20px;cursor:pointer;font-size:13px} .pill.active{background:#FFC107;color:#000;border-color:#FFC107;font-weight:800}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px;padding:20px;max-width:1300px;margin:auto}
.card{background:#1a1a1e;border:1px solid #25252b;border-radius:18px;overflow:hidden;transition:.2s} .card:hover{border-color:#FFC10744;transform:translateY(-2px)}
.card-img{height:210px;background:#111;position:relative} .card-img img{width:100%;height:100%;object-fit:cover}
.card-body{padding:14px} .card-body b{font-size:14px;display:block;min-height:36px} .price{color:#FFC107;font-weight:800;margin-top:6px}
.qty-row{display:flex;align-items:center;gap:8px;margin-top:10px} .qty-btn{width:32px;height:32px;border-radius:8px;border:1px solid #333;background:#222;color:white;cursor:pointer}
.btn-add{width:100%;background:#FFC107;color:#000;border:none;padding:11px;border-radius:10px;font-weight:800;margin-top:12px;cursor:pointer}

/* === CARRITO ARREGLADO - MANTIENE TU ESTILO ORIGINAL === */
#modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.78);z-index:50;justify-content:center;align-items:center;padding:12px}
.modal-box{background:#1a1a1e;border:1px solid #2a2a2e;border-radius:16px;max-width:420px;width:95%;max-height:90vh;display:flex;flex-direction:column;padding:22px;gap:10px;box-shadow:0 20px 60px rgba(0,0,0,.6)}
#lista{flex:1;overflow-y:auto;max-height:38vh;padding-right:8px;margin:8px 0}
#lista::-webkit-scrollbar{width:6px} #lista::-webkit-scrollbar-thumb{background:#333;border-radius:10px} #lista::-webkit-scrollbar-track{background:transparent}
.cart-item{padding:12px 0;border-bottom:1px solid #24242a}
.cart-item:last-child{border:none}
.inp{width:100%;padding:11px;border-radius:8px;border:1px solid #2a2a2e;background:#111;color:white;margin-top:8px;outline:none}
.inp:focus{border-color:#FFC107}
.btn-wsp{background:#25D366;color:white;border:none;width:100%;padding:13px;border-radius:10px;font-weight:800;cursor:pointer;margin-top:10px;font-size:14px}
.btn-continue{background:transparent;color:#888;border:none;padding:10px;cursor:pointer;width:100%}

/* === SECCION RESEÑAS NUEVA === */
.reviews{padding:50px 20px;max-width:1300px;margin:50px auto 0 auto;border-top:1px solid #1f1f25}
.reviews h2{text-align:center;font-size:28px;margin:0} .reviews .sub{text-align:center;color:#888;margin:8px 0 28px 0}
.reviews-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.review-card{background:#1a1a1e;border:1px solid #25252b;border-radius:16px;padding:20px;position:relative}
.stars{color:#FFC107;font-size:18px;margin-bottom:10px} .review-card p{color:#ccc;line-height:1.4;font-size:14px}
.review-name{color:#FFC107;font-weight:bold;margin-top:14px;font-size:14px} .review-role{font-size:11px;color:#666;margin-top:2px}
.badge-verified{position:absolute;top:16px;right:16px;background:#1a2a1a;color:#25D366;font-size:10px;padding:4px 8px;border-radius:20px;border:1px solid #2a4a2a}
</style>
</head>
<body>
<div class="topbar"><div class="brand"><img src="/static/logo.png" onerror="this.style.display='none'" class="icon"><div><b>FÉNIX</b> Distribuciones</div></div><button class="btn-cart" onclick="abrirCarrito()">🛒 <span id="cart-count">0</span></button></div>

<div class="hero"><span class="badge">CATÁLOGO OFICIAL</span><h1 style="margin:12px 0 8px 0">Insumos para Barbería de Alta Calidad</h1><p style="color:#888;margin:0">Elige la cantidad y haz tu pedido directo a WhatsApp. Entrega en Bogotá.</p></div>

<div style="display:flex;justify-content:center;padding:0 20px"><div class="search-box">🔍<input id="busc" placeholder="Buscar productos... (ej: dorco, capa, cera)" onkeyup="filtrar()"></div></div>
<div class="pills" id="pills"></div>
<div id="grid" class="grid"></div>

<!-- RESEÑAS -->
<div class="reviews">
<h2>⭐ Lo que dicen nuestros clientes</h2>
<p class="sub">Más de 200 barberos ya confían en FÉNIX</p>
<div class="reviews-grid">
<div class="review-card"><span class="badge-verified">✓ Verificado</span><div class="stars">★★★★★</div><p>"Excelente calidad en las cuchillas Dorco y entrega super rápida en Bogotá. Mis clientes notan la diferencia en el afeitado."</p><div class="review-name">Andrés Molina</div><div class="review-role">Barbería La 93 - Bogotá</div></div>
<div class="review-card"><span class="badge-verified">✓ Verificado</span><div class="stars">★★★★★</div><p>"Los precios más competitivos que encontré. La capa profesional salió buenísima y duradera, nada de plástico barato."</p><div class="review-name">Cristian Durán</div><div class="review-role">Fades & Co - Chapinero</div></div>
<div class="review-card"><span class="badge-verified">✓ Verificado</span><div class="stars">★★★★★</div><p>"Hago pedido cada 15 días por WhatsApp y siempre llega completo. La atención por WhatsApp es 10/10."</p><div class="review-name">Yenifer Londoño</div><div class="review-role">Studio Barber - Usaquén</div></div>
</div>
</div>

<div id="modal">
<div class="modal-box">
<h2 style="margin:0">Tu pedido - FÉNIX</h2>
<div id="lista"></div>
<h3 style="margin:10px 0 0 0">Total: $<span id="tot">0</span></h3>
<input class="inp" id="nom" placeholder="Nombre *">
<input class="inp" id="dir" placeholder="Dirección *">
<input class="inp" id="cel" placeholder="Celular *">
<button class="btn-wsp" onclick="enviarWsp()">📲 Enviar pedido por WhatsApp</button>
<button class="btn-continue" onclick="cerrarCarrito()">Seguir comprando</button>
</div>
</div>

<script>
const productosFallback = [
{id:1,nombre:"cuchillas dorco x 60 hojas individuales",precio:15000,cat:"CUCHILLAS",img:"https://i.imgur.com/8Km9tLL.png",stock:20},
{id:2,nombre:"losion after shave 500ml",precio:18000,cat:"LOCIÓN",img:"https://i.imgur.com/8Km9tLL.png",stock:15},
{id:3,nombre:"capa profesional",precio:20000,cat:"CAPAS",img:"https://i.imgur.com/8Km9tLL.png",stock:10},
{id:4,nombre:"cuelleras 5 rollos x 120 tiras c/u total 600",precio:19000,cat:"CUELLERAS",img:"https://i.imgur.com/8Km9tLL.png",stock:25},
{id:5,nombre:"cera para cabello acabado mate",precio:24000,cat:"CERAS",img:"https://i.imgur.com/8Km9tLL.png",stock:12}
];
let productos = productosFallback;
let carrito = {};
let catActiva = "TODOS";

async function cargarProductos(){
 try{
  let r = await fetch('/api/productos');
  let data = await r.json();
  if(data && data.length>0) productos = data;
 }catch(e){ console.log("usando fallback"); }
 renderPills(); renderGrid(productos);
}

function renderPills(){
 const cats=["TODOS",...new Set(productos.map(p=>p.cat || p.categoria || "OTROS"))];
 document.getElementById("pills").innerHTML=cats.map(c=>`<button class="pill ${c==catActiva?'active':''}" onclick="filtrarCat('${c}')">${c}</button>`).join("");
}
function renderGrid(lista){
 document.getElementById("grid").innerHTML=lista.map(p=>`
 <div class="card">
  <div class="card-img"><img src="${p.img || p.imagen || 'https://via.placeholder.com/300/111/FFC107?text=FENIX'}" onerror="this.src='https://via.placeholder.com/300/111/FFC107?text=FENIX'"></div>
  <div class="card-body">
   <b>${p.nombre}</b>
   <div class="price">$${Number(p.precio).toLocaleString()}</div>
   <small style="color:#666">Stock: ${p.stock || 10}</small>
   <div class="qty-row"><button class="qty-btn" onclick="cambiar(${p.id},-1)">-</button><span id="q-${p.id}">${carrito[p.id]||1}</span><button class="qty-btn" onclick="cambiar(${p.id},1)">+</button></div>
   <button class="btn-add" onclick="agregar(${p.id})">Agregar</button>
  </div>
 </div>`).join("");
}
function cambiar(id,d){ let el=document.getElementById("q-"+id); if(!el) return; let v=parseInt(el.innerText)+d; if(v<1)v=1; el.innerText=v; if(carrito[id]){carrito[id]=v; actualizarModal();}}
function agregar(id){ let cant=parseInt(document.getElementById("q-"+id)?.innerText || "1"); carrito[id]=(carrito[id]||0)+cant; actualizarCont(); abrirCarrito(); }
function actualizarCont(){ document.getElementById("cart-count").innerText=Object.values(carrito).reduce((a,b)=>a+b,0); }
function filtrar(){ let t=document.getElementById("busc").value.toLowerCase(); renderGrid(productos.filter(p=>p.nombre.toLowerCase().includes(t) && (catActiva=="TODOS" || (p.cat||p.categoria)==catActiva))); }
function filtrarCat(c){ catActiva=c; renderPills(); filtrar(); }
function abrirCarrito(){ actualizarModal(); document.getElementById("modal").style.display="flex"; }
function cerrarCarrito(){ document.getElementById("modal").style.display="none"; }
function actualizarModal(){
 let lista=document.getElementById("lista"); let total=0; let html="";
 for(let id in carrito){
  let p=productos.find(x=>x.id==id || x.id==parseInt(id)); if(!p) continue; let cant=carrito[id]; let sub=p.precio*cant; total+=sub;
  html+=`<div class="cart-item"><div style="flex:1"><b style="font-size:13px">${p.nombre}</b><br><small style="color:#888">$${p.precio} x ${cant}</small></div><div style="text-align:right"><div class="qty-row" style="justify-content:flex-end"><button class="qty-btn" onclick="restar(${p.id})">-</button><span>${cant}</span><button class="qty-btn" onclick="sumar(${p.id})">+</button></div><b style="color:#FFC107">$${sub.toLocaleString()}</b></div></div>`;
 }
 if(html=="") html="<p style='color:#888;text-align:center;padding:20px'>Tu carrito está vacío<br>Agrega productos para verlos aquí</p>";
 lista.innerHTML=html; document.getElementById("tot").innerText=total.toLocaleString();
}
function sumar(id){carrito[id]++; actualizarCont(); actualizarModal();}
function restar(id){carrito[id]--; if(carrito[id]<=0) delete carrito[id]; actualizarCont(); actualizarModal();}
function enviarWsp(){
 let nom=document.getElementById("nom").value.trim(), dir=document.getElementById("dir").value.trim(), cel=document.getElementById("cel").value.trim();
 if(!nom||!dir||!cel){alert("Por favor completa Nombre, Dirección y Celular");return;}
 if(Object.keys(carrito).length==0){alert("Tu carrito está vacío");return;}
 let msg=`Hola FÉNIX Distribuciones, quiero hacer este pedido:%0A%0A`; 
 for(let id in carrito){ let p=productos.find(x=>x.id==id || x.id==parseInt(id)); msg+=`• ${p.nombre} x ${carrito[id]} = $${(p.precio*carrito[id]).toLocaleString()}%0A`; }
 msg+=`%0A*Total: $${document.getElementById("tot").innerText}*%0A%0A*Datos de entrega:*%0ANombre: ${nom}%0ADirección: ${dir}%0ACelular: ${cel}`;
 window.open(`https://wa.me/573000000000?text=${msg}`,"_blank");
}
cargarProductos();
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE

@app.get("/api/productos")
async def get_productos():
    try:
        res = supabase.table("productos").select("*").execute()
        if res.data:
            return res.data
    except Exception as e:
        print("Error supabase:", e)
    # fallback si no hay tabla
    return [
        {"id":1,"nombre":"cuchillas dorco x 60 hojas individuales","precio":15000,"cat":"CUCHILLAS","img":"","stock":20},
        {"id":2,"nombre":"losion after shave 500ml","precio":18000,"cat":"LOCIÓN","img":"","stock":15},
        {"id":3,"nombre":"capa profesional","precio":20000,"cat":"CAPAS","img":"","stock":10},
        {"id":4,"nombre":"cuelleras 5 rollos x 120 tiras c/u total 600","precio":19000,"cat":"CUELLERAS","img":"","stock":25},
        {"id":5,"nombre":"cera para cabello acabado mate","precio":24000,"cat":"CERAS","img":"","stock":12},
    ]
