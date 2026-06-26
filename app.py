import tornado.ioloop
import tornado.web
import tornado.escape
import os, json, re, bcrypt, random, string, secrets, urllib.parse
import requests
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from datetime import datetime
from time import monotonic
from jinja2 import Environment, FileSystemLoader, select_autoescape
from database import get_connection, init_db, slugify, MARCAS_MOTO, USD_RATE, STORES_MDQ

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
PORT = int(os.environ.get('PORT', 8889))
DEBUG_DEFAULT = 'true' if not os.environ.get('COOKIE_SECRET') else 'false'
DEBUG = os.environ.get('DEBUG', DEBUG_DEFAULT).lower() in ('1', 'true', 'yes')
COOKIE_SECRET = os.environ.get('COOKIE_SECRET')
if not COOKIE_SECRET:
    if DEBUG:
        COOKIE_SECRET = 'dev-cookie-secret'
    else:
        raise RuntimeError('COOKIE_SECRET is required when DEBUG=false')
SECURE_COOKIES = os.environ.get('SECURE_COOKIES', '').lower() in ('1', 'true', 'yes')
# Las cuentas demo solo se muestran en desarrollo (o si DEMO_MODE se fuerza a true).
DEMO_MODE = os.environ.get('DEMO_MODE', 'true' if DEBUG else 'false').lower() in ('1', 'true', 'yes')
RATE_LIMITS = {}

# ── Google OAuth (opcional: si no hay credenciales, el boton queda oculto) ────
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', '').strip()
GOOGLE_AUTH_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and GOOGLE_REDIRECT_URI)
GOOGLE_AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'

jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(['html'])
)

def ars(val):
    if val is None: return '$0'
    return f"${float(val):,.0f}".replace(',', '.')

def usd(val):
    if val is None: return 'USD 0'
    return f"USD {float(val):,.2f}"

def abs_filter(val):
    try: return abs(float(val))
    except: return val

jinja_env.filters['ars'] = ars
jinja_env.filters['usd'] = usd
jinja_env.filters['abs'] = abs_filter
jinja_env.filters['tojson'] = lambda v: json.dumps(v, ensure_ascii=False)

def get_nav_categories():
    conn = get_connection()
    parents = conn.execute(
        "SELECT * FROM categories WHERE parent_id IS NULL AND vertical IN ('REPUESTOS','ACCESORIOS') "
        "ORDER BY position").fetchall()
    result = []
    for p in parents:
        subs = conn.execute(
            "SELECT * FROM categories WHERE parent_id=? ORDER BY id", (p['id'],)).fetchall()
        result.append({'parent': dict(p), 'subs': [dict(s) for s in subs]})
    conn.close()
    return result

def get_market_prices():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM market_prices ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def unique_product_slug(conn, title):
    base = slugify(title) or 'producto'
    candidate = base
    suffix = 2
    while conn.execute("SELECT 1 FROM products WHERE slug=?", (candidate,)).fetchone():
        candidate = f'{base}-{suffix}'
        suffix += 1
    return candidate

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('X-Content-Type-Options', 'nosniff')
        self.set_header('X-Frame-Options', 'DENY')
        self.set_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.set_header('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')

    def cookie_options(self):
        return {'httponly': True, 'secure': SECURE_COOKIES, 'samesite': 'Lax'}

    def client_ip(self):
        forwarded = self.request.headers.get('X-Forwarded-For', '')
        return (forwarded.split(',')[0].strip() if forwarded else self.request.remote_ip) or 'unknown'

    def enforce_rate_limit(self, scope, limit, window_seconds):
        key = f'{scope}:{self.client_ip()}'
        now = monotonic()
        hits = [ts for ts in RATE_LIMITS.get(key, []) if now - ts < window_seconds]
        if len(hits) >= limit:
            self.set_status(429)
            self.write('Demasiados intentos. Espera unos minutos y volve a probar.')
            RATE_LIMITS[key] = hits
            return False
        hits.append(now)
        RATE_LIMITS[key] = hits
        return True

    def get_current_user(self):
        uid = self.get_secure_cookie('uid')
        if not uid: return None
        conn = get_connection()
        user = conn.execute("SELECT * FROM users WHERE id=?", (int(uid),)).fetchone()
        conn.close()
        return dict(user) if user else None

    def render_template(self, template_name, **kwargs):
        user = self.get_current_user()
        nav_cats = get_nav_categories()
        market_prices = get_market_prices()
        tmpl = jinja_env.get_template(template_name)
        html = tmpl.render(
            current_user=user,
            nav_categories=nav_cats,
            market_prices=market_prices,
            request=self.request,
            flash_msg=self.get_secure_cookie('flash'),
            xsrf_form_html=self.xsrf_form_html(),
            MARCAS_MOTO=MARCAS_MOTO,
            demo_mode=DEMO_MODE,
            google_auth_enabled=GOOGLE_AUTH_ENABLED,
            **kwargs
        )
        if self.get_secure_cookie('flash'):
            self.clear_cookie('flash')
        self.write(html)

    def flash(self, msg):
        self.set_secure_cookie('flash', msg, expires_days=0.001, **self.cookie_options())

    def require_login(self):
        if not self.get_current_user():
            self.redirect('/auth/login?next=' + self.request.uri)
            return False
        return True

    def require_seller(self):
        user = self.get_current_user()
        if not user or user['role'] not in ('VENDEDOR', 'ADMIN'):
            self.redirect('/auth/login?next=' + self.request.uri)
            return False
        return True


