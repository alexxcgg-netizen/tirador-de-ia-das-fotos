"""Observaveis de memoria numa janela fisica [t_i, fim], com as correcoes da revisao adversarial da etapa 6.

Corrige (ver linhas/L00_infraestrutura.md e os itens da revisao):
  1. escada numerica: em binarias.gerar a grade do substituto comeca no primeiro ponto depois de f_low e
     a janela salta de dt quando M muda (saltos de ~3e-6 no spin). Aqui a onda e avaliada numa rede FIXA
     t_k = (k + t_desloc) dt (ancorada no pico, opcao `times` do gwsurrogate), gerada desde 0.9 f0, e a
     janela comeca no instante exato t_i em que a frequencia do modo (2,2) vale f0 (interpolacao linear);
     o primeiro subintervalo parcial entra na quadratura por interpolacao linear (pesos_janela). As
     memorias sao funcoes suaves de M, q, chi. A fase orbital e zerada exatamente em t_i (o gwsurrogate
     zera a fase no ponto da grade mais proximo de f_ref, outra escada, que so afeta os m != 0).
  2. multipolos m != 0: todos_m=True guarda todos os (l, m), l <= 8, e no_observador_completo soma todos
     com sYlm(s, l, m, iota, phi); phi e o azimute do observador medido a partir da fase orbital em t_i.
  3. deslocamento de janela (desl='janela', o observavel) separado do total (desl='total', como binarias).
  4. memoria de CM: parte nula da janela + ordinaria -(3/2) M_f Dfrak^-1 Delta Phi com o MESMO deslocamento
     da opcao desl (em binarias a ordinaria usa o total e a nula so a janela). Observacao: com
     desl='total' a parte nula continua sendo so a da janela (a nula total diverge com o inicio da
     inspiral); essa opcao existe para comparar com binarias.
  6. serie_memoria(tipo='nula') da a memoria nula pelo fluxo dos modos oscilatorios (sem o toque quase
     normal dos modos m = 0 de RN, que tipo='rn' inclui).
 13. comparar2 / snr2: janela de Tukey no inicio, degrau final tratado (valor inicial subtraido, valor final
     mantido 4 s e rampa de cosseno de 8 s), reamostragem por spline cubica e busca no tempo refinada
     (zero padding do espectro cruzado e depois maximizacao continua no atraso).

Outras escolhas (documentadas no L00):
  - derivada temporal por diferencas centrais de 8a ordem (binarias usa 4a ordem; o erro de truncamento da
    4a ordem na fusao, ~6e-6 no deslocamento com dt = 0.25 M, domina a convergencia em dt). ordem_deriv=4
    reproduz binarias.
  - M_f = 1 - E_janela - E_lig(x_i), com E_lig 3PN sem spin + spin-orbita 1.5PN, 2.5PN e 3.5PN (Blanchet
    LRR 2014, eq. 415); ordem_elig=1 reproduz binarias (1PN).

Unidades adimensionais como em binarias: tempo em M, h = r (h_+ - i h_x) / M. Nao guarda formas de onda em
caches: cada chamada gera a onda, calcula e devolve so numeros (ou a serie pedida).

Verificacao L00 (linhas/L00_infraestrutura_verificacao.md): unica correcao, em comparar2. O 'atraso' devolvido e
contado entre as primeiras amostras das series (o alinhamento pelo pico em preparar nao muda as amostras), e nao
"relativo ao alinhamento pelos picos" como dizia a docstring; acrescentado 'atraso_rotulos' (atraso de B em relacao
a A nos rotulos de tempo dados). Nenhum numero de memoria, SNR ou match mudou.
"""
import numpy as np

import binarias as B
from deteccao import MSUN_S, MPC_S, psd_serie
from harmonicos import sYlm, Dfrak, ethb2_de_escalar
from memorias import CalculadoraMemoria       # noqa: F401  (reexportado para os scripts de linha)

TIPOS = B.TIPOS
LMAX = 8
FRAC_INICIO = 0.9          # a onda e gerada desde FRAC_INICIO * f0


