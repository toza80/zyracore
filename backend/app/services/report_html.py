"""Informe de calibracion (autoria en HTML/CSS), inspirado en el formato de
reporte de laboratorio de color que ya usa el cliente -- con identidad de
ZyraWorks, no de terceros. Se ofrece en dos salidas a partir del MISMO
resultado ya calculado:

- render_color_report_pdf: PDF (WeasyPrint) para archivar / imprimir / mandar
  a un cliente. El grafico de TVI va como imagen (PNG) porque un PDF no
  ejecuta JS.
- render_color_report_html: .html standalone (sin dependencias externas,
  pensado para abrirse localmente con doble click / file://) con el grafico
  de TVI interactivo (SVG + tooltip al pasar el mouse por cada punto).

IMPORTANTE: este es un SERVICIO COMPARTIDO, no un agente. No tiene criterio
propio ni conversa -- toma un resultado YA CALCULADO (por cgats_offset.py) y
le da formato. Cualquier agente futuro (Prepress, Finance, etc.) puede
llamarlo para sus propios informes sin duplicar diseno.
"""

import base64
from datetime import datetime

from weasyprint import HTML

from app.services.cgats_offset import ISO_STANDARDS
from app.services.charts import render_tvi_grid, render_tvi_grid_svg

ACCENT = "#5b3df5"
PASS_COLOR = "#1f9d55"
FAIL_COLOR = "#d64545"

CHANNEL_LABELS = {"C": "Cyan", "M": "Magenta", "Y": "Yellow", "K": "Black"}


def _b64(png_bytes: bytes) -> str:
    return base64.b64encode(png_bytes).decode("ascii")


def _badge(passed: bool) -> str:
    color = PASS_COLOR if passed else FAIL_COLOR
    text = "OK" if passed else "FALLA"
    return f'<span style="color:{color}; font-weight:700;">{text}</span>'


def _conformance_rows(iso: dict) -> str:
    rows = [
        ("Primarios &Delta;E (C/M/Y)", iso.get("primaries_de")),
        ("Negro &Delta;E", iso.get("black_de")),
        ("TVI en luces", iso.get("highlight_tvi")),
        ("TVI en medios", iso.get("midtone_tvi")),
        ("TVI en sombras", iso.get("shadow_tvi")),
        ("Mid-Tone Spread", iso.get("mid_tone_spread")),
    ]
    return "".join(
        f"<tr><td>{label}</td><td>{_badge(bool(passed))}</td></tr>"
        for label, passed in rows
    )


def _solids_rows(analysis: dict, standard_key: str) -> str:
    solids = analysis.get("solids") or {}
    de_primaries = analysis.get("de_primaries") or {}
    std = ISO_STANDARDS.get(standard_key, {})
    rows = []
    for ch in ["C", "M", "Y", "K"]:
        solid = solids.get(ch)
        if not solid:
            continue
        if ch == "K":
            target_lab = std.get("lab_k")
            de = analysis.get("de_black")
            passed = analysis.get("de_black_passed")
        else:
            entry = de_primaries.get(ch, {})
            target_lab = entry.get("target")
            de = entry.get("de")
            passed = entry.get("passed")
        target_str = ", ".join(f"{v:.1f}" for v in target_lab) if target_lab else "—"
        meas_str = ", ".join(f"{v:.1f}" for v in solid["lab"])
        rows.append(
            f"<tr>"
            f"<td><strong>{CHANNEL_LABELS[ch]}</strong></td>"
            f"<td>{target_str}</td>"
            f"<td>{meas_str}</td>"
            f"<td>{de if de is not None else '—'}</td>"
            f"<td>{_badge(bool(passed))}</td>"
            f"</tr>"
        )
    return "".join(rows)


def _header_and_meta_html(analysis: dict, meta: dict) -> str:
    """Bloque compartido por PDF y HTML: marca, titulo, score box y tabla de
    setup. Identico en las dos salidas -- solo cambia lo que va despues."""
    overall_passed = bool(analysis.get("iso_compliance", {}).get("overall"))
    score = analysis.get("condition_score", 0)
    filename = meta.get("filename", "—")
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    return f"""
      <div class="brand">Zyra<span>Works</span> — Informe de Calibracion</div>
      <h1>Analisis de prensa offset vs {analysis.get("standard_name", "")}</h1>

      <div class="layout">
        <div class="col" style="flex: 0 0 160px;">
          <div class="score-box" style="background:{'#eafaf1' if overall_passed else '#fdecec'};
               border-color:{PASS_COLOR if overall_passed else FAIL_COLOR};">
            <div class="score-number" style="color:{PASS_COLOR if overall_passed else FAIL_COLOR};">{score}%</div>
            <div class="score-label">{"APROBADO" if overall_passed else "NO APROBADO"}</div>
          </div>
        </div>
        <div class="col">
          <table class="meta-table">
            <tr><td>Archivo</td><td>{filename}</td></tr>
            <tr><td>Standard</td><td>{analysis.get("standard_name", "")}</td></tr>
            <tr><td>Parches leidos</td><td>{analysis.get("total_patches", "—")}</td></tr>
            <tr><td>Generado</td><td>{generated_at}</td></tr>
          </table>
        </div>
      </div>

      <div class="section-title">Conformidad ISO 12647-2</div>
      <table>{_conformance_rows(analysis.get("iso_compliance", {}))}</table>

      <div class="section-title">Solidos (Lab &amp; &Delta;E00)</div>
      <table>
        <tr><th></th><th>Target Lab</th><th>Medido Lab</th><th>&Delta;E00</th><th></th></tr>
        {_solids_rows(analysis, meta.get("_standard_key", ""))}
      </table>

      <div class="section-title">Ganancia de punto (TVI) por canal</div>
    """