class HomeHandler(BaseHandler):
    def get(self):
        conn = get_connection()
        featured = conn.execute(
            "SELECT p.*,sp.company_name,sp.verified FROM products p "
            "JOIN seller_profiles sp ON sp.user_id=p.seller_id "
            "WHERE p.status='ACTIVO' AND p.featured=1 ORDER BY RANDOM() LIMIT 12"
        ).fetchall()
        most_viewed = conn.execute(
            "SELECT p.*,sp.company_name,sp.verified FROM products p "
            "JOIN seller_profiles sp ON sp.user_id=p.seller_id "
            "WHERE p.status='ACTIVO' ORDER BY p.views DESC LIMIT 16"
        ).fetchall()
        recent = conn.execute(
            "SELECT p.*,sp.company_name FROM products p "
            "JOIN seller_profiles sp ON sp.user_id=p.seller_id "
            "WHERE p.status='ACTIVO' ORDER BY p.created_at DESC LIMIT 8"
        ).fetchall()
        cat_counts = conn.execute(
            """SELECT c.id,c.name,c.slug,c.icon,c.description,
               COUNT(p.id) as total
               FROM categories c
               LEFT JOIN products p ON p.category_id=c.id AND p.status='ACTIVO'
               WHERE c.parent_id IS NULL
               GROUP BY c.id,c.name,c.slug,c.icon,c.description,c.position ORDER BY c.position"""
        ).fetchall()
        total_products = conn.execute("SELECT COUNT(*) FROM products WHERE status='ACTIVO'").fetchone()[0]
        total_sellers = conn.execute("SELECT COUNT(*) FROM seller_profiles").fetchone()[0]
        conn.close()
        self.render_template('home.html',
            featured=[dict(r) for r in featured],
            most_viewed=[dict(r) for r in most_viewed],
            recent=[dict(r) for r in recent],
            cat_counts=[dict(r) for r in cat_counts],
            total_products=total_products,
            total_sellers=total_sellers,
        )


class HealthHandler(BaseHandler):
    def get(self):
        self.write({'status': 'ok'})