# ------------------------------------------------------------------ onda na rede fixa
def derivada(H, dt, ordem=8):
    """Derivada temporal por diferencas centrais de ordem 8 (ou 4, como binarias.derivada4) ao longo do eixo 0."""
    D = B.derivada4(H, dt)
    if ordem == 4:
        return D
    c = (4 / 5, -1 / 5, 4 / 105, -1 / 280)
    n = H.shape[0]
    acc = np.zeros_like(H[4:n - 4])
    for j, cj in enumerate(c, start=1):
        acc += cj * (H[4 + j:n - 4 + j] - H[4 - j:n - 4 - j])
    D[4:n - 4] = acc / dt
    return D


def _freq22(t, h22):
    """Frequencia angular do modo (2,2), -d/dt da fase desenrolada (h22 ~ exp(-2 i phi_orb)), e a fase."""
    fase = np.unwrap(np.angle(h22))
    w = -derivada(fase, t[1] - t[0], ordem=8)
    return w, fase


def instante_frequencia(t, h22, f0):
    """Instante t_i (interpolacao linear de omega_22) em que omega_22 = 2 pi f0, antes do pico; e (k, fase)."""
    w, fase = _freq22(t, h22)
    w0 = 2 * np.pi * f0
    ate_pico = np.nonzero(t <= 0)[0]
    acima = ate_pico[w[ate_pico] >= w0]
    if len(acima) == 0 or acima[0] == 0:
        raise ValueError("f0 fora do trecho gerado")
    k = int(acima[0])                                   # primeiro ponto com omega >= omega0
    ti = t[k - 1] + (w0 - w[k - 1]) / (w[k] - w[k - 1]) * (t[k] - t[k - 1])
    return float(ti), k, fase


def _fase_em(t, fase, ti, k):
    """Fase do (2,2) em ti por interpolacao cubica local (4 pontos em torno de ti)."""
    idx = np.arange(k - 2, k + 2)
    return float(np.polyval(np.polyfit(t[idx] - ti, fase[idx], 3), 0.0))


def gerar_janela(q, chi1, chi2, M_msun, f_ini_hz, dt=0.25, t_desloc=0.0):
    """Onda NRHybSur3dq8_CCE na rede fixa t_k = (k + t_desloc) dt e o instante t_i em que f_22 = f0.

    f0 = M MSUN_S f_ini (adimensional). A onda e gerada desde ~0.9 f0 (opcao `times` do gwsurrogate, que nao
    trunca nem desloca a rede). A fase orbital e zerada exatamente em t_i: h_lm -> h_lm exp(-i m Phi22(t_i)/2),
    com Phi22(t_i) pequeno (o gwsurrogate ja zera a fase no ponto da rede mais proximo de f_ref = f0, o que
    tambem fixa a ambiguidade de pi: buraco mais pesado no eixo +x). Devolve (t, h, t_i), t em M, h dict de
    modos (todos, inclusive m = 0 e m < 0) como binarias.gerar.
    """
    f0 = M_msun * MSUN_S * f_ini_hz
    f_low = FRAC_INICIO * f0
    sur = B._sur()
    cA, cB = [0.0, 0.0, chi1], [0.0, 0.0, chi2]
    t1, _, _ = sur(q, cA, cB, dt=dt, f_low=f_low, mode_list=[(2, 2)])    # so para achar o dominio valido
    k0 = int(np.ceil(t1[0] / dt - t_desloc)) + 1
    k1 = int(np.floor(t1[-1] / dt - t_desloc))
    tt = (np.arange(k0, k1 + 1) + t_desloc) * dt
    del t1
    t, h, _ = sur(q, cA, cB, times=tt, f_low=f_low, f_ref=f0)
    h = {(int(l), int(m)): np.asarray(v) for (l, m), v in h.items()}
    t = np.asarray(t)
    ti, k, fase = instante_frequencia(t, h[(2, 2)], f0)
    f22 = _fase_em(t, fase, ti, k)
    dphi = float(np.angle(np.exp(1j * f22)))        # pequeno: |dphi| ~ omega dt
    for (l, m) in h:
        if m != 0:
            h[(l, m)] = h[(l, m)] * np.exp(-0.5j * m * dphi)
    return t, h, ti


