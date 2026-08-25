# =========================================================
# SONRICKS STORE — sonricksstore.py
# Servidor Flask: renderiza home.html, que extiende layout.html
# e incluye components/navbar.html y components/footer.html
# =========================================================

from flask import Flask, render_template, url_for

app = Flask(__name__)

# Datos del catálogo (simulados, en memoria).
# En un proyecto real vendrían de una base de datos.
PRODUCTOS = [
    {
        "nombre": "Sonricks Pro Match",
        "tag": "Pro Match",
        "descripcion": "Balón oficial de competencia, vuelo estable y costura termosellada.",
        "precio": "$899 MXN",
        "imagen": "https://images.unsplash.com/photo-1614632537197-38a17061c2bd?auto=format&fit=crop&w=500&q=80",
    },
    {
        "nombre": "Sonricks Street",
        "tag": "Street",
        "descripcion": "Resistente al pavimento, ideal para cascarita entre amigos.",
        "precio": "$599 MXN",
        "imagen": "https://images.unsplash.com/photo-1552667466-07770ae110d0?auto=format&fit=crop&w=500&q=80",
    },
    {
        "nombre": "Sonricks Training",
        "tag": "Training",
        "descripcion": "Pensado para sesiones intensas: ligero, durable y preciso.",
        "precio": "$499 MXN",
        "imagen": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?auto=format&fit=crop&w=500&q=80",
    },
    {
        "nombre": "Sonricks Kids",
        "tag": "Kids",
        "descripcion": "Talla reducida y peso ajustado para los futuros cracks.",
        "precio": "$399 MXN",
        "imagen": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=500&q=80",
    },
]

ESLOGAN = "Golpea con estilo."


@app.route("/")
def home():
    """Ruta principal: renderiza home.html (usa layout.html + components/)."""
    return render_template(
        "home.html",
        productos=PRODUCTOS,
        eslogan=ESLOGAN,
    )


if __name__ == "__main__":
    # debug=True solo para desarrollo local
    app.run(debug=True)