class CatalogoHandler(BaseHandler):
    # Subclases (Avisos/Motos/Servicios) pisan estos para filtrar el mismo listado.
    LISTING_TYPES = ('PRODUCTO',)
    VERTICALS = ('REPUESTOS', 'ACCESORIOS')
    TEMPLATE = 'catalogo.html'
    VERTICAL_LABEL = 'Repuestos y Accesorios'
    BASE_URL = '/productos'
    ITEM_NOUN = 'repuestos'

    def get(self):
        conn = get_connection()
        category_slug = self.get_argument('categoria', '')
        search = self.get_argument('q', '').strip()
        condition = self.get_argument('condicion', '')
        brand = self.get_argument('marca', '')
        compat = self.get_argument('compatible', '')
        tienda = self.get_argument('tienda', '')
        vendedor_tipo = self.get_argument('vendedor', '')
        order = self.get_argument('orden', 'relevancia')
        price_min = self.get_argument('precio_min', '')
        price_max = self.get_argument('precio_max', '')
        page = max(1, int(self.get_argument('pagina', 1) or 1))
        per_page = 24

        type_placeholders = ','.join(['?'] * len(self.LISTING_TYPES))
        wheres = ["p.status='ACTIVO'", f"p.listing_type IN ({type_placeholders})"]
        params = list(self.LISTING_TYPES)
        current_cat = None

        if vendedor_tipo in ('particular', 'concesionaria'):
            wheres.append("p.seller_kind=?")
            params.append(vendedor_tipo.upper())

        if category_slug:
            cat = conn.execute("SELECT * FROM categories WHERE slug=?", (category_slug,)).fetchone()
            if cat:
                current_cat = dict(cat)
                if cat['parent_id'] is None:
                    sub_ids = [r['id'] for r in conn.execute(
                        "SELECT id FROM categories WHERE parent_id=?", (cat['id'],)).fetchall()]
                    all_ids = [cat['id']] + sub_ids
                    wheres.append(f"p.category_id IN ({','.join(['?']*len(all_ids))})")
                    params += all_ids
                else:
                    wheres.append("p.category_id=?"); params.append(cat['id'])

        if search:
            wheres.append("(p.title LIKE ? OR p.description LIKE ? OR p.brand LIKE ? OR p.compatible_models LIKE ?)")
            params += [f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%']
        if condition:
            wheres.append("p.condition=?"); params.append(condition)
        if brand:
            wheres.append("p.brand=?"); params.append(brand)
        if compat:
            wheres.append("p.compatible_models LIKE ?"); params.append(f'%{compat}%')
        if price_min:
            try: wheres.append("p.price>=?"); params.append(float(price_min))
            except: pass
        if price_max:
            try: wheres.append("p.price<=?"); params.append(float(price_max))
            except: pass
        if tienda:
            try: wheres.append("p.seller_id=?"); params.append(int(tienda))
            except ValueError: pass

        where_sql = " AND ".join(wheres)
        order_sql = {
            'relevancia': 'p.leads_count DESC, p.views DESC',
            'mas-vistos': 'p.views DESC',
            'precio-asc': 'p.price ASC',
            'precio-desc': 'p.price DESC',
            'recientes': 'p.created_at DESC',
        }.get(order, 'p.leads_count DESC, p.views DESC')

        total = conn.execute(f"SELECT COUNT(*) FROM products p WHERE {where_sql}", params).fetchone()[0]
        products = conn.execute(
            f"""SELECT p.*,sp.company_name,sp.verified,sp.rating,
                c.name as cat_name, c.slug as cat_slug
                FROM products p
                JOIN seller_profiles sp ON sp.user_id=p.seller_id
                JOIN categories c ON c.id=p.category_id
                WHERE {where_sql} ORDER BY {order_sql}
                LIMIT ? OFFSET ?""",
            params + [per_page, (page-1)*per_page]
        ).fetchall()

        brands_available = conn.execute(
            f"SELECT DISTINCT brand FROM products p WHERE {where_sql} AND brand IS NOT NULL ORDER BY brand",
            params).fetchall()
        vertical_placeholders = ','.join(['?'] * len(self.VERTICALS))
        all_cats = conn.execute(
            "SELECT c.id,c.name,c.slug,c.icon,c.description,c.parent_id,c.position,c.vertical,c.image_url, COUNT(p.id) as cnt FROM categories c "
            "LEFT JOIN products p ON p.category_id=c.id AND p.status='ACTIVO' "
            f"WHERE c.parent_id IS NULL AND c.vertical IN ({vertical_placeholders}) "
            "GROUP BY c.id,c.name,c.slug,c.icon,c.description,c.parent_id,c.position,c.vertical,c.image_url ORDER BY c.position", list(self.VERTICALS)).fetchall()
        sellers_for_filter = conn.execute(
            "SELECT sp.user_id as id, sp.company_name, sp.verified, "
            "COUNT(p.id) as cnt FROM seller_profiles sp "
            "LEFT JOIN products p ON p.seller_id=sp.user_id AND p.status='ACTIVO' "
            "GROUP BY sp.user_id, sp.company_name, sp.verified ORDER BY cnt DESC"
        ).fetchall()
        conn.close()

        total_pages = (total + per_page - 1) // per_page
        self.render_template(self.TEMPLATE,
            products=[dict(r) for r in products],
            current_cat=current_cat,
            total=total, page=page, total_pages=total_pages,
            search=search, condition=condition, brand=brand,
            compat=compat, order=order, price_min=price_min, price_max=price_max,
            category_slug=category_slug, tienda=tienda, vendedor_tipo=vendedor_tipo,
            brands_available=[r['brand'] for r in brands_available],
            all_cats=[dict(r) for r in all_cats],
            sellers_for_filter=[dict(r) for r in sellers_for_filter],
            vertical_label=self.VERTICAL_LABEL,
            base_url=self.BASE_URL, item_noun=self.ITEM_NOUN,
            show_vendedor_filter=(self.LISTING_TYPES == ('MOTO',)),
            vendedor_tipo_arg=vendedor_tipo,
        )


class AvisosHandler(CatalogoHandler):
    LISTING_TYPES = ('AVISO',)
    VERTICALS = ('AVISOS',)
    VERTICAL_LABEL = 'Avisos'
    BASE_URL = '/avisos'
    ITEM_NOUN = 'avisos'


class MotosHandler(CatalogoHandler):
    LISTING_TYPES = ('MOTO',)
    VERTICALS = ('MOTOS',)
    VERTICAL_LABEL = 'Motos'
    BASE_URL = '/motos'
    ITEM_NOUN = 'motos'


class ServiciosHandler(BaseHandler):
    def get(self):
        conn = get_connection()
        rubro = self.get_argument('rubro', '')
        search = self.get_argument('q', '').strip()
        wheres, params = ["1=1"], []
        if rubro:
            wheres.append("rubro=?"); params.append(rubro)
        if search:
            wheres.append("(name LIKE ? OR description LIKE ?)")
            params += [f'%{search}%', f'%{search}%']
        where_sql = " AND ".join(wheres)
        services = conn.execute(
            f"SELECT * FROM services WHERE {where_sql} ORDER BY verified DESC, id DESC",
            params).fetchall()
        rubros = conn.execute(
            "SELECT DISTINCT rubro FROM services WHERE rubro IS NOT NULL ORDER BY rubro").fetchall()
        conn.close()
        self.render_template('servicios.html',
            services=[dict(r) for r in services],
            rubro=rubro, search=search,
            rubros_available=[r['rubro'] for r in rubros],
        )


class ProductoHandler(BaseHandler):
    def get(self, slug):
        conn = get_connection()
        prod = conn.execute(
            """SELECT p.*,
               sp.company_name,sp.verified,sp.rating,sp.total_reviews,
               sp.response_rate,sp.response_time,sp.member_since,sp.city as seller_city,
               sp.address as seller_address, sp.phone as seller_phone,
               sp.whatsapp as seller_whatsapp,
               u.id as seller_uid,
               c.name as cat_name, c.slug as cat_slug,
               pc.name as parent_cat_name, pc.slug as parent_cat_slug
               FROM products p
               JOIN seller_profiles sp ON sp.user_id=p.seller_id
               JOIN users u ON u.id=p.seller_id
               JOIN categories c ON c.id=p.category_id
               LEFT JOIN categories pc ON pc.id=c.parent_id
               WHERE p.slug=? AND p.status='ACTIVO'""", (slug,)
        ).fetchone()
        if not prod:
            self.set_status(404); self.write("Producto no encontrado"); return

        conn.execute("UPDATE products SET views=views+1 WHERE slug=?", (slug,))
        conn.commit()

        prod = dict(prod)
        prod['images_list'] = json.loads(prod.get('images') or '[]') or [prod.get('image_url')]
        prod['compat_list'] = json.loads(prod.get('compatible_models') or '[]')
        prod['tags_list'] = json.loads(prod.get('tags') or '[]')

        similar = conn.execute(
            """SELECT p.*,sp.company_name,sp.verified FROM products p
               JOIN seller_profiles sp ON sp.user_id=p.seller_id
               WHERE p.category_id=? AND p.slug!=? AND p.status='ACTIVO'
               ORDER BY RANDOM() LIMIT 6""",
            (prod['category_id'], slug)
        ).fetchall()

        reviews = conn.execute(
            "SELECT * FROM reviews WHERE seller_id=? ORDER BY created_at DESC LIMIT 5",
            (prod['seller_uid'],)).fetchall()

        other_seller = conn.execute(
            "SELECT p.*,sp.company_name FROM products p JOIN seller_profiles sp ON sp.user_id=p.seller_id "
            "WHERE p.seller_id=? AND p.slug!=? AND p.status='ACTIVO' LIMIT 4",
            (prod['seller_uid'], slug)).fetchall()

        conn.close()
        self.render_template('producto.html',
            prod=prod,
            similar=[dict(r) for r in similar],
            reviews=[dict(r) for r in reviews],
            other_seller=[dict(r) for r in other_seller],
        )

    def post(self, slug):
        if not self.enforce_rate_limit('lead', 5, 300):
            return
        conn = get_connection()
        prod = conn.execute("SELECT id,seller_id,title FROM products WHERE slug=?", (slug,)).fetchone()
        if not prod:
            self.redirect('/'); return

        name = self.get_argument('buyer_name', '').strip()
        email = self.get_argument('buyer_email', '').strip()
        phone = self.get_argument('buyer_phone', '').strip()
        message = self.get_argument('message', '').strip()

        if name and email:
            conn.execute(
                "INSERT INTO leads(product_id,seller_id,buyer_name,buyer_email,buyer_phone,message) VALUES(?,?,?,?,?,?)",
                (prod['id'], prod['seller_id'], name, email, phone, message))
            conn.execute("UPDATE products SET leads_count=leads_count+1 WHERE id=?", (prod['id'],))
            conn.execute("UPDATE seller_profiles SET total_leads=total_leads+1 WHERE user_id=?", (prod['seller_id'],))
            conn.commit()
            self.flash('Tu consulta fue enviada. Te contactaran a la brevedad.')

        conn.close()
        self.redirect(f'/producto/{slug}#contacto')


class BusquedaHandler(BaseHandler):
    def get(self):
        q = self.get_argument('q', '').strip()
        if not q:
            self.redirect('/productos'); return

        conn = get_connection()
        results = conn.execute(
            """SELECT p.*,sp.company_name,sp.verified,c.name as cat_name,c.slug as cat_slug
               FROM products p
               JOIN seller_profiles sp ON sp.user_id=p.seller_id
               JOIN categories c ON c.id=p.category_id
               WHERE p.status='ACTIVO' AND (
                   p.title LIKE ? OR p.brand LIKE ? OR p.description LIKE ?
                   OR p.compatible_models LIKE ? OR p.model LIKE ?
               ) ORDER BY p.views DESC LIMIT 48""",
            [f'%{q}%']*5
        ).fetchall()
        conn.close()
        self.render_template('busqueda.html',
            q=q,
            results=[dict(r) for r in results],
            total=len(results)
        )


class TiendasHandler(BaseHandler):
    def get(self):
        conn = get_connection()
        sellers = conn.execute(
            """SELECT sp.*, u.email FROM seller_profiles sp
               JOIN users u ON u.id=sp.user_id
               WHERE sp.lat IS NOT NULL ORDER BY sp.verified DESC, sp.rating DESC"""
        ).fetchall()
        conn.close()
        sellers_list = []
        for s in sellers:
            d = dict(s)
            d['brands_list'] = json.loads(d.get('brands_json') or '[]')
            sellers_list.append(d)
        self.render_template('tiendas.html', sellers=sellers_list)


class PerfilVendedorHandler(BaseHandler):
    def get(self, uid):
        conn = get_connection()
        seller = conn.execute(
            "SELECT u.*,sp.* FROM users u JOIN seller_profiles sp ON sp.user_id=u.id WHERE u.id=?",
            (int(uid),)).fetchone()
        if not seller:
            self.set_status(404); self.write("Vendedor no encontrado"); return

        products = conn.execute(
            "SELECT * FROM products WHERE seller_id=? AND status='ACTIVO' ORDER BY views DESC LIMIT 24",
            (int(uid),)).fetchall()
        reviews = conn.execute(
            "SELECT * FROM reviews WHERE seller_id=? ORDER BY created_at DESC LIMIT 10",
            (int(uid),)).fetchall()
        stats = conn.execute(
            "SELECT COUNT(*) as total, SUM(views) as total_views, SUM(leads_count) as total_leads "
            "FROM products WHERE seller_id=? AND status='ACTIVO'", (int(uid),)).fetchone()
        conn.close()
        s = dict(seller)
        s['brands_list'] = json.loads(s.get('brands_json') or '[]')
        self.render_template('perfil_vendedor.html',
            seller=s,
            products=[dict(p) for p in products],
            reviews=[dict(r) for r in reviews],
            stats=dict(stats) if stats else {}
        )


class LoginHandler(BaseHandler):
    def get(self):
        self.render_template('auth/login.html', error=None,
                             next_url=self.get_argument('next', '/'))

    def post(self):
        if not self.enforce_rate_limit('login', 10, 300):
            return
        email = self.get_argument('email', '').strip().lower()
        password = self.get_argument('password', '').strip()
        next_url = self.get_argument('next', '/')
        conn = get_connection()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if user and bcrypt.checkpw(password.encode(), user['password'].encode()):
            self.set_secure_cookie('uid', str(user['id']), expires_days=30, **self.cookie_options())
            if user['role'] == 'VENDEDOR':
                self.redirect('/mi-cuenta/dashboard')
            else:
                self.redirect(next_url if next_url.startswith('/') else '/')
        else:
            self.render_template('auth/login.html',
                                 error='Email o contrasena incorrectos.',
                                 next_url=next_url)


class RegisterHandler(BaseHandler):
    def get(self):
        self.render_template('auth/register.html', error=None)

    def post(self):
        if not self.enforce_rate_limit('register', 5, 3600):
            return
        name = self.get_argument('name', '').strip()
        email = self.get_argument('email', '').strip().lower()
        password = self.get_argument('password', '').strip()
        role = self.get_argument('role', 'COMPRADOR')
        company = self.get_argument('company_name', '').strip()

        if not name or not email or len(password) < 6:
            self.render_template('auth/register.html', error='Completa todos los campos correctamente.')
            return

        conn = get_connection()
        existing = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if existing:
            conn.close()
            self.render_template('auth/register.html', error='Ya existe una cuenta con ese email.')
            return

        pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        conn.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                     (name, email, pw, role))
        uid = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()[0]

        if role == 'VENDEDOR' and company:
            conn.execute(
                "INSERT INTO seller_profiles(user_id,company_name) VALUES(?,?)",
                (uid, company))

        conn.commit()
        conn.close()
        self.set_secure_cookie('uid', str(uid), expires_days=30, **self.cookie_options())
        self.redirect('/mi-cuenta/dashboard' if role == 'VENDEDOR' else '/')


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('uid')
        self.redirect('/')


