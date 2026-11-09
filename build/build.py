#!/usr/bin/env python3
"""Baut die statische Website von 1a Clean Car.

Aufruf:  python3 build/build.py
Alle Firmendaten stehen im Block FIRMA. Felder mit None werden auf der Seite
als gelb markierter Platzhalter angezeigt und aus den Google-Daten weggelassen.
"""
import json, os, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://www.1a-cleancar.de"

# ---------------------------------------------------------------- FIRMA ----
FIRMA = {
    "name": "1a Clean Car",
    "strasse": "Kleinfeldweg 40",
    "plz": "69190",
    "ort": "Walldorf",
    "telefon_anzeige": "0151 55870869",
    "telefon": "+4915155870869",
    "whatsapp": "4915155870869",
    "email": "info@1a-cleancar.de",
    "instagram": "https://www.instagram.com/1acleancar.de/",
    "maps": "https://www.google.com/maps/search/?api=1&query=1a+Clean+Car+Kleinfeldweg+40+69190+Walldorf",
    # Öffnungszeiten: Liste von (Tage, Zeit) – z. B. [("Mo–Fr","08:00–18:00"),("Sa","09:00–14:00")]
    "oeffnungszeiten": None,
    # Schema.org-Format, z. B. ["Mo-Fr 08:00-18:00","Sa 09:00-14:00"]
    "oeffnungszeiten_schema": None,
    # Ab-Preise der Pakete, z. B. {"innen":"ab 89 €","aussen":"ab 59 €","komplett":"ab 149 €"}
    "preise": None,
    # Impressum
    "inhaber": None,          # vollständiger Name
    "rechtsform": None,       # z. B. "Einzelunternehmen" oder "GmbH"
    "vertreten_durch": None,  # nur bei GmbH: Geschäftsführer
    "register": None,         # z. B. "Amtsgericht Mannheim, HRB 123456"
    "ust_id": None,           # z. B. "DE123456789"
}
# ----------------------------------------------------------------------------

E = html.escape
TODO = lambda t: f'<span class="todo">{E(t)}</span>'

def wa(text=None):
    u = f"https://wa.me/{FIRMA['whatsapp']}"
    if text:
        from urllib.parse import quote
        u += "?text=" + quote(text)
    return u

def rel(depth, path):
    """Relativer Link, damit die Seite auch unter einer Vorschau-Adresse funktioniert."""
    p = "../" * depth + path
    return p if p else "./"

NAV = [("leistungen/", "Leistungen"), ("leistungen/fahrzeugaufbereitung/", "Fahrzeugaufbereitung"),
       ("#bewertungen", "Bewertungen"), ("kontakt/", "Kontakt")]

LEISTUNGEN = [  # slug, titel, kurz, bild
    ("fahrzeugaufbereitung", "Fahrzeugaufbereitung", "Innen und außen mit Liebe zum Detail – von der Pflege bis zur Komplettaufbereitung.", "porsche-gt3-halle"),
    ("innenreinigung", "Innenreinigung", "Sitze, Fußraum, Kofferraum und Cockpit gründlich gereinigt.", "vn-fussraum-nachher"),
    ("ozonbehandlung", "Ozonbehandlung", "Gegen Rauch-, Tier- und andere hartnäckige Gerüche im Innenraum.", "ozonbehandlung"),
    ("motorraumwaesche", "Motorraumwäsche", "Gründliche, schonende Reinigung und Pflege des Motorraums.", "motorraum-amg"),
    ("lackierung-karosserie", "Lack, Karosserie & Dellen", "Lackierarbeiten, Karosserie-Instandsetzung und Dellentechnik.", "dellentechnik"),
    ("unfallservice", "Unfallservice & Mietwagen", "Wir koordinieren Gutachten, Versicherung und Reparatur – und Sie bleiben mobil.", "unfallservice"),
]
WEITERE = [("Reifenwechsel", "Bereit für die nächste Saison – Reifen- und Räderwechsel."),
           ("Windschutzscheibe", "Ihr Ansprechpartner rund um die Windschutzscheibe."),
           ("Trockeneisreinigung", "Gezielte Reinigung geeigneter Bauteile und schwer zugänglicher Bereiche."),
           ("Individuelle Beratung", "Persönlich, rund ums Auto – sprechen Sie uns einfach an.")]

VN = [("fussraum", "Fußraum"), ("kofferraum", "Kofferraum"), ("heckklappe", "Heckklappenfalz"),
      ("felge", "Felge"), ("motorraum", "Motorraum")]

GALERIE = [("hero-nacht", "Mercedes vor der 1a Clean Car Halle bei Nacht"),
           ("lamborghini-aventador", "Lamborghini Aventador in Hellblau mit geöffneten Türen"),
           ("urus-front", "Lamborghini Urus nach der Aufbereitung"),
           ("porsche-911", "Porsche 911 in Mattgrau"),
           ("maybach", "Mercedes-Maybach S-Klasse nach der Aufbereitung"),
           ("audi-rsq8", "Audi RS Q8 in Kupfer"),
           ("porsche-gt3-front", "Weißer Porsche 911 GT3 in der Halle"),
           ("bmw-x5-front", "Weißer BMW X5 nach der Außenpflege"),
           ("mercedes-cla-halle", "Schwarzer Mercedes CLA in der Halle"),
           ("urus-cockpit", "Cockpit eines Lamborghini Urus nach der Innenreinigung"),
           ("vw-golf-gti", "VW Golf GTI nach der Fahrzeugaufbereitung"),
           ("bmw-3er-gt", "Schwarzer BMW 3er GT frisch aufbereitet")]

REVIEWS = [  # Auszüge aus öffentlichen Google-Bewertungen (gekürzt), nur Vorname + Initial
    ("Unkomplizierte Kontaktaufnahme mit kurzfristiger Terminvereinbarung. Super freundliches Team. Verwendung von namhaften Waschprodukten zu einem fairen Preis.", "Dennis S."),
    ("Absolute Empfehlung! Ich konnte mein Fahrzeug kurzfristig vorbeibringen. Das Ergebnis hat meine Erwartungen übertroffen.", "Google-Rezension"),
    ("Vor dem Verkauf unseres Audi Q2 ließen wir eine Komplettreinigung durchführen. Vor allem stach die Motorreinigung heraus.", "Jürgen K."),
    ("Sympathischer Familienbetrieb mit top Service bei fairen Preisen! Kurzfristige Anfragen sind auch möglich.", "Patrick"),
    ("Sehr guter Service. Habe kurzfristig einen Termin bekommen. Fahrzeugaufbereitung war 1. Klasse. Auto sieht aus wie neu.", "Marc B."),
    ("Wir hatten kurzfristig Hilfe wegen ein paar Kratzern benötigt. Hier wurde sofort geholfen – zu einem super fairen Preis.", "Richard B."),
]
GOOGLE_REVIEWS_URL = FIRMA["maps"]

