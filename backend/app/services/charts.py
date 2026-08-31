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


# ── Version interactiva (SVG + JS embebido, sin dependencias externas) ─────
# Mismo dato, mismo criterio visual que render_tvi_grid (paneles, colores,
# bandas de tolerancia) pero como SVG real -- no una imagen -- para que el
# informe HTML tenga tooltip al pasar el mouse por cada punto. Pensado para
# abrirse localmente (file://), por eso el <script> va inline, sin CDNs.

_SVG_PAD_L, _SVG_PAD_R, _SVG_PAD_T, _SVG_PAD_B = 30, 10, 22, 24
_SVG_PLOT_W, _SVG_PLOT_H = 180, 160
_SVG_VB_W = _SVG_PAD_L + _SVG_PLOT_W + _SVG_PAD_R
_SVG_VB_H = _SVG_PAD_T + _SVG_PLOT_H + _SVG_PAD_B


def _svg_x(pct: float) -> float:
    return _SVG_PAD_L + (pct / 100.0) * _SVG_PLOT_W


def _svg_y(val: float) -> float:
    return _SVG_PAD_T + (1 - val / 100.0) * _SVG_PLOT_H


def _svg_panel(ch: str, tvi_measured: dict, tvi_compliance: dict) -> str:
    style = CHANNEL_STYLE[ch]
    bg = _PANEL_BG[ch]
    parts = [
        f'<svg class="tvi-panel" viewBox="0 0 {_SVG_VB_W} {_SVG_VB_H}" '
        f'role="img" aria-label="Ganancia de punto canal {ch}">',
        f'<rect x="{_SVG_PAD_L}" y="{_SVG_PAD_T}" width="{_SVG_PLOT_W}" '
        f'height="{_SVG_PLOT_H}" fill="{bg}" />',
    ]

    # Ejes minimos (0/50/100) -- recesivos, solo de referencia.
    for pct in (0, 50, 100):
        x, y0 = _svg_x(pct), _svg_y(0)
        y, x0 = _svg_y(pct), _svg_x(0)
        parts.append(
            f'<text x="{x:.1f}" y="{y0 + 14:.1f}" font-size="6.5" fill="#888888" '
            f'text-anchor="middle">{pct}</text>'
        )
        parts.append(
            f'<text x="{x0 - 4:.1f}" y="{y + 2.5:.1f}" font-size="6.5" fill="#888888" '
            f'text-anchor="end">{pct}</text>'
        )

    # Diagonal de referencia "sin ganancia".
    parts.append(
        f'<line x1="{_svg_x(0):.1f}" y1="{_svg_y(0):.1f}" x2="{_svg_x(100):.1f}" '
        f'y2="{_svg_y(100):.1f}" stroke="#bbbbbb" stroke-width="1" '
        f'stroke-dasharray="3,2" />'
    )

    # Bandas de tolerancia -- solo en los puntos donde el standard define target
    # (nunca se interpola un target inventado entre esos puntos).
    for pct, comp in sorted((tvi_compliance.get(ch) or {}).items()):
        target = comp.get("target")
        tol = comp.get("tolerance", 0)
        if target is None:
            continue
        x = _svg_x(pct)
        y_top, y_bot = _svg_y(target + tol), _svg_y(target - tol)
        parts.append(
            f'<line x1="{x:.1f}" y1="{y_top:.1f}" x2="{x:.1f}" y2="{y_bot:.1f}" '
            f'stroke="#999999" stroke-width="3" stroke-linecap="round" opacity="0.55" />'
        )
        parts.append(
            f'<line x1="{x - 4:.1f}" y1="{_svg_y(target):.1f}" x2="{x + 4:.1f}" '
            f'y2="{_svg_y(target):.1f}" stroke="#555555" stroke-width="1.4" />'
        )

    points = tvi_measured.get(ch) or {}
    xs = sorted(points.keys())
    if xs:
        path_d = " ".join(
            f"{'M' if i == 0 else 'L'}{_svg_x(x):.1f},{_svg_y(points[x]):.1f}"
            for i, x in enumerate(xs)
        )
        parts.append(f'<path d="{path_d}" fill="none" stroke="{style["color"]}" stroke-width="2" />')

    for pct in xs:
        measured = points[pct]
        comp = (tvi_compliance.get(ch) or {}).get(pct, {})
        target = comp.get("target")
        tol = comp.get("tolerance")
        passed = comp.get("passed", True)
        x, y = _svg_x(pct), _svg_y(measured)
        tip = (
            f"{ch} — {pct}%: medido {measured:.1f}%"
            + (f" (target {target:.1f}% ± {tol:.1f})" if target is not None else "")
            + (" — FALLA" if not passed else " — OK" if target is not None else "")
        )
        # Marca visible (>=8px de diametro) con anillo de superficie, mas un
        # area de hit invisible de 24px para que el hover no sea puntería fina.
        parts.append(
            f'<g class="tvi-point" tabindex="0" data-tip="{tip}">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="transparent" />'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{style["color"]}" '
            f'stroke="#ffffff" stroke-width="1.5" />'
            + (
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="none" '
                f'stroke="{FAIL_SVG_COLOR}" stroke-width="1.3" />'
                if not passed else ""
            )
            + "</g>"
        )
        # Label directo -- solo en los puntos fuera de tolerancia (selectivo,
        # nunca un numero en cada punto), asi lo importante no depende del hover.
        if not passed and target is not None:
            deviation = comp.get("deviation", measured - target)
            parts.append(
                f'<text x="{x:.1f}" y="{y - 9:.1f}" font-size="6.5" font-weight="700" '
                f'fill="{FAIL_SVG_COLOR}" text-anchor="middle">{deviation:+.1f}</text>'
            )

    parts.append(
        f'<text x="{_SVG_PAD_L:.1f}" y="12" font-size="9" font-weight="700" '
        f'fill="#222222">{ch} — TVI</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


FAIL_SVG_COLOR = "#c0392b"


def render_tvi_grid_svg(analysis: dict) -> str | None:
    """Grilla interactiva (SVG + tooltip JS, sin librerias externas) equivalente
    a render_tvi_grid pero para el informe HTML -- cada punto medido responde
    al hover/foco con el detalle exacto (nominal, medido, target, tolerancia)."""
    tvi_measured = analysis.get("tvi_measured") or {}
    tvi_compliance = analysis.get("tvi_compliance") or {}
    if not any(tvi_measured.get(ch) for ch in CHANNEL_STYLE):
        return None

    panels = "".join(_svg_panel(ch, tvi_measured, tvi_compliance) for ch in _PANEL_ORDER)

    return f"""
    <div class="tvi-legend">
      <span><i class="tvi-swatch" style="background:#0090C8"></i>Curva medida</span>
      <span><i class="tvi-swatch tvi-swatch--tick"></i>Target ISO ± tolerancia</span>
      <span><i class="tvi-swatch tvi-swatch--dashed"></i>Sin ganancia (referencia)</span>
      <span><i class="tvi-swatch" style="background:{FAIL_SVG_COLOR}; border-radius:50%;"></i>Fuera de tolerancia</span>
    </div>
    <div class="tvi-grid">{panels}</div>
    <div id="tvi-tooltip" class="tvi-tooltip" hidden></div>
    <script>
    (function () {{
      var tooltip = document.getElementById('tvi-tooltip');
      var grid = document.currentScript.previousElementSibling.previousElementSibling;
      function showTip(el, evt) {{
        var tip = el.getAttribute('data-tip');
        if (!tip) return;
        tooltip.textContent = tip;
        tooltip.hidden = false;
        var x = (evt && evt.clientX != null) ? evt.clientX : el.getBoundingClientRect().left;
        var y = (evt && evt.clientY != null) ? evt.clientY : el.getBoundingClientRect().top;
        tooltip.style.left = (x + 14) + 'px';
        tooltip.style.top = (y + 14) + 'px';
      }}
      function hideTip() {{ tooltip.hidden = true; }}
      grid.addEventListener('pointermove', function (evt) {{
        var pt = evt.target.closest('.tvi-point');
        if (pt) showTip(pt, evt); else hideTip();
      }});
      grid.addEventListener('pointerleave', hideTip);
      grid.addEventListener('focusin', function (evt) {{
        var pt = evt.target.closest('.tvi-point');
        if (pt) showTip(pt, null);
      }});
      grid.addEventListener('focusout', hideTip);
    }})();
    </script>
    """