class GoogleAuthHandler(BaseHandler):
    def get(self):
        if not GOOGLE_AUTH_ENABLED:
            self.redirect('/auth/login')
            return
        state = secrets.token_urlsafe(24)
        self.set_secure_cookie('oauth_state', state, expires_days=0.02, **self.cookie_options())
        next_url = self.get_argument('next', '/')
        self.set_secure_cookie('oauth_next', next_url, expires_days=0.02, **self.cookie_options())
        params = {
            'client_id': GOOGLE_CLIENT_ID,
            'redirect_uri': GOOGLE_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state,
            'access_type': 'online',
            'prompt': 'select_account',
        }
        self.redirect(f"{GOOGLE_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}")


class GoogleAuthCallbackHandler(BaseHandler):
    def get(self):
        if not GOOGLE_AUTH_ENABLED:
            self.redirect('/auth/login')
            return
        if self.get_argument('error', ''):
            self.redirect('/auth/login')
            return

        state = self.get_argument('state', '')
        cookie_state = self.get_secure_cookie('oauth_state')
        self.clear_cookie('oauth_state')
        if not state or not cookie_state or state != cookie_state.decode():
            self.set_status(400)
            self.write('Estado OAuth invalido o expirado. Volve a intentar.')
            return

        next_cookie = self.get_secure_cookie('oauth_next')
        next_url = next_cookie.decode() if next_cookie else '/'
        self.clear_cookie('oauth_next')

        code = self.get_argument('code', '')
        try:
            token_resp = requests.post(GOOGLE_TOKEN_URL, data={
                'code': code,
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'redirect_uri': GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code',
            }, timeout=10)
            token_resp.raise_for_status()
            tokens = token_resp.json()
            idinfo = google_id_token.verify_oauth2_token(
                tokens['id_token'], google_requests.Request(), GOOGLE_CLIENT_ID)
        except Exception:
            self.set_status(400)
            self.write('No se pudo verificar el login con Google. Volve a intentar.')
            return

        google_sub = idinfo['sub']
        email = (idinfo.get('email') or '').strip().lower()
        name = idinfo.get('name') or (email.split('@')[0] if email else 'Usuario Google')
        avatar = idinfo.get('picture')

        conn = get_connection()
        user = conn.execute("SELECT * FROM users WHERE google_id=?", (google_sub,)).fetchone()
        is_new = False
        if not user and email:
            user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
            if user:
                conn.execute("UPDATE users SET google_id=?, avatar_url=? WHERE id=?",
                             (google_sub, avatar, user['id']))
                conn.commit()
        if not user:
            is_new = True
            # Password placeholder inutilizable: el login local sigue exigiendo NOT NULL en SQLite.
            placeholder_pw = bcrypt.hashpw(secrets.token_bytes(32), bcrypt.gensalt()).decode()
            conn.execute(
                "INSERT INTO users(name,email,password,role,auth_provider,google_id,avatar_url) "
                "VALUES(?,?,?,?,?,?,?)",
                (name, email, placeholder_pw, 'COMPRADOR', 'GOOGLE', google_sub, avatar))
            conn.commit()
            user = conn.execute("SELECT * FROM users WHERE google_id=?", (google_sub,)).fetchone()
        conn.close()

        self.set_secure_cookie('uid', str(user['id']), expires_days=30, **self.cookie_options())
        if is_new:
            self.redirect('/auth/onboarding')
        else:
            self.redirect(next_url if next_url.startswith('/') else '/')


