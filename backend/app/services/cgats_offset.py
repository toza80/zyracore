import math
import json

# ── STANDARDS ISO 12647-2 ──────────────────────────────────────────
ISO_STANDARDS = {
    'fogra39': {
        'name': 'Fogra 39 — ISO Coated v2',
        'description': 'Offset hoja, papel estucado brillante',
        'lab_white': [95.0, 0.0, -2.0],
        'lab_c':  [55.0, -37.0, -50.0],
        'lab_m':  [48.0,  74.0,  -3.0],
        'lab_y':  [89.0,  -5.0,  93.0],
        'lab_k':  [16.0,   0.0,   0.0],
        # TVI targets ISO 12647-2 — GANANCIA de punto esperada
        # Parches de la Fogra Media Wedge V3: 25%, 40%, 75% (no 20/40/70)
        # Fuente: ISO 12647-2:2013 Table 8 + Alwan JCT Fogra 39
        'tvi_gain': {
            'C': {25: 9.0,  40: 13.9, 75: 13.8},
            'M': {25: 8.0,  40: 12.3, 75: 12.7},
            'Y': {25: 8.5,  40: 13.3, 75: 13.5},
            'K': {25: 10.5, 40: 16.1, 75: 13.0},
        },
        # Valor impreso = nominal + ganancia
        'tvi': {
            'C': {25: 34.0, 40: 53.9, 75: 88.8},
            'M': {25: 33.0, 40: 52.3, 75: 87.7},
            'Y': {25: 33.5, 40: 53.3, 75: 88.5},
            'K': {25: 35.5, 40: 56.1, 75: 88.0},
        },
        'tvi_tolerance': {25: 3.0, 40: 4.0, 75: 3.0},
        'de_primary_tolerance': 5.0,
        'de_black_tolerance': 5.0,
        'mid_tone_spread_tolerance': 5.0,
    },
    'fogra51': {
        'name': 'Fogra 51 — PSO Coated v3',
        'description': 'Offset hoja, papel estucado, iluminante M1',
        'lab_white': [95.0, 0.0, -2.0],
        'lab_c':  [54.0, -36.0, -50.0],
        'lab_m':  [47.0,  73.0,  -3.0],
        'lab_y':  [88.0,  -5.0,  92.0],
        'lab_k':  [16.0,   0.0,   0.0],
        'tvi': {
            'C': {20: 28.5, 40: 54.0, 70: 84.0},
            'M': {20: 27.5, 40: 52.5, 70: 83.0},
            'Y': {20: 28.0, 40: 53.5, 70: 84.0},
            'K': {20: 30.0, 40: 56.0, 80: 92.0},
        },
        'tvi_tolerance': {20: 3.0, 40: 4.0, 70: 3.0, 80: 3.0},
        'de_primary_tolerance': 5.0,
        'de_black_tolerance': 5.0,
        'mid_tone_spread_tolerance': 5.0,
    },
    'fogra47': {
        'name': 'Fogra 47 — ISO Uncoated',
        'description': 'Offset hoja, papel no estucado',
        'lab_white': [92.0, 0.0, -3.0],
        'lab_c':  [52.0, -34.0, -46.0],
        'lab_m':  [46.0,  70.0,  -3.0],
        'lab_y':  [86.0,  -5.0,  88.0],
        'lab_k':  [16.0,   0.0,   0.0],
        'tvi': {
            'C': {20: 32.0, 40: 58.0, 70: 86.0},
            'M': {20: 30.0, 40: 56.0, 70: 85.0},
            'Y': {20: 31.0, 40: 57.0, 70: 86.0},
            'K': {20: 34.0, 40: 60.0, 80: 94.0},
        },
        'tvi_tolerance': {20: 4.0, 40: 5.0, 70: 4.0, 80: 4.0},
        'de_primary_tolerance': 5.0,
        'de_black_tolerance': 5.0,
        'mid_tone_spread_tolerance': 6.0,
    },
    'gracol': {
        'name': 'GRACoL 2013',
        'description': 'Offset hoja, papel estucado, mercado americano',
        'lab_white': [95.0, 0.0, -2.0],
        'lab_c':  [55.0, -37.0, -50.0],
        'lab_m':  [48.0,  74.0,  -3.0],
        'lab_y':  [89.0,  -5.0,  93.0],
        'lab_k':  [16.0,   0.0,   0.0],
        'tvi': {
            'C': {20: 29.0, 40: 54.0, 70: 84.0},
            'M': {20: 27.5, 40: 52.5, 70: 83.0},
            'Y': {20: 28.0, 40: 53.5, 70: 84.0},
            'K': {20: 30.5, 40: 56.5, 80: 92.0},
        },
        'tvi_tolerance': {20: 3.0, 40: 4.0, 70: 3.0, 80: 3.0},
        'de_primary_tolerance': 5.0,
        'de_black_tolerance': 5.0,
        'mid_tone_spread_tolerance': 5.0,
    },
    'fogra29': {
        'name': 'Fogra 29 — ISO Uncoated (2004, descontinuado)',
        'description': 'Offset hoja, papel no estucado 120g/m2, caracterizacion 2004 '
                        '(superada por Fogra47 y luego Fogra52). Datos de blanco y solidos '
                        'tomados del archivo oficial FOGRA29L.txt. El TVI en 20%/70% no esta '
                        'disponible con precision (solo hay dato colorimetrico oficial en 40%).',
        'lab_white': [95.71, 0.61, -2.32],
        'lab_c':  [59.04, -26.66, -42.80],
        'lab_m':  [55.04,  59.46,  -4.00],
        'lab_y':  [88.85,  -1.65,  79.16],
        'lab_k':  [31.88,   2.05,   2.08],
        'tvi_gain': {
            'C': {40: 19.6},
            'M': {40: 18.1},
            'Y': {40: 19.0},
            'K': {40: 22.0},
        },
        'tvi': {
            'C': {40: 59.6},
            'M': {40: 58.1},
            'Y': {40: 59.0},
            'K': {40: 62.0},
        },
        'tvi_tolerance': {40: 4.0},
        'de_primary_tolerance': 5.0,
        'de_black_tolerance': 5.0,
        'mid_tone_spread_tolerance': 5.0,
    },
    'fogra49': {
        'name': 'Fogra 49 — PSO Coated v2 300% Laminado Mate (ECI)',
        'description': 'Finishing proof: simula el resultado tras laminado OPP mate, no el '
                        'impreso sin laminar. Datos de blanco y solidos tomados del archivo '
                        'oficial FOGRA49.txt. TVI segun ISO 12647-2 curvas A (CMY) / B (K), '
                        'confirmado en el registro ICC oficial (color.org/chardata/fogra49) '
                        '- mismas curvas que ya usa Fogra39.',
        'lab_white': [94.11, 0.07, -1.72],
        'lab_c':  [56.07, -35.06, -48.46],
        'lab_m':  [49.72,  71.33,  -1.71],
        'lab_y':  [89.25,  -5.05,  90.18],
        'lab_k':  [22.17,  -0.32,  -0.26],
        'tvi_gain': {
            'C': {25: 9.0,  40: 13.9, 75: 13.8},
            'M': {25: 8.0,  40: 12.3, 75: 12.7},
            'Y': {25: 8.5,  40: 13.3, 75: 13.5},
            'K': {25: 10.5, 40: 16.1, 75: 13.0},
        },
        'tvi': {
            'C': {25: 34.0, 40: 53.9, 75: 88.8},
            'M': {25: 33.0, 40: 52.3, 75: 87.7},
            'Y': {25: 33.5, 40: 53.3, 75: 88.5},
            'K': {25: 35.5, 40: 56.1, 75: 88.0},
        },
        'tvi_tolerance': {25: 3.0, 40: 4.0, 75: 3.0},
        'de_primary_tolerance': 5.0,
        'de_black_tolerance': 5.0,
        'mid_tone_spread_tolerance': 5.0,
    },
    'fogra50': {
        'name': 'Fogra 50 — PSO Coated v2 300% Laminado Brillante (ECI)',
        'description': 'Finishing proof: simula el resultado tras laminado OPP brillante, no '
                        'el impreso sin laminar. Datos de blanco y solidos tomados del archivo '
                        'oficial FOGRA50.txt. TVI segun ISO 12647-2 curvas A (CMY) / B (K), '
                        'confirmado en el registro ICC oficial (color.org/chardata/fogra50) '
                        '- mismas curvas que ya usa Fogra39.',
        'lab_white': [93.99, 0.02, -1.66],
        'lab_c':  [54.27, -37.75, -50.31],
        'lab_m':  [47.32,  75.66,  -1.73],
        'lab_y':  [88.96,  -5.13,  96.30],
        'lab_k':  [11.69,  -0.55,   0.92],
        'tvi_gain': {
            'C': {25: 9.0,  40: 13.9, 75: 13.8},
            'M': {25: 8.0,  40: 12.3, 75: 12.7},
            'Y': {25: 8.5,  40: 13.3, 75: 13.5},
            'K': {25: 10.5, 40: 16.1, 75: 13.0},
        },
        'tvi': {
            'C': {25: 34.0, 40: 53.9, 75: 88.8},
            'M': {25: 33.0, 40: 52.3, 75: 87.7},
            'Y': {25: 33.5, 40: 53.3, 75: 88.5},
            'K': {25: 35.5, 40: 56.1, 75: 88.0},
        },
        'tvi_tolerance': {25: 3.0, 40: 4.0, 75: 3.0},
        'de_primary_tolerance': 5.0,
        'de_black_tolerance': 5.0,
        'mid_tone_spread_tolerance': 5.0,
    },
}