# ------------------------------------------------------------------ quadratura na janela
def pesos_janela(t, t_i):
    """Pesos de trapezio para int_{t_i}^{t[-1]} f dt numa grade uniforme t.

    O subintervalo parcial [t_i, t_k] (t_{k-1} < t_i <= t_k) usa f(t_i) por interpolacao linear entre
    t_{k-1} e t_k: a integral e funcao continua (e suave por partes, com derivada continua) de t_i.
    """
    dt = t[1] - t[0]
    n = len(t)
    k = int(np.searchsorted(t, t_i, side="left"))      # t[k-1] < t_i <= t[k]
    if k <= 0 or k >= n - 1:
        raise ValueError("t_i fora da grade")
    a = (t_i - t[k - 1]) / dt                          # fracao em [0, 1)
    L = t[k] - t_i
    w = np.zeros(n)
    w[k - 1] = 0.5 * L * (1 - a)
    w[k] = 0.5 * L * (1 + a) + 0.5 * dt
    w[k + 1:n - 1] = dt
    w[n - 1] += 0.5 * dt
    return w


def gram_pesos(H, Hd, w):
    """Matrizes de Gram com pesos: B = sum w hdot hdot^dagger, A = sum w h hdot^dagger (como memorias.gram)."""
    Hdw = Hd * w[:, None]
    Bm = Hdw.T @ Hd.conj()
    Am = (H * w[:, None]).T @ Hd.conj()
    return Bm, Am


# ------------------------------------------------------------------ energia de ligacao (PN)
def e_lig(x, q, chi1, chi2, ordem=3):
    """Energia de ligacao (positiva) de orbita circular em unidades da massa total.

    E = -(eta x/2) {1 + x(-3/4 - eta/12) + x^2(-27/8 + 19/8 eta - eta^2/24)
         + x^3(-675/64 + (34445/576 - 205/96 pi^2) eta - 155/96 eta^2 - 35/5184 eta^3)
         + x^1.5 [14/3 S + 2 d Sig] + x^2.5 [(11 - 61/9 eta) S + d(3 - 10/3 eta) Sig]
         + x^3.5 [(135/4 - 367/4 eta + 29/12 eta^2) S + d(27/4 - 39 eta + 5/4 eta^2) Sig]}
    (Blanchet, Living Rev. Relativ. 17, 2 (2014), eqs. 233 e 415), S = chi1 m1^2 + chi2 m2^2,
    Sig = chi2 m2 - chi1 m1, d = m1 - m2 (M = 1). ordem=1: so ate 1PN (como binarias); ordem=3: tudo acima.
    Sem os termos spin-spin (2PN, ~1e-6 em M_f para |chi| <= 0.3, x ~ 0.05).
    """
    eta = q / (1 + q) ** 2
    m1, m2 = q / (1 + q), 1 / (1 + q)
    s = 1 + x * (-0.75 - eta / 12)
    if ordem >= 2:
        S = chi1 * m1 ** 2 + chi2 * m2 ** 2
        Sig = chi2 * m2 - chi1 * m1
        d = m1 - m2
        pi = np.pi
        s = (s + x ** 2 * (-27 / 8 + 19 / 8 * eta - eta ** 2 / 24)
             + x ** 3 * (-675 / 64 + (34445 / 576 - 205 / 96 * pi ** 2) * eta - 155 / 96 * eta ** 2
                         - 35 / 5184 * eta ** 3)
             + x ** 1.5 * (14 / 3 * S + 2 * d * Sig)
             + x ** 2.5 * ((11 - 61 / 9 * eta) * S + d * (3 - 10 / 3 * eta) * Sig)
             + x ** 3.5 * ((135 / 4 - 367 / 4 * eta + 29 / 12 * eta ** 2) * S
                           + d * (27 / 4 - 39 * eta + 5 / 4 * eta ** 2) * Sig))
    return 0.5 * eta * x * s


# ------------------------------------------------------------------ memorias da janela
def _restringir(m, todos_m):
    out = {}
    for tipo in TIPOS:
        out[tipo] = {k: complex(v) for k, v in m[tipo].items() if k[0] <= LMAX and (todos_m or k[1] == 0)}
    return out


def _interp_em(t, y, t_i):
    """Valor de y em t_i por interpolacao linear."""
    k = int(np.searchsorted(t, t_i, side="left"))
    a = (t_i - t[k - 1]) / (t[k] - t[k - 1])
    return (1 - a) * y[k - 1] + a * y[k]