class OnboardingHandler(BaseHandler):
    def get(self):
        if not self.require_login(): return
        self.render_template('auth/onboarding.html')

    def post(self):
        if not self.require_login(): return
        user = self.get_current_user()
        role = self.get_argument('role', 'COMPRADOR')
        if role not in ('COMPRADOR', 'VENDEDOR'):
            role = 'COMPRADOR'
        company = self.get_argument('company_name', '').strip()
        conn = get_connection()
        conn.execute("UPDATE users SET role=? WHERE id=?", (role, user['id']))
        if role == 'VENDEDOR' and company:
            existing_sp = conn.execute("SELECT id FROM seller_profiles WHERE user_id=?", (user['id'],)).fetchone()
            if not existing_sp:
                conn.execute("INSERT INTO seller_profiles(user_id,company_name) VALUES(?,?)",
                             (user['id'], company))
        conn.commit()
        conn.close()
        self.redirect('/mi-cuenta/dashboard' if role == 'VENDEDOR' else '/')


# ── VENDEDOR DASHBOARD ─────────────────────────────────────────────────────────
class DashboardHandler(BaseHandler):
    def get(self):
        if not self.require_seller(): return
        user = self.get_current_user()
        conn = get_connection()
        sp = conn.execute("SELECT * FROM seller_profiles WHERE user_id=?", (user['id'],)).fetchone()
        products = conn.execute(
            "SELECT * FROM products WHERE seller_id=? ORDER BY created_at DESC LIMIT 10",
            (user['id'],)).fetchall()
        leads = conn.execute(
            "SELECT l.*,p.title as prod_title FROM leads l JOIN products p ON p.id=l.product_id "
            "WHERE l.seller_id=? ORDER BY l.created_at DESC LIMIT 10", (user['id'],)).fetchall()
        stats = conn.execute(
            "SELECT COUNT(*) as prods, SUM(views) as views, SUM(leads_count) as leads "
            "FROM products WHERE seller_id=? AND status='ACTIVO'", (user['id'],)).fetchone()
        conn.close()
        self.render_template('vendedor/dashboard.html',
            sp=dict(sp) if sp else {},
            products=[dict(p) for p in products],
            leads=[dict(l) for l in leads],
            stats=dict(stats) if stats else {}
        )


