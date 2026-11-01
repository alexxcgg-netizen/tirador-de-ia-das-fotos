"""Funcoes comuns das linhas L01, L02 e L18 (agente D1): memorias de muitas janelas a partir de UMA onda.

Base: codigo/observaveis.py (L00). Para (q, chi1, chi2) fixos a onda adimensional nao depende de M; M so muda o
instante inicial da janela t_i (f_22 = f_ini, f0 = M MSUN_S f_ini). Por isso uma onda gerada desde o menor f0
(rede fixa, como observaveis.gerar_janela) da as memorias de qualquer M maior. As matrizes de Gram de cada janela
sao somas de cauda (uma passagem pela onda) mais o subintervalo parcial de observaveis.pesos_janela; depois
memorias_gram (5 ms) e o pos-processamento de observaveis.memorias_observaveis (nivel A, desl='janela', CM com o
mesmo deslocamento, M_f com E_lig 3PN+SO).

Referenciais de fase dos multipolos m != 0 (rotacao em torno do eixo orbital, X_lm -> X_lm exp(-i m alpha)):
  'ti'   : fase orbital zerada em t_i (convencao de observaveis.gerar_janela; phi do observador medido dai);
  'pico' : fase orbital zerada no pico (t = 0); phi' = phi - Phi_orb(0). Reparametrizacao (lambda, phi) ->
           (lambda, phi') e um difeomorfismo: posto e dimensao das fibras nao mudam, e o termo de borda final
           (fusao) fica suave nos parametros (no referencial 'ti' ele gira ~ 450 rad por unidade de ln M).
Termo de borda inicial dos m != 0: a integral de t_i de um integrando ~ exp(-i m psi) deixa um termo
oscilatorio em t_i (artefato da janela abrupta; e parte da onda oscilatoria, nao memoria). Com media=True os
multipolos m != 0 sao a media (janela de Hann) sobre inicios t_s em [t_i, t_i + n_orb periodos orbitais], o que
o suprime; os m = 0, E_janela e M_f sao sempre os da janela que comeca em t_i.

q < 1: pela simetria de troca, (q, chi1, chi2) = (1/q, chi2, chi1) girado de pi (corpo 1 no eixo +x).
Nao guarda formas de onda: cada chamada devolve so os multipolos (dicts pequenos).
"""
import numpy as np

import binarias as B
import observaveis as O
from deteccao import MSUN_S, MPC_S
from harmonicos import sYlm, Dfrak, ethb2_de_escalar

TIPOS = B.TIPOS
S_TIPO = {"deslocamento": -2, "spin": -2, "cm": -2, "giroscopica": 0}
ESCALA_D = {"deslocamento": 1, "spin": 1, "cm": 1, "giroscopica": 2}      # potencia de 1/D
ESCALA_M = {"deslocamento": 1, "spin": 2, "cm": 2, "giroscopica": 2}      # potencia de M (fisico)


def f0_de(M_msun, f_ini=10.0):
    return M_msun * MSUN_S * f_ini


# ------------------------------------------------------------------ onda base
_surs = {}


def _sur_modelo(nome):
    if nome == "NRHybSur3dq8_CCE":
        return B._sur()
    if nome not in _surs:
        import gwsurrogate
        _surs[nome] = gwsurrogate.LoadSurrogate(nome)
    return _surs[nome]