# ------------------------------------------------------------- Bausteine ----
def img(depth, name, alt, cls="", w=None, h=None, eager=False):
    size = f' width="{w}" height="{h}"' if w else ""
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<img src="{rel(depth, "img/" + name + ".webp")}" alt="{E(alt)}"{c}{size} {load}>'

def schema_business():
    d = {
        "@context": "https://schema.org",
        "@type": "AutoWash",
        "@id": DOMAIN + "/#firma",
        "name": FIRMA["name"],
        "description": "Autoaufbereitung, Fahrzeugpflege, Innenreinigung, Ozonbehandlung, Lack- und Karosseriearbeiten in Walldorf.",
        "url": DOMAIN + "/",
        "telephone": FIRMA["telefon"],
        "email": FIRMA["email"],
        "image": DOMAIN + "/img/og-1a-clean-car.jpg",
        "address": {"@type": "PostalAddress", "streetAddress": FIRMA["strasse"],
                    "postalCode": FIRMA["plz"], "addressLocality": FIRMA["ort"],
                    "addressRegion": "Baden-Württemberg", "addressCountry": "DE"},
        "areaServed": {"@type": "City", "name": "Walldorf"},
        "sameAs": [FIRMA["instagram"]],
        "hasMap": FIRMA["maps"],
    }
    if FIRMA["oeffnungszeiten_schema"]:
        d["openingHours"] = FIRMA["oeffnungszeiten_schema"]
    return d

def page(path, title, desc, body, depth, crumbs=None, extra_schema=None, active=None, noindex=False):
    canonical = DOMAIN + "/" + path
    schemas = [schema_business()]
    if crumbs:
        items = [{"@type": "ListItem", "position": 1, "name": "Startseite", "item": DOMAIN + "/"}]
        for i, (p, n) in enumerate(crumbs, start=2):
            items.append({"@type": "ListItem", "position": i, "name": n, "item": DOMAIN + "/" + p})
        schemas.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items})
    if extra_schema:
        schemas += extra_schema
    nav = "".join(
        f'<li><a href="{rel(depth, "" if h.startswith("#") else h) + (h if h.startswith("#") else "")}"'
        f'{" aria-current=\"page\"" if h == active else ""}>{t}</a></li>' for h, t in NAV)
    robots = '<meta name="robots" content="noindex, follow">' if noindex else ""
    adresse = f'{FIRMA["strasse"]}, {FIRMA["plz"]} {FIRMA["ort"]}'
    doc = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="1a Clean Car">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{DOMAIN}/img/og-1a-clean-car.jpg">
<meta name="theme-color" content="#0b0d0c">
<link rel="icon" href="{rel(depth, 'favicon.svg')}" type="image/svg+xml">
<link rel="stylesheet" href="{rel(depth, 'assets/style.css')}">
{''.join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schemas)}
</head>
<body>
<div class="notice">Neuer Standort: <a href="{FIRMA['maps']}" rel="noopener">{adresse}</a></div>
<header class="site">
 <div class="wrap bar">
  <a class="logo" href="{rel(depth, '')}">1a <span>Clean</span> Car</a>
  <button class="menu-toggle" aria-expanded="false" aria-controls="nav">Menü</button>
  <nav class="main" id="nav" aria-label="Hauptmenü"><ul>{nav}<li><a class="btn sm" href="{rel(depth, 'kontakt/')}">Termin anfragen</a></li></ul></nav>
 </div>
</header>
<main>
{body}
</main>
<footer class="site">
 <div class="wrap">
  <div class="cols">
   <div>
    <a class="logo" href="{rel(depth, '')}">1a <span>Clean</span> Car</a>
    <p style="margin-top:14px">Autoaufbereitung &amp; Fahrzeugpflege in Walldorf.<br>Ihre Zufriedenheit ist unser Erfolg!</p>
   </div>
   <div>
    <h3>Kontakt</h3>
    <ul>
     <li>{FIRMA['strasse']}<br>{FIRMA['plz']} {FIRMA['ort']}</li>
     <li><a href="tel:{FIRMA['telefon']}">{FIRMA['telefon_anzeige']}</a></li>
     <li><a href="mailto:{FIRMA['email']}">{FIRMA['email']}</a></li>
     <li><a href="{wa()}" rel="noopener">WhatsApp</a> · <a href="{FIRMA['instagram']}" rel="noopener">Instagram</a></li>
    </ul>
   </div>
   <div>
    <h3>Leistungen</h3>
    <ul>{''.join(f'<li><a href="{rel(depth, "leistungen/" + s + "/")}">{t}</a></li>' for s, t, _, _ in LEISTUNGEN)}</ul>
   </div>
   <div>
    <h3>Öffnungszeiten</h3>
    {hours_html()}
   </div>
  </div>
  <div class="legal">
   <span>© 2026 1a Clean Car · Walldorf</span>
   <span><a href="{rel(depth, 'impressum/')}">Impressum</a> · <a href="{rel(depth, 'datenschutz/')}">Datenschutz</a></span>
  </div>
 </div>
</footer>
<div class="quick"><a href="tel:{FIRMA['telefon']}">Anrufen</a><a class="wa" href="{wa('Guten Tag, ich möchte einen Termin bei 1a Clean Car anfragen.')}" rel="noopener">WhatsApp</a></div>
<script>
document.querySelector('.menu-toggle').addEventListener('click',function(){{var n=document.getElementById('nav');var o=n.classList.toggle('open');this.setAttribute('aria-expanded',o)}});
</script>
</body>
</html>
"""
    out = ROOT / path / "index.html" if not path.endswith(".html") else ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return path

def hours_html():
    if not FIRMA["oeffnungszeiten"]:
        return f'<p>{TODO("Öffnungszeiten folgen")}<br>Termine nach Vereinbarung: <a href="tel:{FIRMA["telefon"]}">{FIRMA["telefon_anzeige"]}</a></p>'
    rows = "".join(f"<tr><td>{E(t)}</td><td>{E(z)}</td></tr>" for t, z in FIRMA["oeffnungszeiten"])
    return f'<table class="hours">{rows}</table>'

def price(key):
    p = (FIRMA["preise"] or {}).get(key)
    return E(p) if p else "Preis nach Fahrzeug &amp; Zustand"

def cta(depth, title="Was dürfen wir für Ihr Auto tun?", text="Rufen Sie uns an oder schreiben Sie uns per WhatsApp – wir besprechen persönlich, was Ihr Fahrzeug braucht."):
    return f"""<section class="cta"><div class="wrap">
<h2>{title}</h2><p class="lead" style="margin:0 auto">{text}</p>
<div class="actions"><a class="btn" href="{rel(depth, 'kontakt/')}">Termin anfragen</a><a class="btn ghost" href="tel:{FIRMA['telefon']}">{FIRMA['telefon_anzeige']}</a></div>
</div></section>"""

def vn_block(depth, items=VN):
    figs = ""
    for key, label in items:
        figs += f"""<figure><div class="pair">
