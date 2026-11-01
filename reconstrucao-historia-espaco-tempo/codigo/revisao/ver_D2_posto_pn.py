"""Verificacao D2: posto do jacobiano das bandas PN (deslocamento (2,0) + spin (3,0)) ordem a ordem, com modelo
proprio (series fechadas H20 de Favata/Cunningham ate 1,5PN e S30 do relatorio), aritmetica de 40 digitos (mpmath)
e derivadas por diferenca central de passo 1e-12. Testa tambem: so deslocamento; outra grade de bandas; ponto q=3."""
import mpmath as mp
mp.mp.dps = 40
MSUN = mp.mpf('4.925490947e-6')

def bandas(th, ordem, freqs, tipos=(0, 1)):
    q, c1, c2, M, io, D = th
    m1 = q / (1 + q); m2 = 1 / (1 + q); nu = m1 * m2; de = m1 - m2
    s = m1**2 * c1 + m2**2 * c2; sg = m2 * c2 - m1 * c1
    a1 = (-mp.mpf(4075)/4032 + mp.mpf(67)/48*nu) if ordem >= 1 else 0
    a15 = (mp.mpf(16)/3*s + mp.mpf(419)/160*de*sg) if ordem >= 1.5 else 0
    b1 = (mp.mpf(7529)/4536 - mp.mpf(68)/27*nu) if ordem >= 1 else 0
    b15 = -(mp.mpf(415)/54*s + mp.mpf(3575)/864*de*sg) if ordem >= 1.5 else 0
    def h(f):
        x = (mp.pi * M * MSUN * f) ** (mp.mpf(2)/3)
        return nu * M * x * (1 + a1*x + a15*x**mp.mpf(1.5)) * mp.sin(io)**2 / D
    def S(f):
        x = (mp.pi * M * MSUN * f) ** (mp.mpf(2)/3)
        return nu * M**2 * x**mp.mpf(-0.5) * (1 + b1*x + b15*x**mp.mpf(1.5)) * mp.sin(io)**2 * mp.cos(io) / D
    out = []
    for fa, fb in zip(freqs[:-1], freqs[1:]):
        if 0 in tipos: out.append(mp.log(abs(h(fb) - h(fa))))
        if 1 in tipos: out.append(mp.log(abs(S(fa) - S(fb))))
    return out

def svals(th0, ordem, freqs, tipos=(0, 1)):
    esc = [0.1, 0.1, 0.1, 1.0, 0.01, 0.01 * th0[5]]
    hh = mp.mpf('1e-12')
    cols = []
    for j in range(6):
        tp = list(th0); tm = list(th0); tp[j] += hh * esc[j]; tm[j] -= hh * esc[j]
        yp = bandas(tp, ordem, freqs, tipos); ym = bandas(tm, ordem, freqs, tipos)
        cols.append([(a - b) / (2 * hh) for a, b in zip(yp, ym)])
    J = mp.matrix(len(cols[0]), 6)
    for j in range(6):
        for i in range(len(cols[0])):
            J[i, j] = cols[j][i]
    return [float(z) for z in mp.svd_r(J, compute_uv=False)]

A = [mp.mpf('1.2'), mp.mpf('0.3'), mp.mpf('-0.2'), mp.mpf(65), mp.radians(50), mp.mpf(400)]
Q3 = [mp.mpf(3), mp.mpf('0.6'), mp.mpf(0), mp.mpf(65), mp.radians(50), mp.mpf(400)]
fmax = mp.mpf('0.012') / (65 * MSUN)
g9 = [10 * (fmax / 10) ** (mp.mpf(j) / 8) for j in range(9)]
g4 = [10 * (fmax / 10) ** (mp.mpf(j) / 3) for j in range(4)]
for nome, th, gr, tipos in (("A, 8 bandas, desl+spin", A, g9, (0, 1)), ("A, 3 bandas, desl+spin", A, g4, (0, 1)),
                           ("A, 8 bandas, so desl", A, g9, (0,)), ("q=3, 8 bandas, desl+spin", Q3, g9, (0, 1))):
    print(nome)
    for ordem in (0, 1, 1.5):
        sv = svals(th, ordem, gr, tipos)
        print("   ordem %s: %s" % (ordem, " ".join("%.2e" % z for z in sv)))
