"""Graficos estilo Alwan (curva de ganancia de punto / TVI) a partir del
resultado ya calculado por cgats_offset.analyze_cgats_offset().

Paleta C/M/Y validada con el validador de accesibilidad del design system
(node scripts/validate_palette.js): C/M/Y pasan los 6 checks (contraste,
banda de luminancia, piso de croma, separacion CVD). K es acromatico por
definicion (es tinta negra) y por eso no pasa los checks de "hue categorico"
-- se compensa con una forma de marcador propia (diamante) y etiqueta directa
al final de la linea, en vez de depender solo del color para identificarlo.
"""

import io

import matplotlib

matplotlib.use("Agg")  # sin display, solo generar PNG en memoria
import matplotlib.pyplot as plt

CHANNEL_STYLE = {
    "C": {"color": "#0090C8", "marker": "o"},
    "M": {"color": "#EC008C", "marker": "s"},
    "Y": {"color": "#B8860B", "marker": "^"},
    "K": {"color": "#222222", "marker": "D"},
}


def render_tvi_chart(analysis: dict) -> bytes | None:
    """Curva de ganancia de punto (TVI) medida por canal, con la diagonal de
    referencia "sin ganancia" -- el grafico clasico de reporte de prensa."""
    tvi_measured = analysis.get("tvi_measured") or {}
    if not any(tvi_measured.get(ch) for ch in CHANNEL_STYLE):
        return None

    fig, ax = plt.subplots(figsize=(6.4, 4.4), dpi=150)
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")

    for ch, style in CHANNEL_STYLE.items():
        points = tvi_measured.get(ch) or {}
        if not points:
            continue
        xs = sorted(points.keys())
        ys = [points[x] for x in xs]
        ax.plot(
            xs, ys,
            color=style["color"], marker=style["marker"], markersize=7,
            linewidth=2, label=ch, zorder=3,
        )
        # Etiqueta directa al final de la linea -- la identidad no depende
        # solo del color (importante para el canal K, que es acromatico).
        ax.annotate(
            ch, (xs[-1], ys[-1]), textcoords="offset points", xytext=(6, 0),
            fontsize=10, fontweight="bold", color=style["color"], va="center",
        )

    # Diagonal de referencia "sin ganancia" -- recesiva, no compite con los datos.
    ax.plot([0, 100], [0, 100], linestyle="--", linewidth=1, color="#b0b0b0",
             label="Sin ganancia", zorder=1)

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Valor nominal (%)", color="#444444")
    ax.set_ylabel("Valor medido (%)", color="#444444")
    standard_name = analysis.get("standard_name", "")
    ax.set_title(f"Ganancia de punto (TVI) vs {standard_name}", color="#1a1a1a", fontsize=12)

    ax.grid(True, linestyle=":", linewidth=0.6, color="#cccccc", alpha=0.6, zorder=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#cccccc")

    ax.legend(loc="upper left", fontsize=8, frameon=False)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


# Fondo tenue por canal para la grilla del informe (mismo espiritu que los
# paneles de color por tinta de un reporte de prensa clasico).
_PANEL_BG = {"C": "#eaf6fc", "M": "#fdeef6", "Y": "#fdf8e3", "K": "#f2f2f2"}
_PANEL_ORDER = ["K", "C", "M", "Y"]  # mismo orden que usa el reporte de referencia


def render_tvi_grid(analysis: dict) -> bytes | None:
    """4 paneles (uno por canal) con la curva medida + banda de tolerancia
    alrededor del target, para el informe de calibracion en PDF."""
    tvi_measured = analysis.get("tvi_measured") or {}
    tvi_compliance = analysis.get("tvi_compliance") or {}
    if not any(tvi_measured.get(ch) for ch in CHANNEL_STYLE):
        return None

    # Aspecto mas achatado que un grid cuadrado -- para que, con el resto del
    # informe, la pagina completa entre en una sola hoja A4 (como el reporte
    # de referencia, que es todo de un vistazo, sin dar vuelta la pagina).
    fig, axes = plt.subplots(2, 2, figsize=(7.6, 4.5), dpi=150)
    fig.patch.set_facecolor("#ffffff")

    for ax, ch in zip(axes.flat, _PANEL_ORDER):
        style = CHANNEL_STYLE[ch]
        ax.set_facecolor(_PANEL_BG[ch])

        # Banda de tolerancia alrededor de cada target definido por el standard
        # (solo en los puntos donde el standard realmente define un target --
        # nunca interpolamos targets inventados entre esos puntos).
        for pct, comp in sorted((tvi_compliance.get(ch) or {}).items()):
            target = comp.get("target")
            tol = comp.get("tolerance", 0)
            if target is None:
                continue
            ax.plot([pct, pct], [target - tol, target + tol],
                     color="#999999", linewidth=4, alpha=0.5, zorder=1)
            ax.plot(pct, target, marker="_", color="#555555", markersize=10, zorder=2)

        points = tvi_measured.get(ch) or {}
        if points:
            xs = sorted(points.keys())
            ys = [points[x] for x in xs]
            ax.plot(xs, ys, color=style["color"], marker=style["marker"],
                     markersize=6, linewidth=2, zorder=3)

        ax.plot([0, 100], [0, 100], linestyle="--", linewidth=0.8, color="#bbbbbb", zorder=0)

        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_title(f"{ch} — TVI", fontsize=10, fontweight="bold", color="#222222")
        ax.tick_params(labelsize=7, colors="#555555")
        ax.grid(True, linestyle=":", linewidth=0.5, color="#ffffff", alpha=0.8)
        for spine in ax.spines.values():
            spine.set_color("#dddddd")

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