# Standards para proofer
PROOFER_STANDARDS = {
    'iso_coated_v2': {
        'name': 'ISO Coated v2 (Fogra 39)',
        'avg_de_tolerance': 3.0,
        'max_de_tolerance': 6.0,
        'substrate_de_tolerance': 3.0,
        'primary_de_tolerance': 5.0,
        'primary_dh_tolerance': 2.5,
        'gray_dh_tolerance': 1.5,
        'lab_c':  [55.0, -37.0, -50.0],
        'lab_m':  [48.0,  74.0,  -3.0],
        'lab_y':  [89.0,  -5.0,  93.0],
        'lab_k':  [16.0,   0.0,   0.0],
        'lab_white': [95.0, 0.0, -2.0],
    },
    'pso_coated_v3': {
        'name': 'PSO Coated v3 (Fogra 51)',
        'avg_de_tolerance': 3.0,
        'max_de_tolerance': 6.0,
        'substrate_de_tolerance': 3.0,
        'primary_de_tolerance': 5.0,
        'primary_dh_tolerance': 2.5,
        'gray_dh_tolerance': 1.5,
        'lab_c':  [54.0, -36.0, -50.0],
        'lab_m':  [47.0,  73.0,  -3.0],
        'lab_y':  [88.0,  -5.0,  92.0],
        'lab_k':  [16.0,   0.0,   0.0],
        'lab_white': [95.0, 0.0, -2.0],
    },
}