def memorias_observaveis(q, chi1, chi2, M_msun, f_ini_hz, nivel="A", desl="janela", todos_m=False, dt=0.25,
                         t=None, h=None, t_i=None, ordem_deriv=8, ordem_elig=3):
    """Memorias acumuladas de t_i (f_22 = f_ini) ao fim, dict por tipo e (l, m), l <= 8; e auxiliares.

    nivel 'A': partes nulas pelos fluxos dos modos oscilatorios (m != 0 do substituto).
    nivel 'C': deslocamento h_l0(fim) - h_l0(t_i) (l = 2, 4; com desl='total', h_l0(fim)); spin
               int_{t_i} h_30 du; giroscopica -Dfrak(3) Psi_30 + helicidade de todos os modos (como o nivel C
               de binarias); os demais multipolos pelos fluxos com todos os modos.
    desl 'janela' (observavel) ou 'total' (soma favata_h20 / lrr_h40 em x_i no nivel A, como binarias).
    CM = parte nula da janela + ordinaria -(3/2) M_f Dfrak^-1 Delta Phi com o deslocamento da opcao desl.
    todos_m=True guarda tambem os multipolos m != 0.
    aux: E_janela, E_lig (antes de t_i), M_f = 1 - E_janela - E_lig(x_i), P_rad, recuo (= -P/M_f), t_i, x_i, eta.
    Se (t, h, t_i) forem dados (de gerar_janela com os mesmos parametros), a onda nao e gerada de novo.
    """
    if desl not in ("janela", "total"):
        raise ValueError("desl deve ser 'janela' ou 'total'")
    if h is None:
        t, h, t_i = gerar_janela(q, chi1, chi2, M_msun, f_ini_hz, dt)
    dtt = t[1] - t[0]
    f0 = M_msun * MSUN_S * f_ini_hz
    x_i = (np.pi * f0) ** (2 / 3)
    eta = q / (1 + q) ** 2
    c_osc, c_full = B.calculadoras()
    Losc = B.lista_osc()
    H = np.stack([h[k] for k in Losc], axis=1)
    if nivel == "A":
        calc = c_osc
    elif nivel == "C":
        H = np.concatenate([H, np.stack([h[k] for k in B.MODOS_M0], axis=1)], axis=1)
        calc = c_full
    else:
        raise ValueError("nivel deve ser 'A' ou 'C'")
    Hd = derivada(H, dtt, ordem_deriv)
    w = pesos_janela(t, t_i)
    m = calc.memorias_gram(*gram_pesos(H, Hd, w))
    del H, Hd
    E_jan = float(m["energia_total"])
    E_l = float(e_lig(x_i, q, chi1, chi2, ordem_elig))
    Mf = 1.0 - E_jan - E_l
    P = B.momento_irradiado(m["energia_modos"])
    out = _restringir(m, todos_m)
    if nivel == "C":
        for l in (2, 4):
            fim = complex(h[(l, 0)][-1])
            out["deslocamento"][(l, 0)] = fim if desl == "total" else fim - complex(_interp_em(t, h[(l, 0)], t_i))
        S30 = complex(np.sum(w * h[(3, 0)]))
        for k in out["spin"]:
            if k[1] == 0:
                out["spin"][k] = S30 if k == (3, 0) else 0j
        spin_pot30 = 2j * S30 / ethb2_de_escalar(3)            # h^B = -(i/2) ethb^2 Psi
        out["giroscopica"][(3, 0)] = complex(-Dfrak(3) * spin_pot30 + 0.25 * m["helicidade_modos"][(3, 0)])
        for l in (5, 7):
            out["giroscopica"][(l, 0)] = complex(0.25 * m["helicidade_modos"][(l, 0)])
    elif desl == "total":
        out["deslocamento"][(2, 0)] += B.favata_h20(x_i, eta)
        out["deslocamento"][(4, 0)] += B.lrr_h40(x_i, eta)
    # CM: nula da janela (ja em out["cm"]) + ordinaria com o deslocamento escolhido
    for (l, mm), dJ in out["deslocamento"].items():
        if l >= 2:
            dPhi = 2 * dJ / ethb2_de_escalar(l)
            dK = -1.5 * Mf * dPhi / Dfrak(l)
            out["cm"][(l, mm)] = out["cm"].get((l, mm), 0j) + 0.5 * ethb2_de_escalar(l) * dK
    aux = dict(E_janela=E_jan, E_lig=E_l, M_f=Mf, P_rad=P, recuo=-P / Mf, t_i=float(t_i), x_i=x_i, eta=eta,
               f0=f0, nivel=nivel, desl=desl)
    return out, aux