def gerar_base(q, chi1, chi2, f0_min, dt=0.25, modelo="NRHybSur3dq8_CCE"):
    """Onda na rede fixa t_k = k dt desde 0.9 f0_min, f_ref = f0_min. Devolve (t, h, fase, troca).

    fase: fase desenrolada de h22 (-2 x fase orbital + cte), derivada de 8a ordem como observaveis.
    Para q < 1 gera (1/q, chi2, chi1) e gira de pi (h_lm -> (-1)^m h_lm): corpo 1 no eixo +x.
    """
    troca = q < 1
    if troca:
        q, chi1, chi2 = 1.0 / q, chi2, chi1
    f_low = O.FRAC_INICIO * f0_min
    sur = _sur_modelo(modelo)
    cA, cB = [0.0, 0.0, chi1], [0.0, 0.0, chi2]
    t1, _, _ = sur(q, cA, cB, dt=dt, f_low=f_low, mode_list=[(2, 2)])
    k0 = int(np.ceil(t1[0] / dt)) + 1
    k1 = int(np.floor(t1[-1] / dt))
    tt = np.arange(k0, k1 + 1) * dt
    del t1
    t, h, _ = sur(q, cA, cB, times=tt, f_low=f_low, f_ref=f0_min)
    h = {(int(l), int(m)): np.asarray(v) for (l, m), v in h.items()}
    if troca:
        for k in h:
            if k[1] % 2:
                h[k] = -h[k]
    t = np.asarray(t)
    fase = np.unwrap(np.angle(h[(2, 2)]))
    return t, h, fase, troca


def _instante(t, w22, f0):
    """t_i com omega_22 = 2 pi f0 (interpolacao linear, antes do pico), como observaveis.instante_frequencia."""
    w0 = 2 * np.pi * f0
    ate = np.nonzero(t <= 0)[0]
    acima = ate[w22[ate] >= w0]
    if len(acima) == 0 or acima[0] == 0:
        raise ValueError("f0 fora do trecho gerado")
    k = int(acima[0])
    return float(t[k - 1] + (w0 - w22[k - 1]) / (w22[k] - w22[k - 1]) * (t[k] - t[k - 1])), k


def _fase_em(t, fase, ti, k):
    idx = np.arange(k - 2, k + 2)
    return float(np.polyval(np.polyfit(t[idx] - ti, fase[idx], 3), 0.0))


class Grams:
    """Somas de cauda das matrizes de Gram (B = sum w hdot hdot^+, A = sum w h hdot^+) para muitos t_i."""

    def __init__(self, t, H, Hd):
        self.t, self.H, self.Hd = t, H, Hd
        self.dt = t[1] - t[0]
        self.N = len(t)
        self._cauda = {}            # k -> (B, A) de dt*sum_{j=k+1}^{N-2} X_j + dt/2 X_{N-1}

    def preparar(self, lista_k):
        ks = sorted(set(int(k) for k in lista_k), reverse=True)
        N, dt, H, Hd = self.N, self.dt, self.H, self.Hd
        Bc = 0.5 * dt * np.outer(Hd[N - 1], Hd[N - 1].conj())
        Ac = 0.5 * dt * np.outer(H[N - 1], Hd[N - 1].conj())
        fim = N - 2                        # proximo indice ainda nao somado (inclusive)
        for k in ks:
            if k + 1 <= fim:
                seg = slice(k + 1, fim + 1)
                Bc = Bc + dt * (Hd[seg].T @ Hd[seg].conj())
                Ac = Ac + dt * (H[seg].T @ Hd[seg].conj())
                fim = k
            self._cauda[k] = (Bc.copy(), Ac.copy())

    def gram(self, ti):
        t, dt = self.t, self.dt
        k = int(np.searchsorted(t, ti, side="left"))
        a = (ti - t[k - 1]) / dt
        L = t[k] - ti
        w0, w1 = 0.5 * L * (1 - a), 0.5 * L * (1 + a) + 0.5 * dt
        Bc, Ac = self._cauda[k]
        H, Hd = self.H, self.Hd
        Bm = Bc + w0 * np.outer(Hd[k - 1], Hd[k - 1].conj()) + w1 * np.outer(Hd[k], Hd[k].conj())
        Am = Ac + w0 * np.outer(H[k - 1], Hd[k - 1].conj()) + w1 * np.outer(H[k], Hd[k].conj())
        return Bm, Am


def _girar(mem, alpha):
    """Rotacao de alpha em torno do eixo orbital: X_lm -> X_lm exp(-i m alpha)."""
    return {tipo: {k: v * np.exp(-1j * k[1] * alpha) for k, v in mem[tipo].items()} for tipo in mem}


