"""exp34 (L11) - figuras: padrao de memoria de deslocamento no ceu com linhas de polarizacao e zeros (e34_ceu.png);
angulos entre o eixo dos zeros e direcoes fisicas na populacao (e34_angulos.png). Usa exp34_populacao.npz."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import exp33_comum as C
import exp34_zeros as Z
import exp34_populacao as EP

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
AZ, LA, VE, TX = "#2a78d6", "#eb6834", "#1baf7a", "#52514e"


def estilo(a):
    a.set_facecolor("#fcfcfb")
    a.grid(color="#e6e5e0")
    a.tick_params(colors=TX)
    for s in a.spines.values():
        s.set_color(TX)


def painel(a, nome, centro, raio):
    """Projecao gnomonica em torno de `centro` (graus de raio): |h| e linhas de polarizacao, zeros e direcoes."""
    import surfinBH
    q, cA, cB = EP.NOMEADOS[nome]
    t, h, dyn = C.gerar7(q, cA, cB, f_ref=C.F0_PADRAO)
    ti = C.instante_orbital(t, dyn["orbphase"], C.F0_PADRAO)
    mem, aux = C.memorias7(q, t, h, dyn, ti)
    eQ, _, _ = EP.eixo_luminosidade(t, h, dyn, ti)
    del t, h, dyn
    fit = surfinBH.LoadFits("NRSur7dq4Remnant")
    chif = fit.chif(q, list(cA), list(cB), omega0=np.pi * C.F0_PADRAO, omega_switch_IG=0.5 * np.pi * C.F0_PADRAO,
                    allow_extrap=True)[0]
    D = mem["deslocamento"]
    _, lt = Z.indices_triangulos(D, nivel=6)
    zz = Z.zeros(D, extras=[c for c, _ in lt])
    if centro is None:
        _, _, centro = Z.eixos_opticos(EP.tensor_desl(mem))
        centro = centro if centro[2] > 0 else -centro
    c = centro / np.linalg.norm(centro)
    u, w = Z.base_tangente(c)
    r = np.tan(np.radians(raio))
    x = np.linspace(-r, r, 161)
    X, Y = np.meshgrid(x, x)
    n = c[None, :] + X.ravel()[:, None] * u[None, :] + Y.ravel()[:, None] * w[None, :]
    n /= np.linalg.norm(n, axis=1)[:, None]
    n = Z._girar_fora_do_polo(n)
    amp = np.abs(Z.campo_h(D, n)).reshape(X.shape)
    im = a.pcolormesh(np.degrees(np.arctan(X)), np.degrees(np.arctan(Y)), amp / amp.max(), cmap="Blues_r", shading="auto")
    xs = np.linspace(-r, r, 17)
    XS, YS = np.meshgrid(xs, xs)
    ns = c[None, :] + XS.ravel()[:, None] * u[None, :] + YS.ravel()[:, None] * w[None, :]
    ns /= np.linalg.norm(ns, axis=1)[:, None]
    zl = Z.z_local(D, Z._girar_fora_do_polo(ns), u, w)
    psi = 0.5 * np.angle(zl)
    L = 0.45 * (xs[1] - xs[0])
    for (px, py, p) in zip(XS.ravel(), YS.ravel(), psi):
        a.plot(np.degrees(np.arctan([px - L * np.cos(p), px + L * np.cos(p)])),
               np.degrees(np.arctan([py - L * np.sin(p), py + L * np.sin(p)])), color=TX, lw=0.7)

    def proj(v):
        v = np.asarray(v, float) / np.linalg.norm(v)
        if v @ c <= 0:
            return None
        p = v / (v @ c)
        return np.degrees(np.arctan(p @ u)), np.degrees(np.arctan(p @ w))
    for z in zz:
        pp = proj(z["n"])
        if pp is not None and max(abs(pp[0]), abs(pp[1])) < raio:
            a.plot(*pp, marker="o", ms=8, mfc=LA if z["indice"] > 0 else VE, mec="k")
    for rot, v, mk, cor in (("L_i", aux["Lhat_i"], "s", "w"), ("J_rad", aux["J_rad"], "^", AZ), ("chi_f", chif, "D", VE),
                             ("e_Q", eQ, "*", LA)):
        pp = proj(v)
        if pp is not None and max(abs(pp[0]), abs(pp[1])) < raio:
            a.plot(*pp, marker=mk, ms=9, mfc=cor, mec="k", ls="none", label=rot)
    a.set_xlim(-raio, raio)
    a.set_ylim(-raio, raio)
    a.set_aspect("equal")
    a.set_xlabel("graus (projecao gnomonica)", color=TX)
    a.set_title("%s: |Delta h|, linhas de polarizacao, zeros +1/2 (circulos)" % nome, color=TX, fontsize=9)
    a.legend(fontsize=7, loc="lower right")
    return im


def main():
    fig, ax = plt.subplots(1, 3, figsize=(15, 5))
    for a in ax:
        a.set_facecolor("#fcfcfb")
        a.tick_params(colors=TX)
    painel(ax[0], "AL1", np.array([0, 0, 1.0]), 6.0)
    im = painel(ax[1], "P3", None, 24.0)
    painel(ax[2], "P6", None, 30.0)
    fig.colorbar(im, ax=ax, shrink=0.8, label="|Delta h| / max")
    fig.savefig(os.path.join(RAIZ, "figuras", "e34_ceu.png"), dpi=130, facecolor="#fcfcfb")
    d = np.load(os.path.join(RAIZ, "resultados", "exp34_populacao.npz"))
    pop = np.array([str(n).startswith("R") for n in d["nomes"]])
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    for a in ax:
        estilo(a)
    chaves = [("e_Q", LA), ("J_rad", AZ), ("chi_f", VE), ("L_pico", "#9a9893"), ("L_i", TX)]
    bins = np.logspace(-2, 2, 33)
    for k, cor in chaves:
        ax[0].hist(d["ang_e1_" + k][pop], bins=bins, histtype="step", lw=1.8, color=cor, label=k)
    ax[0].set_xscale("log")
    ax[0].set_xlabel("angulo entre e1 (eixo dos pares de zeros) e a direcao (graus)", color=TX)
    ax[0].set_ylabel("numero de sistemas", color=TX)
    ax[0].legend(fontsize=8)
    ax[0].set_title("populacao NRSur7dq4 (%d sistemas)" % pop.sum(), color=TX, fontsize=10)
    ax[1].plot(d["a_Q"][pop], d["abert"][pop], "o", color=AZ, ms=4, label="prevista por Q (eixo precessante)")
    ax[1].plot(d["a_prev"][pop], d["abert"][pop], "s", color=LA, ms=3, label="eixos opticos do tensor l = 2")
    mx = np.nanmax(d["abert"][pop]) * 1.1
    ax[1].plot([0, mx], [0, mx], color=TX, lw=0.8)
    ax[1].set_xlabel("meia abertura prevista (graus)", color=TX)
    ax[1].set_ylabel("meia abertura medida dos pares de zeros (graus)", color=TX)
    ax[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(RAIZ, "figuras", "e34_angulos.png"), dpi=130, facecolor="#fcfcfb")


if __name__ == "__main__":
    main()