# ------------------------------------------------------------------ observador
def no_observador_completo(mem, iota, phi):
    """As quatro memorias adimensionais no observador (iota, phi), somando todos os (l, m) presentes.

    Convencoes de binarias.no_observador: spin = -Im, demais = Re; s = 0 (giroscopica) ou -2 (demais).
    deslocamento: r Delta h_+ / M ; spin: r int h_x du / M^2 ; CM: Delta K no observador (r/M^2) ;
    giroscopica: r^2 Phi / M^2. phi: azimute a partir da fase orbital zerada em t_i (gerar_janela).
    """
    vals = {}
    for tipo in TIPOS:
        s = 0 if tipo == "giroscopica" else -2
        z = sum(c * complex(sYlm(s, l, m, iota, phi)) for (l, m), c in mem[tipo].items())
        vals[tipo] = float(-np.imag(z)) if tipo == "spin" else float(np.real(z))
    return vals


def valores_fisicos_completo(mem, iota, phi, M_msun, D_mpc):
    """Como binarias.valores_fisicos, com todos os (l, m): deslocamento adimensional, spin e CM em s, giro em rad."""
    M, D = M_msun * MSUN_S, D_mpc * MPC_S
    v = no_observador_completo(mem, iota, phi)
    return {"deslocamento": v["deslocamento"] * M / D, "spin": v["spin"] * M * M / D,
            "cm": v["cm"] * M * M / D, "giroscopica": v["giroscopica"] * (M / D) ** 2}


# ------------------------------------------------------------------ serie temporal da memoria
def _lista_saida(todos_m, tipo):
    if tipo == "rn":
        return list(B.MODOS_M0)
    if todos_m:
        return [(l, m) for l in range(2, LMAX + 1) for m in range(-l, l + 1)]
    return [(l, 0) for l in range(2, LMAX + 1)]


def serie_memoria(t, h, t_i, iota, phi, M_msun, D_mpc, tipo="nula", todos_m=False, magnetica=False,
                  ordem_deriv=8, bloco=2048):
    """Serie h_+ - i h_x da memoria de deslocamento no observador, unidades fisicas, desde t_i.

    tipo 'nula': memoria nula pelo fluxo de energia dos modos oscilatorios (nivel A), integrada no tempo com a
                 mesma quadratura de pesos_janela (o valor final e o deslocamento de janela de
                 memorias_observaveis); multipolos m = 0 (ou todos, com todos_m) de l = 2..8. Com
                 magnetica=True soma a parte magnetica instantanea h^B(u), sem subtrair o valor em t_i (nao e
                 acumulada; sua integral de t_i ao fim e a memoria de spin da janela; s(t_i) = h^B(t_i)).
    tipo 'rn'  : modos (2,0), (3,0), (4,0) do substituto menos o valor em t_i (interpolado): inclui o toque
                 quase normal dos modos m = 0, que nao e memoria.
    Devolve (t_s, s): t_s em segundos (t = 0 no pico do (2,2)), comecando em t_i; s complexo (deformacao).
    """
    Ms, Ds = M_msun * MSUN_S, D_mpc * MPC_S
    k = int(np.searchsorted(t, t_i, side="left"))
    dtt = t[1] - t[0]
    lista = _lista_saida(todos_m, tipo)
    Y = np.array([complex(sYlm(-2, l, m, iota, phi)) for (l, m) in lista])
    if tipo == "rn":
        modos = np.stack([h[kk] for kk in lista], axis=1)
        v0 = np.array([_interp_em(t, h[kk], t_i) for kk in lista])
        S = np.concatenate([np.zeros((1, len(lista)), dtype=complex), modos[k:] - v0[None, :]])
    elif tipo == "nula":
        c_osc = B.calculadoras()[0]
        Losc = B.lista_osc()
        H = np.stack([h[kk] for kk in Losc], axis=1)
        Hd = derivada(H, dtt, ordem_deriv)
        H, Hd = H[k - 1:], Hd[k - 1:]
        n = H.shape[0]
        R = np.zeros((n, len(lista)), dtype=complex)
        HB = np.zeros_like(R) if magnetica else None
        for i in range(0, n, bloco):
            hB, _, dm = c_osc.partes_instantaneas(H[i:i + bloco], Hd[i:i + bloco], lista)
            R[i:i + bloco] = dm
            if magnetica:
                HB[i:i + bloco] = hB
        del H, Hd
        a = (t_i - t[k - 1]) / dtt
        L = t[k] - t_i
        acum = np.zeros((n, len(lista)), dtype=complex)    # acum[j] = integral de t_i a t[k - 1 + j], j >= 1
        acum[1] = 0.5 * L * ((1 - a) * R[0] + (1 + a) * R[1])
        acum[2:] = acum[1] + np.cumsum(0.5 * dtt * (R[1:-1] + R[2:]), axis=0)
        S = acum.copy()
        S[0] = 0.0
        if magnetica:                                      # instantanea: nao se subtrai o valor em t_i
            S[0] = (1 - a) * HB[0] + a * HB[1]
            S[1:] += HB[1:]
        del R
    else:
        raise ValueError("tipo deve ser 'nula' ou 'rn'")
    ts = np.concatenate([[t_i], t[k:]])
    return ts * Ms, (S @ Y) * Ms / Ds