def _pos(m, Mf, lmax):
    """Restringe a l <= lmax e soma a parte ordinaria da CM com o deslocamento de janela (como observaveis)."""
    out = {tipo: {k: complex(v) for k, v in m[tipo].items() if k[0] <= lmax} for tipo in TIPOS}
    for (l, mm), dJ in out["deslocamento"].items():
        if l >= 2:
            dPhi = 2 * dJ / ethb2_de_escalar(l)
            dK = -1.5 * Mf * dPhi / Dfrak(l)
            out["cm"][(l, mm)] = out["cm"].get((l, mm), 0j) + 0.5 * ethb2_de_escalar(l) * dK
    return out


def memorias_varias(q, chi1, chi2, lista_M, f_ini=10.0, dt=0.25, lmax=8, media=True, n_orb=3.0, n_media=128,
                    modos=None, modelo="NRHybSur3dq8_CCE"):
    """Memorias de janela (nivel A, desl='janela', todos os m) para varios M de uma so onda.

    Devolve lista de dicts (um por M): mem_ti (referencial 'ti', janela abrupta: igual a
    observaveis.memorias_observaveis(..., todos_m=True)), mem_pico (referencial 'pico', m != 0 com media sobre o
    inicio se media=True), aux (E_janela, E_lig, M_f, t_i, x_i, eta, f0, Phi_pico = fase orbital do pico menos a de
    t_i, borda = |m != 0 abrupto - medio| relativo por tipo).
    modos: lista de modos oscilatorios (padrao: binarias.lista_osc()); outra lista usa uma calculadora propria.
    """
    lista_M = list(lista_M)
    f0s = [f0_de(M, f_ini) for M in lista_M]
    t, h, fase, _ = gerar_base(q, chi1, chi2, min(f0s), dt, modelo)
    w22 = -O.derivada(fase, dt, ordem=8)
    if modos is None:
        Losc = B.lista_osc()
        calc = B.calculadoras()[0]
    else:
        Losc = list(modos)
        calc = _calc(tuple(Losc))
    H = np.stack([h[k] for k in Losc], axis=1)
    k_pico = int(np.argmin(np.abs(t)))
    fase_pico = fase[k_pico]
    del h
    Hd = O.derivada(H, dt, 8)
    G = Grams(t, H, Hd)
    eta = q / (1 + q) ** 2
    infos = []
    ks = []
    for f0 in f0s:
        ti, k = _instante(t, w22, f0)
        fti = _fase_em(t, fase, ti, k)
        Torb = 2 * np.pi / (np.pi * f0)            # periodo orbital em t_i (omega_orb = pi f0)
        if media:
            u = (np.arange(n_media) + 0.5) / n_media
            pes = np.sin(np.pi * u) ** 2
            pes /= pes.sum()
            tss = ti + u * n_orb * Torb
        else:
            tss, pes = np.array([ti]), np.array([1.0])
        infos.append((f0, ti, fti, tss, pes))
        ks.append(int(np.searchsorted(t, ti, side="left")))
        ks += [int(np.searchsorted(t, x, side="left")) for x in tss]
    G.preparar(ks)
    # fase orbital continua ancorada na convencao do gwsurrogate em f_ref = f0_min (fase de h22 ~ 0 e corpo
    # mais pesado em +x no ponto da rede mais proximo; observaveis.gerar_janela usa o valor enrolado ali):
    # fase_c(t) = fase(t) - fase(t_ref) + wrap(fase(t_ref)), t_ref = t_i da janela de f0_min.
    j_ref = int(np.argmin(f0s))
    f_ref = infos[j_ref][2]
    corr = -f_ref + float(np.angle(np.exp(1j * f_ref)))
    saida = []
    for (M, (f0, ti, fti, tss, pes)) in zip(lista_M, infos):
        x_i = (np.pi * f0) ** (2 / 3)
        m = calc.memorias_gram(*G.gram(ti))
        E_jan = float(m["energia_total"])
        E_l = float(O.e_lig(x_i, q, chi1, chi2, 3))
        Mf = 1.0 - E_jan - E_l
        mem_g = _pos(m, Mf, lmax)                      # referencial de geracao
        Bm = sum(p * G.gram(x)[0] for p, x in zip(pes, tss))
        Am = sum(p * G.gram(x)[1] for p, x in zip(pes, tss))
        mm = _pos(calc.memorias_gram(Bm, Am), Mf, lmax)
        # referenciais: rotacao alpha = -Phi_orb(ref) = fase(ref)/2 (h_lm -> h_lm exp(-i m fase/2), como gerar_janela)
        a_ti = 0.5 * (fti + corr)
        a_pk = 0.5 * (fase_pico + corr)
        mem_ti = _girar(mem_g, a_ti)
        pk_abr = _girar(mem_g, a_pk)
        pk_med = _girar(mm, a_pk)
        mem_pico = {tipo: {k: (pk_abr[tipo][k] if k[1] == 0 else pk_med[tipo][k]) for k in pk_abr[tipo]}
                    for tipo in TIPOS}
        borda = {}
        for tipo in TIPOS:
            ref = max(abs(v) for k, v in pk_abr[tipo].items() if k[1] == 0)
            borda[tipo] = max(abs(pk_abr[tipo][k] - pk_med[tipo][k]) for k in pk_abr[tipo] if k[1] != 0) / ref
        aux = dict(E_janela=E_jan, E_lig=E_l, M_f=Mf, t_i=ti, x_i=x_i, eta=eta, f0=f0,
                   Phi_pico=-0.5 * (fase_pico - fti), borda=borda, M=M)
        saida.append(dict(mem_ti=mem_ti, mem_pico=mem_pico, aux=aux))
    del G, H, Hd
    return saida