<div>{img(depth, "vn-" + key + "-vorher", label + " vor der Aufbereitung")}<span class="tag">Vorher</span></div>
<div>{img(depth, "vn-" + key + "-nachher", label + " nach der Aufbereitung")}<span class="tag after">Nachher</span></div>
</div><figcaption>{label}</figcaption></figure>"""
    return f'<div class="vn">{figs}</div>'

def faq_block(faqs):
    html_ = "".join(f'<details class="faq"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in faqs)
    schema = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    return html_, schema

def packages(depth):
    pk = [("innen", "Innenreinigung", "Für einen Innenraum, in dem man gerne Platz nimmt.",
           ["Saugen von Sitzen und Fußraum", "Reinigung von Oberflächen", "Pflege von Cockpit und Einstieg"], False),
          ("komplett", "Komplettpflege", "Innen und außen – ein frischer Start für Ihr Auto.",
           ["Innenreinigung und Außenpflege", "Abgestimmt auf den Fahrzeugzustand", "Ideal vor Verkauf oder Leasingrückgabe", "Pflege nach individuellem Bedarf"], True),
          ("aussen", "Außenpflege", "Sauber bis ins Detail. Für einen gepflegten Auftritt.",
           ["Schonende Fahrzeugwäsche", "Reinigung von Felgen und Scheiben", "Pflege der äußeren Oberflächen"], False)]
    out = ""
    for key, t, d, items, feat in pk:
        out += f"""<div class="pkg{' featured' if feat else ''}"><p class="eyebrow">{'Innen &amp; außen' if feat else 'Paket'}</p><h3>{t}</h3><p class="small">{d}</p>
<div class="price">{price(key)}</div><ul class="check">{''.join(f'<li>{i}</li>' for i in items)}</ul>
<a class="btn{'' if feat else ' ghost'}" href="{rel(depth, 'kontakt/')}?leistung={t}">{t} anfragen</a></div>"""
    return f'<div class="grid g3">{out}</div>'

# ---------------------------------------------------------------- Seiten ----
def startseite():
    d = 0
    karten = "".join(f"""<a class="card" href="{rel(d, 'leistungen/' + s + '/')}" style="text-decoration:none;color:inherit">
{img(d, b, t + ' bei 1a Clean Car in Walldorf')}<div class="body"><span class="num">{i:02d}</span><h3>{t}</h3><p>{k}</p><span class="more">Mehr erfahren →</span></div></a>"""
                     for i, (s, t, k, b) in enumerate(LEISTUNGEN, 1))
    galerie = "".join(f'<figure>{img(d, n, a)}<figcaption>{E(a)}</figcaption></figure>' for n, a in GALERIE)
    reviews = "".join(f'<blockquote class="rev"><div class="stars" aria-label="5 von 5 Sternen">★★★★★</div><p>„{E(t)}“</p><cite>– {E(n)}, Google</cite></blockquote>' for t, n in REVIEWS)
    body = f"""
<section class="hero">
 {img(d, 'hero-nacht', 'Frisch aufbereiteter Mercedes vor der 1a Clean Car Halle in Walldorf bei Nacht', 'bg', 1200, 1600, eager=True)}
 <div class="wrap">
  <p class="eyebrow">Fahrzeugpflege mit Liebe zum Detail</p>
  <h1>Autoaufbereitung in Walldorf <span>1a Clean Car</span></h1>
  <p class="lead">Frischer Innenraum, gepflegter Lack, sauberer Motorraum: Wir bereiten Ihr Fahrzeug sorgfältig auf – vom Alltagsauto bis zum Sportwagen.</p>
  <div class="actions"><a class="btn" href="kontakt/">Termin anfragen</a><a class="btn ghost" href="tel:{FIRMA['telefon']}">Anrufen: {FIRMA['telefon_anzeige']}</a></div>
  <ul class="facts"><li>5-Sterne-Bewertungen auf Google</li><li>Kurzfristige Termine möglich</li><li>Persönliche Beratung</li></ul>
 </div>
</section>

<section id="leistungen"><div class="wrap">
 <p class="eyebrow">Unsere Leistungen</p>
 <h2>Autopflege, Aufbereitung &amp; mehr</h2>
 <p class="lead">Was Ihr Fahrzeug braucht, besprechen wir persönlich mit Ihnen. Hier finden Sie unsere wichtigsten Leistungen.</p>
 <div class="grid g3" style="margin-top:36px">{karten}</div>
 <p style="margin-top:28px"><a href="leistungen/">Alle Leistungen ansehen</a> – auch Reifenwechsel, Windschutzscheibe und Trockeneisreinigung.</p>
</div></section>

<section class="alt" id="pakete"><div class="wrap">
 <p class="eyebrow">Pflegepakete</p>
 <h2>Pflege, die den Unterschied macht</h2>
 <p class="lead">Vom täglichen Begleiter bis zum Lieblingsstück: Wählen Sie die Pflege, die zu Ihrem Fahrzeug passt.</p>
 <div style="margin-top:36px">{packages(d)}</div>
</div></section>

<section id="vorher-nachher"><div class="wrap">
 <p class="eyebrow">Vorher &amp; Nachher</p>
 <h2>Der Unterschied liegt im Detail</h2>
 <p class="lead">Spuren des Alltags zeigen sich überall: im Fußraum, im Kofferraum, an den Felgen und in schwer erreichbaren Ecken. So sehen echte Fahrzeuge vor und nach unserer Aufbereitung aus.</p>
 <div style="margin-top:36px">{vn_block(d)}</div>
</div></section>

<section class="alt" id="galerie"><div class="wrap">
 <p class="eyebrow">Einblicke</p>
 <h2>Besondere Fahrzeuge. Besondere Pflege.</h2>
 <p class="lead">Bei 1a Clean Car bekommt jedes Fahrzeug die Aufmerksamkeit, die es verdient. Mehr Einblicke gibt es auf <a href="{FIRMA['instagram']}" rel="noopener">Instagram</a>.</p>
 <div class="gallery" style="margin-top:36px" tabindex="0" aria-label="Fahrzeuggalerie, seitlich scrollbar">{galerie}</div>
</div></section>

<section id="bewertungen"><div class="wrap">
 <p class="eyebrow">Google-Bewertungen</p>
 <h2>Was Kunden über uns sagen</h2>
 <div class="rating"><span class="stars">★★★★★</span><span>Unsere Kunden bewerten uns auf Google mit 5 Sternen.</span><a href="{GOOGLE_REVIEWS_URL}" rel="noopener">Alle Bewertungen auf Google ansehen →</a></div>
 <div class="grid g3">{reviews}</div>
</div></section>

