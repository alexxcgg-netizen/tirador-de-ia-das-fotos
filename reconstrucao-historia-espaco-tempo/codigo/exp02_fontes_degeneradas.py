"""Experimento 2 (etapa 3): historias diferentes com as mesmas quatro memorias.

Fonte A: corpo girante que acelera (chirp), sem recuo, parte e termina em repouso.
Fonte B: A vista atraves de um filtro de fase comum que inverte a varredura do modo 22
         (anti-chirp: gira no mesmo sentido, mas desacelera).
Fonte C: duas explosoes de meia potencia, separadas por 2T (aproximado).
Fonte D: rotacao de dualidade constante de A (mistura momentos de massa e de corrente).
Fonte E: A atraves de um filtro de fase aleatorio e suave ("dispersao").

Para cada uma: as quatro memorias (partes nulas) no ceu inteiro, as matrizes de Gram,
e a sobreposicao (overlap) das formas de onda completas com a de A em varias direcoes.
Saidas: resultados/exp02_fontes_degeneradas.txt e figuras/e3_*.png
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from harmonicos import sYlm                                     # noqa: E402
from memorias import CalculadoraMemoria, gram, diferenca_relativa  # noqa: E402
import fontes as F                                               # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "resultados")
FIG = os.path.join(AQUI, "..", "figuras")
os.makedirs(RES, exist_ok=True)
os.makedirs(FIG, exist_ok=True)
linhas = []


def log(s=""):
    print(s)
    linhas.append(s)


u, du = F.grade_tempo()
HA, OmA = F.fonte_girante(u, du)
rng = np.random.default_rng(7)
HB = F.aplicar_fase(HA, F.fase_antichirp(len(u), du))
HC = F.dividir(HA, du, 2600.0)
HD = F.dualidade(HA, np.pi / 3)
HE = F.aplicar_fase(HA, F.fase_aleatoria(len(u), du, rng))
fontes = {"A chirp": HA, "B anti-chirp": HB, "C duas explosoes": HC,
          "D dualidade": HD, "E dispersao": HE}

# conferir que nada vazou para as bordas da janela (sinal periodico na FFT)
for nome, H in fontes.items():
    borda = np.max(np.abs(H[:2000])) + np.max(np.abs(H[-2000:]))
    log("%-18s amplitude max = %.3e   amplitude nas bordas = %.1e" % (nome, np.max(np.abs(H)), borda))

calc = CalculadoraMemoria(F.LISTA)
mem, grams = {}, {}
for nome, H in fontes.items():
    Hd = F.derivar(H, du, 1)
    mem[nome] = calc.memorias_tempo(H, Hd, du)
    grams[nome] = gram(H, Hd, du)

log()
log("Diferenca relativa das memorias em relacao a A (max sobre todos os modos l<=%d):" % calc.lmax)
log("%-18s %12s %12s %12s %12s | %10s %10s" % ("fonte", "deslocam.", "spin", "CM", "giroscop.", "|dB|/|B|", "|dOm|/|Om|"))
BA, AA = grams["A chirp"]
OmA_ = AA - AA.conj().T
for nome in fontes:
    d = diferenca_relativa(mem["A chirp"], mem[nome])
    B, A = grams[nome]
    Om = A - A.conj().T
    log("%-18s %12.2e %12.2e %12.2e %12.2e | %10.2e %10.2e" % (
        nome, d["deslocamento"], d["spin"], d["cm"], d["giroscopica"],
        np.abs(B - BA).max() / np.abs(BA).max(), np.abs(Om - OmA_).max() / np.abs(OmA_).max()))

mA = mem["A chirp"]
log()
log("Valores de referencia (fonte A), unidades G=c=1, h = r x deformacao, M = 1:")
for tipo in ("deslocamento", "spin", "cm", "giroscopica"):
    top = sorted(mA[tipo].items(), key=lambda kv: -abs(kv[1]))[:4]
    log("  %-13s " % tipo + "  ".join("(%d,%d): %.3e%+.3ej" % (l, m, c.real, c.imag) for (l, m), c in top))
log("  energia irradiada = %.5e" % mA["energia_total"])


# ---------- formas de onda: sobreposicao maximizada em deslocamento temporal e fase ----------
def campo(H, th, ph):
    return H @ np.array([sYlm(-2, l, m, th, ph) for (l, m) in F.LISTA])


def overlap(a, b, fase_livre=True):
    """max_tau |<a, b(.+tau)>| / (|a||b|), produto interno de ruido branco nas duas polarizacoes.

    Com fase_livre=False usa Re<a,b> (sem girar a polarizacao): e o que separa a fonte D.
    """
    fa, fb = np.fft.fft(a), np.fft.fft(b)
    xc = np.fft.ifft(fa * np.conj(fb))
    v = np.abs(xc) if fase_livre else xc.real
    return np.max(v) / np.sqrt(np.sum(np.abs(a) ** 2) * np.sum(np.abs(b) ** 2))


direcoes = [(np.pi / 6, 0.0), (np.pi / 3, 1.0), (np.pi / 2, 2.0), (2 * np.pi / 3, 4.0)]
log()
log("Sobreposicao da forma de onda completa com A (1 = identica), maximizada em tempo e fase:")
log("%-18s " % "fonte" + " ".join("th=%3.0f" % np.degrees(t) for t, _ in direcoes))
for nome, H in fontes.items():
    ov = [overlap(campo(HA, t, p), campo(H, t, p)) for t, p in direcoes]
    ov2 = [overlap(campo(HA, t, p), campo(H, t, p), False) for t, p in direcoes]
    log("%-18s " % nome + " ".join("%6.3f" % o for o in ov) + "   | sem girar a polarizacao: "
        + " ".join("%6.3f" % o for o in ov2))


# ---------- historias: perfil temporal da potencia irradiada ----------
def potencia(H):
    Hd = F.derivar(H, du, 1)
    return np.sum(np.abs(Hd) ** 2, axis=1) / (16 * np.pi)


log()
log("Perfil temporal da potencia irradiada (a historia que a memoria nao ve):")
for nome, H in fontes.items():
    P = potencia(H)
    E = np.sum(P) * du
    uc = np.sum(u * P) * du / E
    sig = np.sqrt(np.sum((u - uc) ** 2 * P) * du / E)
    log("  %-18s energia = %.5e  centroide u = %8.1f  largura = %7.1f  pico = %.3e" % (nome, E, uc, sig, P.max()))

with open(os.path.join(RES, "exp02_fontes_degeneradas.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")

_SALVAR_NPZ = False
if _SALVAR_NPZ:
  np.savez_compressed(os.path.join(RES, "exp02_dados.npz"), u=u[::8], **{
    k.split()[0]: campo(H, np.pi / 3, 1.0)[::8] for k, H in fontes.items()})

# ---------- figuras ----------
import matplotlib                                                  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                    # noqa: E402

SUP, TXT, TXT2 = "#fcfcfb", "#0b0b0b", "#52514e"
AZUL, LARANJA, VERDE = "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"figure.facecolor": SUP, "axes.facecolor": SUP, "axes.edgecolor": "#c9c8c2",
                     "axes.labelcolor": TXT2, "xtick.color": TXT2, "ytick.color": TXT2,
                     "text.color": TXT, "font.size": 9, "axes.grid": True, "grid.color": "#e6e5e0",
                     "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False})

th0, ph0 = np.pi / 3, 1.0
TITULOS = {"A chirp": "A — chirp (gira acelerando)", "B anti-chirp": "B — anti-chirp (mesmo sentido, desacelerando)",
           "C duas explosoes": "C — duas explosões de meia potência",
           "D dualidade": "D — rotação de dualidade (mistura momentos de massa e de corrente)",
           "E dispersao": "E — A atravessando um filtro de fase aleatório"}
Ydir = np.array([sYlm(-2, l, m, th0, ph0) for (l, m) in F.LISTA])
memdir = {}
nomes = list(fontes)
fig, ax = plt.subplots(len(nomes), 2, figsize=(10, 9.5), sharex="col",
                       gridspec_kw={"width_ratios": [2.2, 1]})
for i, nome in enumerate(nomes):
    H = fontes[nome]
    h = H @ Ydir
    ax[i, 0].plot(u, h.real, color=AZUL, lw=0.8)
    ax[i, 0].set_ylabel("r h+", fontsize=8)
    ax[i, 0].set_title(TITULOS[nome], loc="left", fontsize=9, color=TXT)
    # memoria nula acumulada nessa direcao: modos dmem integrados
    _, _, dmem = calc.partes_instantaneas(H, F.derivar(H, du, 1),
                                          [(l, 0) for l in (2, 4, 6)] + [(4, 4), (4, -4), (6, 4), (6, -4)])
    lista_m = [(l, 0) for l in (2, 4, 6)] + [(4, 4), (4, -4), (6, 4), (6, -4)]
    Ym = np.array([sYlm(-2, l, m, th0, ph0) for (l, m) in lista_m])
    acum = np.cumsum(dmem @ Ym) * du
    ax[i, 1].plot(u, acum.real, color=LARANJA, lw=1.6)
    ax[i, 1].set_ylabel("memória r h+", fontsize=8)
    ax[i, 1].axhline(acum.real[-1], color=TXT2, lw=0.6, ls=":")
    ax[i, 1].text(u[-1], acum.real[-1], " %.4f" % acum.real[-1], va="bottom", ha="right", fontsize=7, color=TXT2)
ax[-1, 0].set_xlabel("tempo retardado u (unidades de M)")
ax[-1, 1].set_xlabel("u")
for a in ax[:, 0]:
    a.set_xlim(-5200, 5200)
fig.suptitle("Cinco histórias, mesma memória final (direção θ = 60°)", x=0.01, ha="left", fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "e3_formas_de_onda.png"), dpi=140)
plt.close(fig)

# mapas no ceu: A, E e diferenca, para os quatro tipos
TH = np.linspace(0.02, np.pi - 0.02, 90)
PH = np.linspace(0, 2 * np.pi, 180)
TT, PP = np.meshgrid(TH, PH, indexing="ij")


def mapa(md, tipo):
    out = np.zeros(TT.shape, dtype=complex)
    s = 0 if tipo == "giroscopica" else -2
    for (l, m), c in md[tipo].items():
        if abs(c) > 0:
            out += c * sYlm(s, l, m, TT, PP)
    return out.real if tipo in ("deslocamento", "cm", "giroscopica") else -out.imag


rotulos = {"deslocamento": "deslocamento  r Δh+", "spin": "spin  r ∫h× du", "cm": "centro de massa  r ∫h+ du",
           "giroscopica": "giroscópica  r² Φ"}
fig, ax = plt.subplots(4, 3, figsize=(10, 9))
for i, tipo in enumerate(("deslocamento", "spin", "cm", "giroscopica")):
    a_ = mapa(mem["A chirp"], tipo)
    e_ = mapa(mem["E dispersao"], tipo)
    v = np.max(np.abs(a_))
    for j, (dados, tit) in enumerate(((a_, "A (chirp)"), (e_, "E (dispersão)"))):
        im = ax[i, j].pcolormesh(np.degrees(PP), np.degrees(TT), dados, cmap="RdBu_r", vmin=-v, vmax=v, shading="auto")
        ax[i, j].set_title("%s — %s" % (rotulos[tipo], tit), fontsize=8, loc="left")
        ax[i, j].invert_yaxis()
        ax[i, j].grid(False)
    fig.colorbar(im, ax=ax[i, 1], fraction=0.046)
    dif = (e_ - a_) / v
    im2 = ax[i, 2].pcolormesh(np.degrees(PP), np.degrees(TT), dif, cmap="RdBu_r",
                              vmin=-np.max(np.abs(dif)), vmax=np.max(np.abs(dif)), shading="auto")
    ax[i, 2].set_title("(E − A)/max|A|  (máx %.0e)" % np.max(np.abs(dif)), fontsize=8, loc="left")
    ax[i, 2].invert_yaxis()
    ax[i, 2].grid(False)
    fig.colorbar(im2, ax=ax[i, 2], fraction=0.046)
for a in ax[-1]:
    a.set_xlabel("φ (graus)")
for a in ax[:, 0]:
    a.set_ylabel("θ (graus)")
fig.suptitle("As quatro memórias no céu inteiro: duas histórias, mapas idênticos", x=0.01, ha="left", fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "e3_mapas_memoria.png"), dpi=130)
plt.close(fig)

# divisao em duas explosoes: residuo em funcao da separacao
seps = [300, 450, 600, 800, 1000, 1300, 1700, 2200, 2600]
res = []
for T in seps:
    HC_ = F.dividir(HA, du, T)
    mC = calc.memorias_tempo(HC_, F.derivar(HC_, du, 1), du)
    res.append(diferenca_relativa(mA, mC))
fig, ax = plt.subplots(figsize=(6.4, 3.6))
cores = {"deslocamento": AZUL, "spin": LARANJA, "cm": VERDE, "giroscopica": "#eda100"}
nomes_leg = {"deslocamento": "deslocamento", "spin": "spin", "cm": "centro de massa", "giroscopica": "giroscópica"}
for tipo, cor in cores.items():
    y = [r[tipo] for r in res]
    ax.semilogy(seps, y, color=cor, lw=2, marker="o", ms=4, label=nomes_leg[tipo])
ax.legend(frameon=False, fontsize=8, loc="upper right")
ax.set_xlabel("meia separação T entre as duas explosões (unidades de M)")
ax.set_ylabel("diferença relativa das memórias")
ax.set_title("C: duas explosões de meia potência → memórias de A quando não se sobrepõem", loc="left", fontsize=9)
ax.set_xlim(250, 2700)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "e3_divisao.png"), dpi=140)
plt.close(fig)
log()
log("Divisao em duas explosoes, diferenca relativa vs meia separacao T:")
for T, r in zip(seps, res):
    log("  T = %5d   deslocamento %.1e  spin %.1e  CM %.1e  giro %.1e" % (T, r["deslocamento"], r["spin"], r["cm"], r["giroscopica"]))
with open(os.path.join(RES, "exp02_fontes_degeneradas.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