_SHARED_CSS = f"""
  body {{ font-family: -apple-system, "Segoe UI", Arial, sans-serif; color: #1a1a1a; }}
  .brand {{ font-size: 20px; font-weight: 800; color: {ACCENT}; letter-spacing: -0.02em; }}
  .brand span {{ color: #1a1a1a; }}
  h1 {{ font-size: 15px; margin: 4px 0 14px; color: #1a1a1a; }}
  .section-title {{
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em;
    color: #666666; border-bottom: 1px solid #dddddd; padding-bottom: 3px;
    margin: 13px 0 6px;
  }}
  table {{ width: 100%; border-collapse: collapse; font-size: 10.5px; }}
  td, th {{ padding: 4px 8px; border-bottom: 1px solid #eeeeee; text-align: left; }}
  .meta-table td:first-child {{ color: #666666; width: 140px; }}
  .score-box {{ display: inline-block; border-radius: 12px; padding: 14px 22px; border: 1px solid; }}
  .score-number {{ font-size: 30px; font-weight: 800; }}
  .score-label {{ font-size: 11px; color: #666666; }}
  .layout {{ display: flex; gap: 24px; }}
  .layout .col {{ flex: 1; }}
  footer {{ margin-top: 12px; font-size: 9px; color: #999999; }}
"""


def render_color_report_pdf(analysis: dict, standard_key: str, meta: dict) -> bytes | None:
    """meta: {'filename': str, 'requested_by': str opcional}. Devuelve bytes
    de un PDF, o None si no se pudo generar el grafico base."""
    tvi_grid_png = render_tvi_grid(analysis)
    if tvi_grid_png is None:
        return None

    body_meta = dict(meta, _standard_key=standard_key)
    html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <style>
      @page {{ size: A4; margin: 14mm 16mm; }}
      {_SHARED_CSS}
      img.chart {{ width: 94%; display: block; margin: 4px auto 0; }}
    </style>
    </head>
    <body>
      {_header_and_meta_html(analysis, body_meta)}
      <img class="chart" src="data:image/png;base64,{_b64(tvi_grid_png)}" />

      <footer>
        Generado automaticamente por el Color Agent de ZyraWorks. El gamut impreso
        y el detalle completo de parches no estan incluidos en esta version del informe.
      </footer>
    </body>
    </html>
    """

    return HTML(string=html).write_pdf()


def render_color_report_html(analysis: dict, standard_key: str, meta: dict) -> bytes | None:
    """Misma info que render_color_report_pdf, pero como .html standalone con
    el grafico de TVI interactivo (hover muestra nominal/medido/target/
    tolerancia por punto). Sin dependencias externas -- se puede abrir con
    doble click, sin conexion a internet. Devuelve bytes UTF-8, o None si no
    se pudo generar el grafico base."""
    tvi_grid_svg = render_tvi_grid_svg(analysis)
    if tvi_grid_svg is None:
        return None

    body_meta = dict(meta, _standard_key=standard_key)
    html = f"""<!doctype html>
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Informe de calibracion — {analysis.get("standard_name", "")}</title>
    <style>
      {_SHARED_CSS}
      body {{ max-width: 760px; margin: 24px auto; padding: 0 16px; background: #ffffff; }}
      .tvi-legend {{
        display: flex; flex-wrap: wrap; gap: 14px; font-size: 10.5px; color: #555555;
        margin-bottom: 8px;
      }}
      .tvi-legend span {{ display: inline-flex; align-items: center; gap: 5px; }}
      .tvi-swatch {{ display: inline-block; width: 14px; height: 3px; background: #999999; }}
      .tvi-swatch--tick {{ background: #555555; height: 4px; }}
      .tvi-swatch--dashed {{
        background: repeating-linear-gradient(90deg, #bbbbbb 0 3px, transparent 3px 5px);
      }}
      .tvi-grid {{
        display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
      }}
      .tvi-panel {{ width: 100%; height: auto; }}
      .tvi-point {{ cursor: pointer; }}
      .tvi-point:focus {{ outline: none; }}
      .tvi-tooltip {{
        position: fixed; z-index: 10; background: #1a1a1a; color: #ffffff;
        font-size: 11px; padding: 6px 9px; border-radius: 6px; pointer-events: none;
        max-width: 240px; line-height: 1.4;
      }}
      @media (max-width: 520px) {{ .tvi-grid {{ grid-template-columns: 1fr; }} }}
    </style>
    </head>
    <body>
      {_header_and_meta_html(analysis, body_meta)}
      {tvi_grid_svg}

      <footer>
        Generado automaticamente por el Color Agent de ZyraWorks. Pasa el mouse
        (o tocá, en pantalla táctil) sobre cada punto de las curvas para ver el
        detalle. El gamut impreso y el detalle completo de parches no estan
        incluidos en esta version del informe.
      </footer>
    </body>
    </html>
    """

    return html.encode("utf-8")