<section class="alt" id="team"><div class="wrap split">
 <div>
  <p class="eyebrow">Unser Team</p>
  <h2>Mit Herz fürs Auto. Mit Zeit für Sie.</h2>
  <p>Hinter jedem gepflegten Fahrzeug stehen Menschen, die mit Freude und Sorgfalt an die Arbeit gehen. Uns verbindet die Begeisterung für Autos und für die kleinen Details, die am Ende den Unterschied machen.</p>
  <p>Gute Arbeit beginnt mit Zuhören: Wir nehmen uns Zeit für Ihre Wünsche, besprechen gemeinsam, was Ihr Fahrzeug braucht, und behandeln es so, wie wir es uns für unser eigenes Auto wünschen.</p>
  <p class="gold" style="font-family:var(--serif);font-size:1.3rem">Persönlich. Sorgfältig. Mit Leidenschaft.</p>
 </div>
 {img(d, 'halle-licht', 'Die Halle von 1a Clean Car in Walldorf mit Wabenbeleuchtung', '', 1600, 1200)}
</div></section>

<section id="halle"><div class="wrap split">
 <div class="video"><video controls muted playsinline preload="none" poster="img/video-poster.webp" width="512" height="910"><source src="img/halle-video.mp4" type="video/mp4"></video></div>
 <div>
  <p class="eyebrow">Unsere Halle</p>
  <h2>Ein Blick hinter die Kulissen</h2>
  <p>Am neuen Standort im Kleinfeldweg 40 in Walldorf haben wir Platz für sorgfältige Pflege: helle Arbeitsplätze für Fahrzeugpflege und Aufbereitung – und für die Aufmerksamkeit, die jedes Detail verdient.</p>
  <ol class="steps" style="grid-template-columns:1fr;margin-top:28px">
   <li><h3>Bedarf besprechen</h3><p class="small">Was braucht Ihr Auto? Gemeinsam klären wir Pflegewunsch und Fahrzeugzustand.</p></li>
   <li><h3>Pflege abstimmen</h3><p class="small">Umfang, Aufwand und Termin werden vorab individuell vereinbart.</p></li>
   <li><h3>Sauber losfahren</h3><p class="small">Nach der Pflege werfen wir gemeinsam einen Blick auf das Ergebnis.</p></li>
  </ol>
 </div>
</div></section>
{cta(d)}
"""
    return page("", "Autoaufbereitung in Walldorf | 1a Clean Car – Fahrzeugpflege",
                "Autoaufbereitung & Fahrzeugpflege in Walldorf: Innenreinigung, Außenpflege, Ozonbehandlung, Motorraumwäsche, Lack & Dellen. Jetzt Termin anfragen: 0151 55870869.",
                body, d)

def leistungen_uebersicht():
    d = 1
    karten = "".join(f"""<a class="card" href="{rel(d, 'leistungen/' + s + '/')}" style="text-decoration:none;color:inherit">
{img(d, b, t)}<div class="body"><h3>{t}</h3><p>{k}</p><span class="more">Mehr erfahren →</span></div></a>""" for s, t, k, b in LEISTUNGEN)
    weitere = "".join(f'<div class="pkg"><h3>{t}</h3><p class="small">{k}</p><a class="more" href="{wa("Guten Tag, ich habe eine Frage zum Thema " + t + ".")}" rel="noopener">Per WhatsApp anfragen →</a></div>' for t, k in WEITERE)
    body = f"""
<section class="pagehead"><div class="wrap">
 <div class="crumbs"><a href="../">Startseite</a> / Leistungen</div>
 <p class="eyebrow">Leistungen</p>
 <h1>Unsere Leistungen in Walldorf</h1>
 <p class="lead">Von der Innenreinigung bis zum Unfallservice: alles rund ums Auto an einem Ort. Was Ihr Fahrzeug braucht, besprechen wir persönlich mit Ihnen.</p>
</div></section>
<section><div class="wrap"><div class="grid g3">{karten}</div></div></section>
<section class="alt"><div class="wrap"><h2>Weitere Leistungen</h2><div class="grid g4" style="margin-top:28px">{weitere}</div></div></section>
{cta(d)}"""
    return page("leistungen/", "Leistungen: Autoaufbereitung, Lack & Unfallservice | 1a Clean Car Walldorf",
                "Alle Leistungen von 1a Clean Car in Walldorf: Fahrzeugaufbereitung, Innenreinigung, Ozonbehandlung, Motorraumwäsche, Lack, Karosserie, Dellen, Unfallservice und Mietwagen.",
                body, d, crumbs=[("leistungen/", "Leistungen")], active="leistungen/")

def leistung(slug, h1, title, desc, intro, img_name, img_alt, sections, faqs, vn=None):
    d = 2
    name = next(t for s, t, _, _ in LEISTUNGEN if s == slug)
    faq_html, faq_schema = faq_block(faqs)
    service_schema = {"@context": "https://schema.org", "@type": "Service", "name": name,
                      "serviceType": name, "provider": {"@id": DOMAIN + "/#firma"},
                      "areaServed": {"@type": "City", "name": "Walldorf"},
                      "url": f"{DOMAIN}/leistungen/{slug}/"}
    others = "".join(f'<li><a href="{rel(d, "leistungen/" + s + "/")}">{t}</a></li>' for s, t, _, _ in LEISTUNGEN if s != slug)
    vn_html = f'<section class="alt"><div class="wrap"><p class="eyebrow">Vorher &amp; Nachher</p><h2>Echte Ergebnisse</h2><div style="margin-top:30px">{vn_block(d, vn)}</div></div></section>' if vn else ""
    body = f"""
<section class="pagehead"><div class="wrap">
 <div class="crumbs"><a href="../../">Startseite</a> / <a href="../">Leistungen</a> / {name}</div>
 <p class="eyebrow">Leistung</p>
 <h1>{h1}</h1>
 <p class="lead">{intro}</p>
 <div class="actions"><a class="btn" href="{rel(d, 'kontakt/')}?leistung={name}">{name} anfragen</a><a class="btn ghost" href="tel:{FIRMA['telefon']}">{FIRMA['telefon_anzeige']}</a></div>
</div></section>
<section><div class="wrap split">
 <div class="prose">{sections}</div>
 {img(d, img_name, img_alt)}
</div></section>
{vn_html}
<section><div class="wrap split" style="align-items:start">
 <div><h2>Häufige Fragen</h2>{faq_html}</div>
 <div class="contact-box"><h3>Weitere Leistungen</h3><ul class="check">{others}</ul><p class="small">Oder schauen Sie in die <a href="{rel(d, 'leistungen/')}">Leistungsübersicht</a>.</p></div>