_calcs = {}


def _calc(L):
    if L not in _calcs:
        from memorias import CalculadoraMemoria
        _calcs[L] = CalculadoraMemoria(list(L), lmax_saida=11)
    return _calcs[L]


# ------------------------------------------------------------------ observador
def so_m0(mem):
    return {tipo: {k: v for k, v in mem[tipo].items() if k[1] == 0} for tipo in mem}


def adim(mem, iota, phi):
    """Quatro memorias adimensionais no observador (convencoes de observaveis.no_observador_completo)."""
    return O.no_observador_completo(mem, iota, phi)


def fisicos(mem, iota, phi, M, D):
    return O.valores_fisicos_completo(mem, iota, phi, M, D)


def vetor_fisico(mem, iota, phi, M, D, tipos=TIPOS):
    v = fisicos(mem, iota, phi, M, D)
    return np.array([v[k] for k in tipos])


def tabela_Y(mem, tipos=TIPOS):
    """Lista de (tipo, l, m, coef) para projecao rapida."""
    return [(tipo, l, m, c) for tipo in tipos for (l, m), c in mem[tipo].items()]


def projetar(mem, iota, phi, tipos=TIPOS):
    """Como adim, mas devolve tambem d/dphi (analitico) e d/diota (diferenca central de passo 1e-6)."""
    out, dphi, dio = [], [], []
    e = 1e-6
    for tipo in tipos:
        s = S_TIPO[tipo]
        z = zp = zi1 = zi0 = 0j
        for (l, m), c in mem[tipo].items():
            y = complex(sYlm(s, l, m, iota, phi))
            z += c * y
            zp += 1j * m * c * y
            zi1 += c * complex(sYlm(s, l, m, iota + e, phi))
            zi0 += c * complex(sYlm(s, l, m, iota - e, phi))
        f = (lambda w: float(-np.imag(w))) if tipo == "spin" else (lambda w: float(np.real(w)))
        out.append(f(z))
        dphi.append(f(zp))
        dio.append((f(zi1) - f(zi0)) / (2 * e))
    return np.array(out), np.array(dphi), np.array(dio)


def escala_fisica(M, D, tipos=TIPOS):
    Ms, Ds = M * MSUN_S, D * MPC_S
    return np.array([Ms ** ESCALA_M[t] / Ds ** ESCALA_D[t] * (1.0 if t != "giroscopica" else 1.0) for t in tipos])