class MisProductosHandler(BaseHandler):
    def get(self):
        if not self.require_seller(): return
        user = self.get_current_user()
        conn = get_connection()
        products = conn.execute(
            "SELECT p.*,c.name as cat_name FROM products p JOIN categories c ON c.id=p.category_id "
            "WHERE p.seller_id=? ORDER BY p.created_at DESC", (user['id'],)).fetchall()
        conn.close()
        self.render_template('vendedor/productos.html',
                             products=[dict(p) for p in products])


class NuevoProductoHandler(BaseHandler):
    def get(self):
        if not self.require_seller(): return
        conn = get_connection()
        cats = conn.execute("SELECT * FROM categories ORDER BY parent_id NULLS FIRST, position").fetchall()
        conn.close()
        self.render_template('vendedor/nuevo_producto.html',
                             cats=[dict(c) for c in cats], error=None)

    def post(self):
        if not self.require_seller(): return
        user = self.get_current_user()
        conn = get_connection()
        cats = conn.execute("SELECT * FROM categories ORDER BY parent_id NULLS FIRST, position").fetchall()

        title = self.get_argument('title', '').strip()
        if not title:
            self.render_template('vendedor/nuevo_producto.html',
                                 cats=[dict(c) for c in cats], error='El titulo es obligatorio.')
            conn.close(); return

        slug = unique_product_slug(conn, title)
        price = float(self.get_argument('price', 0) or 0)
        image_url = self.get_argument('image_url', '').strip() or \
            f'https://picsum.photos/seed/{slug}/800/600'
        compat_raw = self.get_argument('compatible_models', '').strip()
        compat = json.dumps([x.strip() for x in compat_raw.split(',') if x.strip()])

        conn.execute("""
            INSERT INTO products(seller_id,category_id,title,slug,short_desc,description,
                price,price_usd,condition,brand,model,compatible_models,stock,
                status,province,city,image_url,images,part_number)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (user['id'],
             int(self.get_argument('category_id', 1)),
             title, slug,
             self.get_argument('short_desc', '').strip(),
             self.get_argument('description', '').strip(),
             price, round(price / USD_RATE, 2),
             self.get_argument('condition', 'NUEVO'),
             self.get_argument('brand', '').strip(),
             self.get_argument('model', '').strip(),
             compat,
             int(self.get_argument('stock', 1) or 1),
             'ACTIVO', 'Buenos Aires', 'Mar del Plata',
             image_url, json.dumps([image_url]),
             self.get_argument('part_number', '').strip()))
        conn.commit()
        conn.close()
        self.flash('Producto publicado correctamente.')
        self.redirect('/mi-cuenta/productos')


class EditarProductoHandler(BaseHandler):
    def get(self, pid):
        if not self.require_seller(): return
        user = self.get_current_user()
        conn = get_connection()
        prod = conn.execute("SELECT * FROM products WHERE id=? AND seller_id=?",
                            (int(pid), user['id'])).fetchone()
        cats = conn.execute("SELECT * FROM categories ORDER BY parent_id NULLS FIRST, position").fetchall()
        conn.close()
        if not prod:
            self.redirect('/mi-cuenta/productos'); return
        p = dict(prod)
        p['compat_str'] = ', '.join(json.loads(p.get('compatible_models') or '[]'))
        self.render_template('vendedor/editar_producto.html',
                             prod=p, cats=[dict(c) for c in cats], error=None)

    def post(self, pid):
        if not self.require_seller(): return
        user = self.get_current_user()
        conn = get_connection()
        price = float(self.get_argument('price', 0) or 0)
        compat_raw = self.get_argument('compatible_models', '').strip()
        compat = json.dumps([x.strip() for x in compat_raw.split(',') if x.strip()])
        image_url = self.get_argument('image_url', '').strip()
        conn.execute("""
            UPDATE products SET title=?,category_id=?,short_desc=?,description=?,
                price=?,price_usd=?,condition=?,brand=?,model=?,compatible_models=?,
                stock=?,image_url=?,images=?,part_number=?
            WHERE id=? AND seller_id=?""",
            (self.get_argument('title', '').strip(),
             int(self.get_argument('category_id', 1)),
             self.get_argument('short_desc', '').strip(),
             self.get_argument('description', '').strip(),
             price, round(price / USD_RATE, 2),
             self.get_argument('condition', 'NUEVO'),
             self.get_argument('brand', '').strip(),
             self.get_argument('model', '').strip(),
             compat,
             int(self.get_argument('stock', 1) or 1),
             image_url, json.dumps([image_url]),
             self.get_argument('part_number', '').strip(),
             int(pid), user['id']))
        conn.commit()
        conn.close()
        self.flash('Producto actualizado.')
        self.redirect('/mi-cuenta/productos')


class LeadsHandler(BaseHandler):
    def get(self):
        if not self.require_seller(): return
        user = self.get_current_user()
        conn = get_connection()
        leads = conn.execute(
            "SELECT l.*,p.title as prod_title,p.slug as prod_slug "
            "FROM leads l JOIN products p ON p.id=l.product_id "
            "WHERE l.seller_id=? ORDER BY l.created_at DESC",
            (user['id'],)).fetchall()
        conn.close()
        self.render_template('vendedor/leads.html',
                             leads=[dict(l) for l in leads])


class PerfilTiendaHandler(BaseHandler):
    def get(self):
        if not self.require_seller(): return
        user = self.get_current_user()
        conn = get_connection()
        sp = conn.execute("SELECT * FROM seller_profiles WHERE user_id=?", (user['id'],)).fetchone()
        conn.close()
        sp_dict = dict(sp) if sp else {}
        sp_dict['brands_str'] = ', '.join(json.loads(sp_dict.get('brands_json') or '[]'))
        self.render_template('vendedor/perfil.html', sp=sp_dict, error=None, success=None)

    def post(self):
        if not self.require_seller(): return
        user = self.get_current_user()
        conn = get_connection()
        brands_raw = self.get_argument('brands', '').strip()
        brands = json.dumps([x.strip() for x in brands_raw.split(',') if x.strip()])
        conn.execute("""
            UPDATE seller_profiles SET description=?,phone=?,whatsapp=?,address=?,
                store_hours=?,website=?,brands_json=?
            WHERE user_id=?""",
            (self.get_argument('description', '').strip(),
             self.get_argument('phone', '').strip(),
             self.get_argument('whatsapp', '').strip(),
             self.get_argument('address', '').strip(),
             self.get_argument('store_hours', '').strip(),
             self.get_argument('website', '').strip(),
             brands, user['id']))
        conn.commit()
        conn.close()
        self.flash('Perfil actualizado.')
        self.redirect('/mi-cuenta/perfil')


def make_app():
    return tornado.web.Application([
        (r'/healthz',                HealthHandler),
        (r'/',                       HomeHandler),
        (r'/productos',              CatalogoHandler),
        (r'/avisos',                 AvisosHandler),
        (r'/motos',                  MotosHandler),
        (r'/servicios',              ServiciosHandler),
        (r'/producto/([^/]+)',       ProductoHandler),
        (r'/buscar',                 BusquedaHandler),
        (r'/tiendas',                TiendasHandler),
        (r'/vendedor/(\d+)',         PerfilVendedorHandler),
        (r'/auth/login',             LoginHandler),
        (r'/auth/register',          RegisterHandler),
        (r'/auth/logout',            LogoutHandler),
        (r'/auth/google',            GoogleAuthHandler),
        (r'/auth/google/callback',   GoogleAuthCallbackHandler),
        (r'/auth/onboarding',        OnboardingHandler),
        (r'/mi-cuenta/dashboard',    DashboardHandler),
        (r'/mi-cuenta/productos',    MisProductosHandler),
        (r'/mi-cuenta/nuevo',        NuevoProductoHandler),
        (r'/mi-cuenta/editar/(\d+)', EditarProductoHandler),
        (r'/mi-cuenta/leads',        LeadsHandler),
        (r'/mi-cuenta/perfil',       PerfilTiendaHandler),
    ],
    cookie_secret=COOKIE_SECRET,
    xsrf_cookies=True,
    xsrf_cookie_kwargs={'secure': SECURE_COOKIES, 'samesite': 'Lax'},
    debug=DEBUG,
    static_path=os.path.join(BASE_DIR, 'static') if os.path.exists(os.path.join(BASE_DIR, 'static')) else None,
    )


if __name__ == '__main__':
    init_db()
    app = make_app()
    app.listen(PORT)
    print(f'\n{"="*50}')
    print(f'  Re-Puestos MDP - Repuestos de Motos')
    print(f'{"="*50}')
    print(f'  http://localhost:{PORT}')
    print(f'{"="*50}')
    print(f'  Tienda 1: tienda1@repuestos.com.ar / Demo1234!')
    print(f'  Tienda 2: tienda2@repuestos.com.ar / Demo1234!')
    print(f'  Comprador: comprador@repuestos.com.ar / Demo1234!')
    print(f'  Ctrl+C para detener\n')
    tornado.ioloop.IOLoop.current().start()