</div></section>
{cta(d)}"""
    return page(f"leistungen/{slug}/", title, desc, body, d,
                crumbs=[("leistungen/", "Leistungen"), (f"leistungen/{slug}/", name)],
                extra_schema=[service_schema, faq_schema], active="leistungen/" if slug != "fahrzeugaufbereitung" else "leistungen/fahrzeugaufbereitung/")

def alle_leistungen():
    leistung("fahrzeugaufbereitung",
        "Fahrzeugaufbereitung in Walldorf",
        "Fahrzeugaufbereitung in Walldorf – innen & außen | 1a Clean Car",
        "Professionelle Fahrzeugaufbereitung in Walldorf: Innenreinigung, Außenpflege oder Komplettaufbereitung – ideal auch vor Verkauf oder Leasingrückgabe. Jetzt Termin anfragen.",
        "Innen und außen mit Liebe zum Detail: Wir bringen Ihr Auto wieder in einen Zustand, in dem Sie sich rundum wohlfühlen – ob als regelmäßige Pflege oder als gründliche Komplettaufbereitung.",
        "porsche-gt3-halle", "Weißer Porsche 911 GT3 nach der Aufbereitung in der Halle von 1a Clean Car",
        f"""<h2>Gründlich, sorgfältig, persönlich abgestimmt</h2>
<p>Jedes Fahrzeug ist anders. Deshalb schauen wir uns Ihr Auto zuerst gemeinsam mit Ihnen an und besprechen, was es braucht: eine frische Innenreinigung, eine gründliche Außenpflege oder die komplette Aufbereitung von innen und außen.</p>
<h3>Typische Anlässe</h3>
<ul class="check"><li>Regelmäßige Pflege für den Alltag</li><li>Vor dem Verkauf – für einen besseren ersten Eindruck</li><li>Vor der Leasingrückgabe</li><li>Nach dem Urlaub, mit Kindern oder Haustieren</li><li>Für besondere Fahrzeuge und Sportwagen</li></ul>
<h3>Unsere Pflegepakete</h3>
<p>Wählen Sie zwischen <strong>Innenreinigung</strong>, <strong>Außenpflege</strong> und <strong>Komplettpflege</strong>. Ergänzend bieten wir zum Beispiel eine <a href="../motorraumwaesche/">Motorraumwäsche</a> oder eine <a href="../ozonbehandlung/">Ozonbehandlung</a> gegen Gerüche an.</p>""",
        [("Wie lange dauert eine Fahrzeugaufbereitung?", "Das hängt vom Umfang und vom Zustand des Fahrzeugs ab. Den genauen Zeitrahmen sprechen wir bei der Terminvereinbarung mit Ihnen ab."),
         ("Was kostet eine Fahrzeugaufbereitung?", "Der Preis richtet sich nach Fahrzeuggröße, Zustand und gewünschtem Umfang. Rufen Sie uns an oder schicken Sie uns ein Foto per WhatsApp – dann sagen wir Ihnen vorab, womit Sie rechnen können."),
         ("Bekomme ich kurzfristig einen Termin?", "Oft ja. Viele unserer Kunden haben kurzfristig einen Termin bekommen. Am besten fragen Sie einfach telefonisch oder per WhatsApp an."),
         ("Lohnt sich eine Aufbereitung vor dem Autoverkauf?", "Ein gepflegtes Fahrzeug macht beim Verkauf einen deutlich besseren Eindruck. Viele Kunden lassen ihr Auto deshalb vor dem Verkauf oder der Leasingrückgabe komplett aufbereiten.")],
        vn=VN)
    leistung("innenreinigung",
        "Innenreinigung für Ihr Auto in Walldorf",
        "Auto-Innenreinigung in Walldorf | 1a Clean Car",
        "Gründliche Innenreinigung in Walldorf: Sitze, Fußraum, Kofferraum, Cockpit und Einstiege. Für einen Innenraum, in dem man gerne Platz nimmt. Jetzt Termin anfragen.",
        "Krümel im Fußraum, Flecken auf den Sitzen, Staub im Cockpit: Wir reinigen den Innenraum Ihres Fahrzeugs gründlich – für ein frisches Gefühl beim Einsteigen.",
        "urus-innenraum", "Innenraum eines Lamborghini Urus nach der Innenreinigung",
        """<h2>Ein Innenraum, in dem man gerne Platz nimmt</h2>
<p>Im Innenraum verbringen Sie die meiste Zeit mit Ihrem Auto. Bei der Innenreinigung kümmern wir uns um alle Bereiche, die im Alltag schnell verschmutzen.</p>
<h3>Das gehört dazu</h3>
<ul class="check"><li>Gründliches Saugen von Sitzen, Fußraum und Kofferraum</li><li>Reinigung der Oberflächen</li><li>Pflege von Cockpit, Mittelkonsole und Einstiegen</li></ul>
<p>Hartnäckige Gerüche, etwa von Rauch oder Tieren, behandeln wir auf Wunsch zusätzlich mit einer <a href="../ozonbehandlung/">Ozonbehandlung</a>.</p>""",
        [("Reinigt ihr auch Polster und Teppiche?", "Sprechen Sie uns an: Was für Ihre Sitze und Teppiche sinnvoll ist, besprechen wir je nach Material und Zustand persönlich mit Ihnen."),
         ("Kann ich Innenreinigung und Außenpflege kombinieren?", "Ja. Die Kombination aus beidem ist unsere Komplettpflege."),
         ("Wie lange brauche ich keinen Zugriff auf mein Auto?", "Den Zeitrahmen besprechen wir bei der Terminvereinbarung. Wenn Sie in der Zwischenzeit mobil bleiben müssen, fragen Sie nach unserem Mietwagen.")],
        vn=[("fussraum", "Fußraum"), ("kofferraum", "Kofferraum"), ("heckklappe", "Heckklappenfalz")])
    leistung("ozonbehandlung",
        "Ozonbehandlung gegen Gerüche im Auto",
        "Ozonbehandlung gegen Gerüche im Auto – Walldorf | 1a Clean Car",
        "Rauch-, Tier- oder Schimmelgeruch im Auto? Mit einer Ozonbehandlung neutralisieren wir unangenehme Gerüche im Fahrzeuginnenraum. 1a Clean Car in Walldorf.",
        "Manche Gerüche bleiben trotz Reinigung im Auto hängen – zum Beispiel von Zigarettenrauch, Haustieren oder Feuchtigkeit. Eine Ozonbehandlung setzt genau dort an.",
        "ozonbehandlung", "Ozongerät im leeren Innenraum eines Fahrzeugs während der Ozonbehandlung",
        """<h2>So funktioniert die Ozonbehandlung</h2>