# ------------------------------------------------------------------ produto interno, match e SNR
_psd_cache = {}


def _psd(nome, n, df, fmin):
    chave = (nome, n, round(df, 15), fmin)
    if chave not in _psd_cache:
        _psd_cache.clear()
        _psd_cache[chave] = psd_serie(nome, n, df, fmin)
    return _psd_cache[chave]


def _inicio_serie(t):
    """Rotulo de tempo da primeira amostra que preparar produz (descarta t[0] se coincidir com t[1])."""
    if len(t) > 2 and t[1] - t[0] < 1e-9 * (t[2] - t[1]):
        return float(t[1])
    return float(t[0])


def preparar(t, h, fs=4096.0, taper=0.5, fim="rampa", t_hold=4.0, t_rampa=8.0):
    """Serie complexa na grade t[0] + j/fs, reamostrada por spline cubica, com tratamento.

    (Verificacao L00: a subtracao do instante do pico de |h| nao muda as amostras; a amostra j esta no rotulo
    t[0] + j/fs, ou t[1] + j/fs se t[0] coincidir com t[1]. Ver _inicio_serie e comparar2.)
    fim='rampa': subtrai o valor inicial, mantem o valor final por t_hold s e leva a zero por um cosseno de
    t_rampa s (sem degrau artificial no fim; so potencia abaixo de ~0.1 Hz). fim='nada': sem tratamento.
    taper: meia janela de Tukey (cosseno) nos primeiros taper segundos.
    """
    from scipy.interpolate import CubicSpline
    dt = 1.0 / fs
    tt = t - t[np.argmax(np.abs(h))]
    if len(tt) > 2 and tt[1] - tt[0] < 1e-9 * (tt[2] - tt[1]):      # t_i coincide com um ponto da rede
        tt, h = tt[1:], h[1:]
    tg = np.arange(tt[0], tt[-1], dt)
    x = CubicSpline(tt, h.real)(tg) + 1j * CubicSpline(tt, h.imag)(tg)
    if fim == "rampa":
        x = x - x[0]
        n_hold, n_rampa = int(t_hold / dt), int(t_rampa / dt)
        rampa = x[-1] * 0.5 * (1 + np.cos(np.pi * np.arange(n_rampa) / n_rampa))
        x = np.concatenate([x, np.full(n_hold, x[-1]), rampa])
    elif fim != "nada":
        raise ValueError("fim deve ser 'rampa' ou 'nada'")
    if taper > 0:
        n = int(taper / dt)
        wj = np.ones(len(x))
        wj[:n] = 0.5 * (1 - np.cos(np.pi * np.arange(n) / n))
        x = x * wj
    return x