# ── MEDIA WEDGE V3 PATCHES ─────────────────────────────────────────
# Parches clave de la Ugra/Fogra Media Wedge V3
MEDIA_WEDGE_PATCHES = {
    'white':   (0, 0, 0, 0),
    'cyan':    (100, 0, 0, 0),
    'magenta': (0, 100, 0, 0),
    'yellow':  (0, 0, 100, 0),
    'black':   (0, 0, 0, 100),
    'tvi_c_20': (20, 0, 0, 0),
    'tvi_c_40': (40, 0, 0, 0),
    'tvi_c_70': (70, 0, 0, 0),
    'tvi_m_20': (0, 20, 0, 0),
    'tvi_m_40': (0, 40, 0, 0),
    'tvi_m_70': (0, 70, 0, 0),
    'tvi_y_20': (0, 0, 20, 0),
    'tvi_y_40': (0, 0, 40, 0),
    'tvi_y_70': (0, 0, 70, 0),
    'tvi_k_20': (0, 0, 0, 20),
    'tvi_k_40': (0, 0, 0, 40),
    'tvi_k_80': (0, 0, 0, 80),
    # Grises CMY para balance
    'gray_40': (40, 31, 31, 0),
    'gray_80': (80, 64, 64, 0),
}

def parse_cgats(content):
    """Parser CGATS genérico."""
    fields = []
    data = []
    in_format = False
    in_data = False
    for line in content.splitlines():
        line = line.strip()
        if line == 'BEGIN_DATA_FORMAT':
            in_format = True; continue
        if line == 'END_DATA_FORMAT':
            in_format = False; continue
        if line == 'BEGIN_DATA':
            in_data = True; continue
        if line == 'END_DATA':
            in_data = False; continue
        if in_format:
            fields = line.split()
        if in_data and line:
            values = line.split()
            if len(values) == len(fields):
                row = {}
                for f, v in zip(fields, values):
                    try:
                        row[f] = float(v)
                    except ValueError:
                        row[f] = v
                data.append(row)
    return fields, data