<p>Bei der Ozonbehandlung erzeugt ein Ozongerät im geschlossenen, unbesetzten Fahrzeuginnenraum Ozon. Das Ozon gelangt auch in Polster, Teppiche und schwer erreichbare Stellen und kann dort geruchsverursachende Stoffe abbauen. Anschließend wird das Fahrzeug gründlich gelüftet.</p>
<h3>Geeignet bei</h3>
<ul class="check"><li>Zigaretten- und Rauchgeruch</li><li>Gerüchen von Haustieren</li><li>Muffigem Geruch durch Feuchtigkeit</li><li>Gerüchen nach verschütteten Lebensmitteln</li></ul>
<p>Am besten wirkt die Behandlung in Kombination mit einer gründlichen <a href="../innenreinigung/">Innenreinigung</a>, damit die Ursache des Geruchs mit entfernt wird.</p>""",
        [("Ist die Ozonbehandlung sicher?", "Während der Behandlung befindet sich niemand im Fahrzeug. Danach wird der Innenraum gründlich gelüftet, bevor Sie Ihr Auto zurückbekommen."),
         ("Verschwindet jeder Geruch?", "Viele Gerüche lassen sich deutlich reduzieren oder ganz beseitigen. Wie gut das gelingt, hängt von Ursache und Stärke des Geruchs ab – das besprechen wir vorab ehrlich mit Ihnen."),
         ("Sollte vorher gereinigt werden?", "Wir empfehlen die Kombination mit einer Innenreinigung, damit die Geruchsquelle entfernt wird.")])
    leistung("motorraumwaesche",
        "Motorraumwäsche in Walldorf",
        "Motorraumwäsche & Motorraumpflege in Walldorf | 1a Clean Car",
        "Schonende Motorraumwäsche in Walldorf: Wir reinigen und pflegen den Motorraum Ihres Fahrzeugs gründlich – zum Beispiel vor dem Verkauf. Jetzt Termin anfragen.",
        "Ein sauberer Motorraum macht einen guten Eindruck – besonders beim Autoverkauf oder bei der Inspektion. Wir reinigen ihn gründlich und mit der nötigen Vorsicht.",
        "motorraum-amg", "Sauberer Motorraum eines Mercedes-AMG nach der Motorraumwäsche",
        """<h2>Gründlich und mit Vorsicht</h2>
<p>Im Motorraum sammeln sich mit der Zeit Staub, Laub und Schmutz. Bei der Motorraumwäsche entfernen wir diese Ablagerungen sorgfältig und achten dabei auf empfindliche Bauteile und Elektronik.</p>
<h3>Wann sich eine Motorraumwäsche lohnt</h3>
<ul class="check"><li>Vor dem Verkauf Ihres Fahrzeugs</li><li>Als Teil einer Komplettaufbereitung</li><li>Wenn sich viel Laub und Schmutz angesammelt haben</li></ul>
<p>Ein Kunde schrieb nach der Komplettreinigung seines Audi Q2 vor dem Verkauf: „Vor allem stach die Motorreinigung heraus.“</p>""",
        [("Schadet Wasser dem Motor?", "Wir reinigen den Motorraum schonend und schützen empfindliche Bereiche. Bei Fragen zu Ihrem Fahrzeug beraten wir Sie gern vorab."),
         ("Kann ich die Motorraumwäsche mit einer Aufbereitung kombinieren?", "Ja, sie lässt sich gut mit der Komplettpflege kombinieren – zum Beispiel vor dem Autoverkauf.")],
        vn=[("motorraum", "Motorraum")])
    leistung("lackierung-karosserie",
        "Lackierarbeiten, Karosserie & Dellentechnik",
        "Lackierung, Karosserie & Dellentechnik in Walldorf | 1a Clean Car",
        "Lackierarbeiten, Karosserie-Instandsetzung und Dellentechnik in Walldorf: Kratzer, Parkdellen und Hagelschäden – persönlich beraten bei 1a Clean Car.",
        "Kratzer, Parkdellen oder ein Schaden an der Karosserie? Wir beraten Sie persönlich und kümmern uns um die passende Lösung für einen stimmigen Fahrzeugauftritt.",
        "dellentechnik", "Dellentechnik: Ausbeulen einer Delle ohne Lackierung",
        """<h2>Lackierarbeiten</h2>
<p>Für einen stimmigen Fahrzeugauftritt: Ob einzelne Kratzer oder ein größerer Bereich – wir schauen uns den Schaden an und besprechen mit Ihnen, was sinnvoll ist.</p>
<h2>Karosserie-Instandsetzung</h2>
<p>Aufmerksamkeit für die Form Ihres Fahrzeugs: Wir kümmern uns um Schäden an der Karosserie und beraten Sie zu den nächsten Schritten.</p>
<h2>Dellentechnik – ohne Lackieren</h2>
<p>Geeignete Parkdellen und Hagelschäden entfernen wir mit Dellentechnik ohne Lackierarbeiten. Der Originallack bleibt dabei erhalten. Ob sich eine Delle dafür eignet, sehen wir am besten direkt am Fahrzeug – oder Sie schicken uns vorab ein Foto per WhatsApp.</p>""",
        [("Kann jede Delle ohne Lackieren entfernt werden?", "Nicht jede. Ob Dellentechnik möglich ist, hängt von Größe, Lage und Lackzustand ab. Schicken Sie uns gern ein Foto – dann geben wir Ihnen eine erste Einschätzung."),
         ("Helft ihr auch bei kleinen Kratzern?", "Ja, sprechen Sie uns an. Ein Kunde schrieb: „Wir hatten kurzfristig Hilfe wegen ein paar Kratzern benötigt. Hier wurde sofort geholfen.“")])
    leistung("unfallservice",
        "Unfallservice & Mietwagen in Walldorf",
        "Unfallservice & Mietwagen in Walldorf | 1a Clean Car",
        "Unfallschaden? 1a Clean Car in Walldorf koordiniert Begutachtung, Versicherung und Reparatur – und mit unserem Mietwagen bleiben Sie mobil.",
        "Nach einem Unfall gibt es viel zu klären. Wir sind Ihr Ansprechpartner im Schadenfall und kümmern uns um die nächsten Schritte – damit Sie sich nicht um alles allein kümmern müssen.",
        "unfallservice", "Mitarbeiter begutachtet einen Unfallschaden am Fahrzeug",
        f"""<h2>Ihr Ansprechpartner im Schadenfall</h2>
<p>Wir koordinieren die Begutachtung, die Abstimmung mit der Versicherung und die erforderliche Reparatur. So haben Sie einen festen Ansprechpartner statt vieler einzelner Termine.</p>
<ul class="check"><li>Koordination der Begutachtung</li><li>Abstimmung mit der Versicherung</li><li>Organisation der Reparatur</li></ul>
<h2>Mietwagen – mobil bleiben</h2>
<p>Für private Fahrten, Geschäftstermine oder während Ihr Auto bei uns ist: Mit unserem Mietwagen bleiben Sie mobil. Fragen Sie einfach den gewünschten Zeitraum an.</p>
<p><a class="btn ghost" href="{wa('Guten Tag, ich interessiere mich für einen Mietwagen.')}" rel="noopener">Mietwagen per WhatsApp anfragen</a></p>""",
        [("Was soll ich nach einem Unfall als Erstes tun?", "Sichern Sie die Unfallstelle, kümmern Sie sich um Verletzte und dokumentieren Sie den Schaden mit Fotos. Danach können Sie uns anrufen – wir besprechen mit Ihnen die nächsten Schritte."),
         ("Kann ich während der Reparatur einen Mietwagen bekommen?", "Ja, fragen Sie einfach den gewünschten Zeitraum bei uns an.")])

def kontakt():
    d = 1
    optionen = ["Innenreinigung", "Außenpflege", "Komplettpflege", "Fahrzeugaufbereitung", "Ozonbehandlung", "Motorraumwäsche",
                "Lackierarbeiten", "Karosserie-Instandsetzung", "Dellentechnik", "Unfallservice", "Mietwagen", "Reifenwechsel",
                "Windschutzscheibe", "Trockeneisreinigung", "Individuelle Beratung"]
    opts = "".join(f"<option>{o}</option>" for o in optionen)
    body = f"""