def produto2(a_t, b_t, dt, nome_psd, fmin, up=16, refinar=True):
    """(a|a), (b|b), match e atraso tau (s) para h_+ (parte real), maximizado na fase e no tempo.

    tau maximiza |(a | b(. - tau))| com os tempos contados da primeira amostra de cada serie: a(t) ~ b(t - tau).
    Busca no tempo: transformada inversa do espectro cruzado com zero padding (resolucao dt/up) e depois
    maximizacao continua de |sum_f c(f) exp(2 pi i f tau)| num intervalo de +-dt/up em torno do maximo.
    """
    from scipy.optimize import minimize_scalar
    n = 1
    while n < 2 * max(len(a_t), len(b_t)):
        n *= 2
    A = np.fft.rfft(a_t.real, n) * dt
    Bf = np.fft.rfft(b_t.real, n) * dt
    f = np.fft.rfftfreq(n, dt)
    ok = f >= fmin
    df = f[1] - f[0]
    Sn = _psd(nome_psd, len(f), df, fmin)
    aa = 4 * np.sum(np.abs(A[ok]) ** 2 / Sn[ok]) * df
    bb = 4 * np.sum(np.abs(Bf[ok]) ** 2 / Sn[ok]) * df
    c = np.where(ok, A * np.conj(Bf) / Sn, 0) * 4 * df
    N = n * up
    integrando = np.zeros(N, dtype=complex)
    integrando[:len(f)] = c
    serie = np.abs(np.fft.ifft(integrando) * N)
    j = int(np.argmax(serie))
    tau = j * dt / up
    melhor = serie[j]
    if refinar:
        fo, co = f[ok], c[ok]

        def menos(tau_):
            return -np.abs(np.sum(co * np.exp(2j * np.pi * fo * tau_)))

        r = minimize_scalar(menos, bounds=(tau - dt / up, tau + dt / up), method="bounded",
                            options=dict(xatol=1e-6 * dt / up))
        if -r.fun > melhor:
            melhor, tau = -r.fun, float(r.x)
    if tau > 0.5 * n * dt:
        tau -= n * dt
    return aa, bb, float(melhor / np.sqrt(aa * bb)), tau


def comparar2(tA, hA, tB, hB, nome_psd, fmin, fs=4096.0, up=16, taper=0.5, fim="rampa"):
    """Match (h_+, maximizado em tempo e fase) e SNRs de A e B, com o tratamento de preparar.

    Devolve dict: match, snr_A, snr_B, r = snr_B/snr_A, rho_crit = 1/sqrt(1 + r^2 - 2 r match) (SNR de A em
    que (dh|dh) = 1 mantendo r; criterio de Lindblom et al. 2008 sem supor normas iguais), dd = (dh|dh) na
    SNR real, e dois atrasos (s):
      atraso         tau de produto2, contado entre as PRIMEIRAS amostras das series preparadas (a(t) ~ b(t - tau));
                     nao e relativo ao alinhamento pelos picos (correcao da verificacao L00: a docstring antiga dizia
                     isso, o que so vale quando A e B comecam no mesmo instante relativo ao pico);
      atraso_rotulos delta tal que B(t) ~ A(t - delta) nos rotulos de tempo dados (B atrasado de delta em relacao a A):
                     delta = (inicio de B - inicio de A) - tau.
    """
    dt = 1.0 / fs
    a = preparar(tA, hA, fs, taper, fim)
    b = preparar(tB, hB, fs, taper, fim)
    aa, bb, mt, tau = produto2(a, b, dt, nome_psd, fmin, up=up)
    rA, rB = np.sqrt(aa), np.sqrt(bb)
    r = rB / rA
    return dict(match=mt, snr_A=rA, snr_B=rB, r=r,
                rho_crit=1 / np.sqrt(max(1 + r * r - 2 * r * mt, 1e-300)),
                dd=rA ** 2 + rB ** 2 - 2 * rA * rB * mt, atraso=tau,
                atraso_rotulos=(_inicio_serie(tB) - _inicio_serie(tA)) - tau)


def snr2(t, h, nome_psd, fmin, fs=4096.0, taper=0.5, fim="rampa"):
    """SNR otima de h_+ (detector otimo para +), com o tratamento de preparar."""
    dt = 1.0 / fs
    x = preparar(t, h, fs, taper, fim)
    n = 1
    while n < 2 * len(x):
        n *= 2
    X = np.fft.rfft(x.real, n) * dt
    f = np.fft.rfftfreq(n, dt)
    ok = f >= fmin
    df = f[1] - f[0]
    Sn = _psd(nome_psd, len(f), df, fmin)
    return float(np.sqrt(4 * np.sum(np.abs(X[ok]) ** 2 / Sn[ok]) * df))