def get_patch(data, c, m, y, k, tol=2.0):
    for row in data:
        if (abs(row.get('CMYK_C', -999) - c) <= tol and
            abs(row.get('CMYK_M', -999) - m) <= tol and
            abs(row.get('CMYK_Y', -999) - y) <= tol and
            abs(row.get('CMYK_K', -999) - k) <= tol):
            return row
    return None

def delta_e_2000(lab1, lab2):
    if None in lab1 or None in lab2:
        return None
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    kL = kC = kH = 1.0
    C1 = math.sqrt(a1**2 + b1**2)
    C2 = math.sqrt(a2**2 + b2**2)
    Cab = (C1 + C2) / 2
    Cab7 = Cab**7
    G = 0.5 * (1 - math.sqrt(Cab7 / (Cab7 + 25**7)))
    a1p = a1*(1+G); a2p = a2*(1+G)
    C1p = math.sqrt(a1p**2 + b1**2)
    C2p = math.sqrt(a2p**2 + b2**2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dLp = L2-L1; dCp = C2p-C1p
    if C1p*C2p == 0: dhp = 0
    elif abs(h2p-h1p) <= 180: dhp = h2p-h1p
    elif h2p-h1p > 180: dhp = h2p-h1p-360
    else: dhp = h2p-h1p+360
    dHp = 2*math.sqrt(C1p*C2p)*math.sin(math.radians(dhp/2))
    Lp = (L1+L2)/2; Cp = (C1p+C2p)/2
    if C1p*C2p == 0: Hp = h1p+h2p
    elif abs(h1p-h2p) <= 180: Hp = (h1p+h2p)/2
    elif h1p+h2p < 360: Hp = (h1p+h2p+360)/2
    else: Hp = (h1p+h2p-360)/2
    T = (1-0.17*math.cos(math.radians(Hp-30))
           +0.24*math.cos(math.radians(2*Hp))
           +0.32*math.cos(math.radians(3*Hp+6))
           -0.20*math.cos(math.radians(4*Hp-63)))
    SL = 1+0.015*(Lp-50)**2/math.sqrt(20+(Lp-50)**2)
    SC = 1+0.045*Cp; SH = 1+0.015*Cp*T
    dTheta = 30*math.exp(-((Hp-275)/25)**2)
    RC = 2*math.sqrt(Cp**7/(Cp**7+25**7))
    RT = -math.sin(math.radians(2*dTheta))*RC
    dE = math.sqrt((dLp/(kL*SL))**2+(dCp/(kC*SC))**2+
                   (dHp/(kH*SH))**2+RT*(dCp/(kC*SC))*(dHp/(kH*SH)))
    return round(dE, 2)

def murray_davies_tvi(Rp, Rw, Ri):
    if Rw == Ri or Rw == 0:
        return None
    return round(min(max((Rw-Rp)/(Rw-Ri)*100, 0), 100), 2)

def get_reflectance_for_channel(patch, channel, white):
    """
    Selecciona el canal de reflectancia correcto para cada tinta.
    C,M,K usan XYZ_Y (luminancia).
    Y usa XYZ_Y también pero normalizado diferente — usa D_BLUE si disponible.
    """
    if channel == 'Y':
        # Yellow absorbe en azul — usar D_BLUE o canal espectral azul
        d_blue = patch.get('D_BLUE')
        w_blue = white.get('D_BLUE')
        if d_blue is not None and w_blue is not None and w_blue > 0:
            # Convertir densidad a reflectancia: R = 10^(-D)
            Rp = 10 ** (-d_blue)
            Rw = 10 ** (-w_blue)
            Ri_patch = patch.get('XYZ_Y', 0) / 100
            Rw_xyz = white.get('XYZ_Y', 84.77) / 100
            # Usar Murray-Davies con reflectancia azul
            Ri_blue = 10 ** (-white.get('D_BLUE', 0))  # sólido Y tiene D_BLUE alto
            return Rp, Rw, None  # señal para usar D_BLUE directo
    return (patch.get('XYZ_Y', 0)/100, 
            white.get('XYZ_Y', 84.77)/100, 
            None)

def analyze_cgats_offset(content, standard_key='fogra39'):
    """Análisis completo CGATS para prensa offset vs ISO 12647-2."""
    std = ISO_STANDARDS.get(standard_key)
    if not std:
        return {'error': f'Standard {standard_key} no encontrado.'}

    fields, data = parse_cgats(content)
    if not data:
        return {'error': 'No se pudieron leer datos del archivo.'}

    white = get_patch(data, 0, 0, 0, 0)
    if not white:
        return {'error': 'No se encontró parche de blanco (0,0,0,0).'}

    white_lab = [white['LAB_L'], white['LAB_A'], white['LAB_B']]
    Rw = white.get('XYZ_Y', 84.77) / 100

    # Sólidos CMYK
    solids = {}
    for ch, c, m, y, k in [('C',100,0,0,0),('M',0,100,0,0),
                             ('Y',0,0,100,0),('K',0,0,0,100)]:
        p = get_patch(data, c, m, y, k)
        if p:
            solids[ch] = {
                'lab': [round(p['LAB_L'],2), round(p['LAB_A'],2), round(p['LAB_B'],2)],
                'density': round(p.get('D_VIS', 0), 3),
                'Ri': p.get('XYZ_Y', 0) / 100,
            }

    # Delta E sólidos vs standard
    de_primaries = {}
    for ch in ['C','M','Y']:
        if ch in solids:
            target = std[f'lab_{ch.lower()}']
            de = delta_e_2000(solids[ch]['lab'], target)
            de_primaries[ch] = {
                'de': de,
                'target': target,
                'measured': solids[ch]['lab'],
                'tolerance': std['de_primary_tolerance'],
                'passed': de is not None and de <= std['de_primary_tolerance'],
            }

    de_black = None
    if 'K' in solids:
        de_black = delta_e_2000(solids['K']['lab'], std['lab_k'])

    # TVI por canal usando densidades espectrales (igual que Alwan/ISO)
    # C->D_RED, M->D_GREEN, Y->D_BLUE, K->D_VIS
    DENSITY_FIELDS = {'C': 'D_RED', 'M': 'D_GREEN', 'Y': 'D_BLUE', 'K': 'D_VIS'}
    SOLID_PATCHES  = {'C': (100,0,0,0), 'M': (0,100,0,0),
                      'Y': (0,0,100,0), 'K': (0,0,0,100)}

    tvi_measured = {}
    tvi_compliance = {}
    tvi_gain_targets = std.get('tvi_gain', {})
    tvi_targets = std['tvi']
    tvi_tolerance = std['tvi_tolerance']

    for ch in ['C', 'M', 'Y', 'K']:
        if ch not in solids:
            continue
        df = DENSITY_FIELDS[ch]
        solid_p = get_patch(data, *SOLID_PATCHES[ch])
        if not solid_p:
            continue

        d_w = white.get(df)
        d_i = solid_p.get(df)
        use_density = (d_w is not None and d_i is not None
                       and d_w > 0 and d_i > 0)

        ch_tvi = {}
        ch_compliance = {}
        gain_targets = tvi_gain_targets.get(ch, {})
        abs_targets   = tvi_targets.get(ch, {})

        for pct in [10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90]:
            if ch == 'C': p = get_patch(data, pct, 0, 0, 0)
            elif ch == 'M': p = get_patch(data, 0, pct, 0, 0)
            elif ch == 'Y': p = get_patch(data, 0, 0, pct, 0)
            else: p = get_patch(data, 0, 0, 0, pct)

            if not p:
                continue

            if use_density and p.get(df) is not None:
                Rp_ch = 10 ** (-p[df])
                Rw_ch = 10 ** (-d_w)
                Ri_ch = 10 ** (-d_i)
                tvi = murray_davies_tvi(Rp_ch, Rw_ch, Ri_ch)
            else:
                Ri = solids[ch]['Ri']
                tvi = murray_davies_tvi(p.get('XYZ_Y',0)/100, Rw, Ri)

            if tvi is None:
                continue

            ch_tvi[pct] = tvi
            gain_measured = round(tvi - pct, 2)

            # Buscar target — primero ganancia, después absoluto
            if pct in gain_targets:
                tol = tvi_tolerance.get(pct, 4.0)
                gain_target = gain_targets[pct]
                deviation = round(gain_measured - gain_target, 2)
                ch_compliance[pct] = {
                    'measured':     tvi,
                    'gain_measured': gain_measured,
                    'gain_target':  gain_target,
                    'target':       abs_targets.get(pct, round(pct + gain_target, 1)),
                    'tolerance':    tol,
                    'deviation':    deviation,
                    'passed':       abs(deviation) <= tol,
                }
            elif pct in abs_targets:
                tol = tvi_tolerance.get(pct, 4.0)
                deviation = round(tvi - abs_targets[pct], 2)
                ch_compliance[pct] = {
                    'measured':     tvi,
                    'gain_measured': gain_measured,
                    'gain_target':  round(abs_targets[pct] - pct, 1),
                    'target':       abs_targets[pct],
                    'tolerance':    tol,
                    'deviation':    deviation,
                    'passed':       abs(deviation) <= tol,
                }
                if tvi is not None:
                    ch_tvi[pct] = tvi
                    # Calcular ganancia real
                    gain_measured = round(tvi - pct, 2)

                    if pct in gain_targets:
                        tol = tvi_tolerance.get(pct, 4.0)
                        gain_target = gain_targets[pct]
                        deviation = round(gain_measured - gain_target, 2)
                        ch_compliance[pct] = {
                            'measured': tvi,
                            'gain_measured': gain_measured,
                            'gain_target': gain_target,
                            'target': abs_targets.get(pct, pct + gain_target),
                            'tolerance': tol,
                            'deviation': deviation,
                            'passed': abs(deviation) <= tol,
                        }
                    elif pct in abs_targets:
                        tol = tvi_tolerance.get(pct, 4.0)
                        deviation = round(tvi - abs_targets[pct], 2)
                        ch_compliance[pct] = {
                            'measured': tvi,
                            'gain_measured': gain_measured,
                            'gain_target': round(abs_targets[pct] - pct, 1),
                            'target': abs_targets[pct],
                            'tolerance': tol,
                            'deviation': deviation,
                            'passed': abs(deviation) <= tol,
                        }
        tvi_measured[ch] = ch_tvi
        tvi_compliance[ch] = ch_compliance

    # Mid-Tone Spread — diferencia de GANANCIA en 40% entre C, M, Y
    # (no de valor impreso — Alwan usa ganancia)
    mts = None
    gain_c_40 = round(tvi_measured.get('C', {}).get(40, 0) - 40, 2) if tvi_measured.get('C', {}).get(40) else None
    gain_m_40 = round(tvi_measured.get('M', {}).get(40, 0) - 40, 2) if tvi_measured.get('M', {}).get(40) else None
    gain_y_40 = round(tvi_measured.get('Y', {}).get(40, 0) - 40, 2) if tvi_measured.get('Y', {}).get(40) else None
    if gain_c_40 is not None and gain_m_40 is not None and gain_y_40 is not None:
        mts = round(max(gain_c_40, gain_m_40, gain_y_40) - min(gain_c_40, gain_m_40, gain_y_40), 2)

    mts_tolerance = std['mid_tone_spread_tolerance']
    mts_passed = mts is not None and mts <= mts_tolerance

    # Balance de grises
    gray_balance = []
    for combo, label in [((40,31,31,0),'40%'), ((80,64,64,0),'80%')]:
        p = get_patch(data, *combo, tol=3.0)
        if p:
            lab = [round(p['LAB_L'],2), round(p['LAB_A'],2), round(p['LAB_B'],2)]
            neutrality = math.sqrt(lab[1]**2 + lab[2]**2)
            gray_balance.append({
                'label': label,
                'lab': lab,
                'neutrality': round(neutrality, 2),
                'cast': 'neutro' if neutrality < 2 else 'leve' if neutrality < 4 else 'significativo',
            })

    # ISO Compliance global
    # Highlight/Shadow TVI = spread (variacion) entre canales, igual que Alwan
    tvi_tolerance = std['tvi_tolerance']
    highlight_tol = tvi_tolerance.get(20, tvi_tolerance.get(25, 3.0))
    shadow_tol    = tvi_tolerance.get(70, tvi_tolerance.get(75, 3.0))
    midtone_tol   = tvi_tolerance.get(40, 4.0)

    # Spread en luces (20%) — variacion maxima entre C,M,Y,K
    # FIX: usar tvi_measured (siempre poblado) en vez de tvi_compliance
    # (que solo existe si hay un target 20/25 definido en el standard).
    gains_20 = {}
    for ch in ['C','M','Y','K']:
        tvi_val = tvi_measured.get(ch, {}).get(20)
        pct_ref = 20
        if tvi_val is None:
            tvi_val = tvi_measured.get(ch, {}).get(25)
            pct_ref = 25
        if tvi_val is not None:
            gains_20[ch] = round(tvi_val - pct_ref, 2)
    highlight_spread = round(max(gains_20.values()) - min(gains_20.values()), 2) if len(gains_20) >= 2 else None
    highlight_passed = highlight_spread is not None and highlight_spread <= highlight_tol * 2

    # Spread en medios (40%) — cada canal vs su target
    midtone_passed = all(
        tvi_compliance.get(ch, {}).get(40, {}).get('passed', False)
        for ch in ['C','M','Y','K']
        if tvi_compliance.get(ch, {}).get(40)
    )

    # Spread en sombras (70%) — variacion maxima entre C,M,Y
    # FIX: usar tvi_measured (siempre poblado) en vez de tvi_compliance.
    gains_70 = {}
    for ch in ['C','M','Y']:
        tvi_val = tvi_measured.get(ch, {}).get(70)
        pct_ref = 70
        if tvi_val is None:
            tvi_val = tvi_measured.get(ch, {}).get(75)
            pct_ref = 75
        if tvi_val is not None:
            gains_70[ch] = round(tvi_val - pct_ref, 2)
    shadow_spread = round(max(gains_70.values()) - min(gains_70.values()), 2) if len(gains_70) >= 2 else None
    shadow_passed = shadow_spread is not None and shadow_spread <= shadow_tol * 2

    all_de_passed = all(v['passed'] for v in de_primaries.values())
    de_black_passed = de_black is not None and de_black <= std['de_black_tolerance']

    iso_compliance = {
        'primaries_de':  all_de_passed,
        'black_de':      de_black_passed,
        'highlight_tvi': highlight_passed,
        'midtone_tvi':   midtone_passed,
        'shadow_tvi':    shadow_passed,
        'mid_tone_spread': mts_passed,
        'overall': (all_de_passed and de_black_passed and highlight_passed
                    and midtone_passed and shadow_passed and mts_passed),
    }

    # Guardar spreads para mostrar en UI
    iso_compliance['highlight_spread'] = highlight_spread
    iso_compliance['shadow_spread']    = shadow_spread
    iso_compliance['highlight_tol']    = round(highlight_tol * 2, 1)
    iso_compliance['shadow_tol']       = round(shadow_tol * 2, 1)

    # Score 0-100
    checks = [iso_compliance[k] for k in
              ['primaries_de','black_de','highlight_tvi','midtone_tvi','shadow_tvi','mid_tone_spread']]
    score = round(sum(checks) / len(checks) * 100)

    return {
        'standard': standard_key,
        'standard_name': std['name'],
        'white_lab': [round(v,2) for v in white_lab],
        'solids': solids,
        'de_primaries': de_primaries,
        'de_black': de_black,
        'de_black_passed': de_black_passed,
        'tvi_measured': tvi_measured,
        'tvi_compliance': tvi_compliance,
        'mid_tone_spread': mts,
        'mid_tone_spread_passed': mts_passed,
        'gray_balance': gray_balance,
        'iso_compliance': iso_compliance,
        'condition_score': score,
        'total_patches': len(data),
    }

def analyze_proofer_cgats(content, standard_key='iso_coated_v2'):
    """Análisis CGATS para proofer vs ISO Coated v2 / PSO Coated v3."""
    std = PROOFER_STANDARDS.get(standard_key)
    if not std:
        return {'error': f'Standard {standard_key} no encontrado.'}

    fields, data = parse_cgats(content)
    if not data:
        return {'error': 'No se pudieron leer datos del archivo.'}

    # Sustrato
    white = get_patch(data, 0, 0, 0, 0)
    white_lab = [white['LAB_L'], white['LAB_A'], white['LAB_B']] if white else [95,0,-2]
    substrate_de = delta_e_2000(white_lab, std['lab_white']) if white else None

    # Primarios
    results = []
    all_de = []
    for name, c, m, y, k, target_key in [
        ('Cyan',    100,0,0,0,   'lab_c'),
        ('Magenta', 0,100,0,0,   'lab_m'),
        ('Yellow',  0,0,100,0,   'lab_y'),
        ('Black',   0,0,0,100,   'lab_k'),
        ('Blue',    100,100,0,0, None),
        ('Red',     0,100,100,0, None),
        ('Green',   100,0,100,0, None),
    ]:
        p = get_patch(data, c, m, y, k)
        if p:
            lab = [round(p['LAB_L'],2), round(p['LAB_A'],2), round(p['LAB_B'],2)]
            target = std.get(target_key) if target_key else None
            de = delta_e_2000(lab, target) if target else None
            all_de.append(de or 0)
            results.append({
                'name': name,
                'cmyk': (c,m,y,k),
                'lab': lab,
                'target': target,
                'de': de,
                'passed': de is not None and de <= std['primary_de_tolerance'] if target else None,
            })

    avg_de = round(sum(all_de)/len(all_de), 2) if all_de else None
    max_de = round(max(all_de), 2) if all_de else None

    passed = (
        (avg_de or 999) <= std['avg_de_tolerance'] and
        (max_de or 999) <= std['max_de_tolerance'] and
        (substrate_de or 999) <= std['substrate_de_tolerance']
    )

    score = 100
    if avg_de and avg_de > std['avg_de_tolerance']: score -= 30
    if max_de and max_de > std['max_de_tolerance']: score -= 30
    if substrate_de and substrate_de > std['substrate_de_tolerance']: score -= 20

    return {
        'standard': standard_key,
        'standard_name': std['name'],
        'white_lab': white_lab,
        'substrate_de': substrate_de,
        'substrate_passed': substrate_de is not None and substrate_de <= std['substrate_de_tolerance'],
        'results': results,
        'avg_de': avg_de,
        'max_de': max_de,
        'avg_de_tolerance': std['avg_de_tolerance'],
        'max_de_tolerance': std['max_de_tolerance'],
        'passed': passed,
        'score': max(0, score),
        'total_patches': len(data),
    }

def analyze_mediawedge(content, standard_key='fogra39', baseline_data=None):
    """
    Análisis de Media Wedge V3 para verificación periódica.
    Compara vs ISO 12647-2 Y vs la calibración base del cliente.
    """
    result = analyze_cgats_offset(content, standard_key)
    if result.get('error'):
        return result

    # Comparación vs baseline si existe
    if baseline_data:
        baseline_tvi = baseline_data.get('tvi_measured', {})
        baseline_solids = baseline_data.get('solids', {})
        drift = {}

        for ch in ['C','M','Y','K']:
            ch_drift = {}
            for pct in [20, 40, 70, 80]:
                measured = result['tvi_measured'].get(ch, {}).get(pct)
                base = baseline_tvi.get(ch, {})
                if isinstance(base, dict):
                    base_val = base.get(str(pct)) or base.get(pct)
                else:
                    base_val = None
                if measured is not None and base_val is not None:
                    ch_drift[pct] = round(measured - float(base_val), 2)
            drift[ch] = ch_drift

        result['drift_from_baseline'] = drift

        # ΔE vs baseline sólidos
        de_drift = {}
        for ch in ['C','M','Y','K']:
            current = result['solids'].get(ch, {}).get('lab')
            base_solid = baseline_solids.get(ch, {}).get('lab')
            if current and base_solid:
                de_drift[ch] = delta_e_2000(current, base_solid)
        result['de_drift'] = de_drift

    return result

def analyze_proofer_verification(content, standard_key='iso_coated_v2', baseline_data=None):
    """Verificación periódica de proofer con Media Wedge."""
    result = analyze_proofer_cgats(content, standard_key)
    if result.get('error'):
        return result

    if baseline_data:
        baseline_results = {r['name']: r for r in baseline_data.get('results', [])}
        drift = []
        for r in result['results']:
            base = baseline_results.get(r['name'])
            if base and r['de'] is not None and base.get('de') is not None:
                drift.append({
                    'name': r['name'],
                    'current_de': r['de'],
                    'baseline_de': base['de'],
                    'drift': round(r['de'] - base['de'], 2),
                })
        result['drift'] = drift

    return result