<section class="pagehead"><div class="wrap">
 <div class="crumbs"><a href="../">Startseite</a> / Kontakt</div>
 <p class="eyebrow">Kontakt &amp; Termin</p>
 <h1>Termin bei 1a Clean Car anfragen</h1>
 <p class="lead">Rufen Sie uns an, schreiben Sie uns per WhatsApp oder E-Mail – oder stellen Sie Ihre Anfrage hier zusammen.</p>
</div></section>
<section><div class="wrap split" style="align-items:start">
 <form id="anfrage" onsubmit="return false">
  <h2>Ihre Anfrage</h2>
  <label for="f-leistung">Gewünschte Leistung</label><select id="f-leistung">{opts}</select>
  <label for="f-auto">Ihr Fahrzeug (Marke, Modell)</label><input id="f-auto" placeholder="z. B. BMW X5">
  <label for="f-name">Ihr Name</label><input id="f-name" autocomplete="name">
  <label for="f-wunsch">Wunschtermin &amp; besondere Wünsche (optional)</label><textarea id="f-wunsch"></textarea>
  <div class="actions">
   <button class="btn" type="button" data-send="wa">Per WhatsApp senden</button>
   <button class="btn ghost" type="button" data-send="mail">Per E-Mail senden</button>
  </div>
  <p class="small" style="margin-top:14px">Ihre Angaben werden nicht auf dieser Website gespeichert. Mit Klick öffnet sich WhatsApp bzw. Ihr E-Mail-Programm mit dem vorbereiteten Text. Hinweise zu WhatsApp finden Sie in der <a href="../datenschutz/">Datenschutzerklärung</a>.</p>
 </form>
 <div>
  <div class="contact-box">
   <h3>So erreichen Sie uns</h3>
   <dl>
    <dt>Telefon</dt><dd><a href="tel:{FIRMA['telefon']}">{FIRMA['telefon_anzeige']}</a></dd>
    <dt>WhatsApp</dt><dd><a href="{wa()}" rel="noopener">Nachricht schreiben</a></dd>
    <dt>E-Mail</dt><dd><a href="mailto:{FIRMA['email']}">{FIRMA['email']}</a></dd>
    <dt>Adresse</dt><dd>{FIRMA['strasse']}<br>{FIRMA['plz']} {FIRMA['ort']}<br><a href="{FIRMA['maps']}" rel="noopener">Route in Google Maps öffnen</a></dd>
   </dl>
  </div>
  <div class="contact-box" style="margin-top:22px"><h3>Öffnungszeiten</h3>{hours_html()}</div>
  <div style="margin-top:22px">{img(d, 'standort-amg-gt', 'Mercedes-AMG GT vor dem Standort von 1a Clean Car in Walldorf')}</div>
 </div>
</div></section>
<script>
(function(){{
 var p=new URLSearchParams(location.search).get('leistung'); var s=document.getElementById('f-leistung');
 if(p){{for(var i=0;i<s.options.length;i++) if(s.options[i].text===p) s.selectedIndex=i;}}
 function text(){{var g=function(id){{return document.getElementById(id).value.trim()}};
  var t='Guten Tag, ich möchte eine Anfrage stellen.\\n\\nLeistung: '+g('f-leistung');
  if(g('f-auto')) t+='\\nFahrzeug: '+g('f-auto'); if(g('f-wunsch')) t+='\\nWünsche: '+g('f-wunsch');
  if(g('f-name')) t+='\\n\\nViele Grüße\\n'+g('f-name'); return t;}}
 document.querySelectorAll('[data-send]').forEach(function(b){{b.addEventListener('click',function(){{
  var t=text();
  if(b.dataset.send==='wa') window.open('https://wa.me/{FIRMA['whatsapp']}?text='+encodeURIComponent(t),'_blank','noopener');
  else location.href='mailto:{FIRMA['email']}?subject='+encodeURIComponent('Anfrage: '+document.getElementById('f-leistung').value)+'&body='+encodeURIComponent(t);
 }})}});
}})();
</script>"""
    return page("kontakt/", "Kontakt & Termin | 1a Clean Car Walldorf",
                f"Termin bei 1a Clean Car in Walldorf anfragen: Telefon {FIRMA['telefon_anzeige']}, WhatsApp oder E-Mail. {FIRMA['strasse']}, {FIRMA['plz']} {FIRMA['ort']}.",
                body, d, crumbs=[("kontakt/", "Kontakt")], active="kontakt/")

def impressum():
    d = 1
    f = FIRMA
    v = lambda k, label: E(f[k]) if f[k] else TODO(label)
    body = f"""
<section class="pagehead"><div class="wrap"><div class="crumbs"><a href="../">Startseite</a> / Impressum</div><h1>Impressum</h1></div></section>
<section><div class="wrap prose">
<h2>Angaben gemäß § 5 DDG</h2>
<p>{v('inhaber', 'Vollständiger Name des Inhabers / Firmenname mit Rechtsform')}<br>
1a Clean Car{(' – ' + E(f['rechtsform'])) if f['rechtsform'] else ''}<br>
{f['strasse']}<br>{f['plz']} {f['ort']}</p>
{('<p>Vertreten durch: ' + E(f['vertreten_durch']) + '</p>') if f['vertreten_durch'] else ''}
<h2>Kontakt</h2>
<p>Telefon: <a href="tel:{f['telefon']}">{f['telefon_anzeige']}</a><br>E-Mail: <a href="mailto:{f['email']}">{f['email']}</a></p>
<h2>Registereintrag</h2>
<p>{v('register', 'Registergericht und Registernummer – entfällt bei Einzelunternehmen ohne Handelsregistereintrag')}</p>
<h2>Umsatzsteuer-ID</h2>
<p>Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz: {v('ust_id', 'USt-IdNr. – falls vorhanden')}</p>
<h2>Verbraucherstreitbeilegung</h2>
<p>Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
<h2>Bildnachweis</h2>
<p>Fahrzeug- und Hallenfotos: 1a Clean Car.</p>
</div></section>"""
    return page("impressum/", "Impressum | 1a Clean Car Walldorf", "Impressum von 1a Clean Car, Autoaufbereitung in Walldorf.", body, d, crumbs=[("impressum/", "Impressum")], noindex=True)

def datenschutz():
    d = 1
    f = FIRMA
    verantw = E(f['inhaber']) if f['inhaber'] else TODO('Name des Inhabers')
    body = f"""
<section class="pagehead"><div class="wrap"><div class="crumbs"><a href="../">Startseite</a> / Datenschutz</div><h1>Datenschutzerklärung</h1>
<p class="lead">Stand: November 2026</p></div></section>
<section><div class="wrap prose">
<h2>1. Verantwortlicher</h2>
<p>{verantw}, 1a Clean Car, {f['strasse']}, {f['plz']} {f['ort']}<br>Telefon: {f['telefon_anzeige']} · E-Mail: <a href="mailto:{f['email']}">{f['email']}</a></p>

<h2>2. Grundsätzliches</h2>
<p>Diese Website setzt keine Cookies, verwendet keine Analyse- oder Tracking-Werkzeuge und bindet keine externen Schriftarten, Karten oder Social-Media-Plugins ein. Personenbezogene Daten werden nur verarbeitet, soweit dies für die Bereitstellung der Website oder die Bearbeitung Ihrer Anfrage erforderlich ist.</p>

<h2>3. Hosting und Server-Logfiles</h2>
<p>Diese Website wird bei GitHub Pages gehostet (GitHub Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, USA). Beim Aufruf der Website verarbeitet der Hoster technisch notwendige Daten wie Ihre IP-Adresse, Datum und Uhrzeit des Abrufs, die aufgerufene Seite sowie Browser- und Systeminformationen, um die Website auszuliefern und ihre Sicherheit zu gewährleisten. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an einer sicheren und stabilen Bereitstellung). Eine Übermittlung in die USA kann dabei nicht ausgeschlossen werden; GitHub stützt sich hierfür auf das EU-US Data Privacy Framework bzw. Standardvertragsklauseln. Weitere Informationen: <a href="https://docs.github.com/de/site-policy/privacy-policies/github-general-privacy-statement" rel="noopener">Datenschutzerklärung von GitHub</a>.</p>

<h2>4. Kontaktaufnahme per Telefon und E-Mail</h2>
<p>Wenn Sie uns anrufen oder eine E-Mail schreiben, verarbeiten wir Ihre Angaben (z. B. Name, Telefonnummer, E-Mail-Adresse, Fahrzeug und Anliegen), um Ihre Anfrage zu beantworten und gegebenenfalls einen Auftrag durchzuführen. Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO (Vertragsanbahnung bzw. -erfüllung) sowie Art. 6 Abs. 1 lit. f DSGVO. Die Daten werden gelöscht, sobald sie nicht mehr erforderlich sind und keine gesetzlichen Aufbewahrungspflichten entgegenstehen.</p>

<h2>5. Kontaktaufnahme über WhatsApp</h2>
<p>Auf dieser Website finden Sie Links, über die Sie uns per WhatsApp kontaktieren können. Das Anfrageformular speichert keine Daten auf dieser Website, sondern bereitet lediglich einen Nachrichtentext vor, den Sie in WhatsApp selbst absenden. Anbieter von WhatsApp ist die WhatsApp Ireland Limited, 4 Grand Canal Square, Grand Canal Harbour, Dublin 2, Irland. Wenn Sie uns über WhatsApp schreiben, verarbeitet WhatsApp Ihre Telefonnummer, Ihre Nachricht und Metadaten; dabei kann eine Übermittlung in Drittländer wie die USA stattfinden. Die Nutzung ist freiwillig – Sie können uns jederzeit auch telefonisch oder per E-Mail erreichen. Rechtsgrundlage ist Art. 6 Abs. 1 lit. b und lit. f DSGVO. Weitere Informationen: <a href="https://www.whatsapp.com/legal/privacy-policy-eea" rel="noopener">Datenschutzrichtlinie von WhatsApp</a>.</p>

<h2>6. Links zu Google Maps und Instagram</h2>
<p>Wir verlinken auf unseren Standort bei Google Maps, auf unsere Bewertungen bei Google sowie auf unser Instagram-Profil. Es handelt sich um einfache Links, nicht um eingebettete Inhalte. Erst wenn Sie einen solchen Link anklicken, werden Sie auf die Seite des jeweiligen Anbieters weitergeleitet, dessen Datenschutzbestimmungen dann gelten (Google Ireland Limited bzw. Meta Platforms Ireland Limited).</p>

<h2>7. Kundenbewertungen</h2>
<p>Auf der Startseite zeigen wir gekürzte Auszüge aus öffentlich auf Google abgegebenen Bewertungen, jeweils nur mit Vornamen bzw. Initialen. Wenn Sie nicht möchten, dass Ihre Bewertung hier erscheint, genügt eine kurze Nachricht an uns.</p>

<h2>8. Ihre Rechte</h2>
<p>Sie haben das Recht auf Auskunft (Art. 15 DSGVO), Berichtigung (Art. 16), Löschung (Art. 17), Einschränkung der Verarbeitung (Art. 18), Datenübertragbarkeit (Art. 20) sowie Widerspruch gegen Verarbeitungen auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO (Art. 21). Außerdem können Sie sich bei einer Datenschutz-Aufsichtsbehörde beschweren, zum Beispiel beim Landesbeauftragten für den Datenschutz und die Informationsfreiheit Baden-Württemberg.</p>
</div></section>"""
    return page("datenschutz/", "Datenschutzerklärung | 1a Clean Car Walldorf", "Datenschutzerklärung von 1a Clean Car in Walldorf.", body, d, crumbs=[("datenschutz/", "Datenschutz")], noindex=True)

def seite_404():
    body = f"""<section class="pagehead"><div class="wrap"><h1>Seite nicht gefunden</h1>
<p class="lead">Diese Seite gibt es leider nicht (mehr).</p>
<div class="actions"><a class="btn" href="{DOMAIN}/">Zur Startseite</a><a class="btn ghost" href="{DOMAIN}/kontakt/">Kontakt</a></div></div></section>"""
    page("404.html", "Seite nicht gefunden | 1a Clean Car", "Diese Seite wurde nicht gefunden.", body, 0, noindex=True)

def extras(paths):
    urls = "".join(f"<url><loc>{DOMAIN}/{p}</loc></url>" for p in paths)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")
    (ROOT / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#0b0d0c"/><text x="8" y="44" font-family="Georgia,serif" font-weight="bold" font-size="34" fill="#e6cf72">1a</text></svg>\n', encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")

if __name__ == "__main__":
    startseite(); leistungen_uebersicht(); alle_leistungen(); kontakt(); impressum(); datenschutz(); seite_404()
    indexable = ["", "leistungen/", *[f"leistungen/{s}/" for s, *_ in LEISTUNGEN], "kontakt/"]
    extras(indexable)
    print("Fertig:", len(indexable) + 3, "Seiten")
