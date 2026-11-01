"""Experimento 26b: analise da regiao degenerada da memoria orfa (saidas de exp26_orfa.py).

Para cada sistema (A, baixa): limiares 1/(2 rho^2) (rho do sinal de memoria em D = 400 Mpc e em outras D),
fracao do cubo (q, chi1, chi2) indistinguivel de A depois de otimizar ln M, cos iota (e amplitude, tempo, psi),
largura do vale em ln M, e o que fixa o vale M*(q, chi): comparo a constancia, ao longo dos pontos, de
ln M*, ln(M* m_f), ln(M* m_f / (M omega_220)) e ln(M* * largura da taxa de memoria), com m_f, chi_f do
NRSur3dq8Remnant (surfinBH) e omega_220 do pacote qnm, e a largura a meia altura da taxa da memoria nula h+
(iota = 50 graus) calculada aqui com observaveis.gerar_janela + exp24_comum.serie_modal.
Saidas: resultados/exp26_analise.txt e .json; figuras/e26_orfa.png
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp24_comum as C                                   # noqa: E402
import observaveis as O                                   # noqa: E402

LINHAS = []


def log(s=""):
    print(s, flush=True)
    LINHAS.append(s)


def carregar(sist):
    base = os.path.join(C.RES, "exp26_orfa_%s" % sist)
    if os.path.exists(base + ".json"):
        with open(base + ".json") as fh:
            return json.load(fh)["pontos"]
    pts = []
    with open(base + "_parcial.jsonl") as fh:
        for l in fh:
            pts.append(json.loads(l))
    return pts


def largura_taxa(q, c1, c2, iota=np.radians(50.0)):
    """Largura a meia altura (em M) e momento central de 2a ordem da taxa da memoria h+ perto da fusao."""
    t, h, ti = O.gerar_janela(q, c1, c2, 65.0, 10.0 * 0.0064 / 0.0032)      # janela curta (M f0 = 0.0064)
    mem, _ = O.memorias_observaveis(q, c1, c2, 65.0, 20.0, t=t, h=h, t_i=ti, desl="total")
    from harmonicos import sYlm
    dHtot = sum(float(np.real(mem["deslocamento"][(L, 0)])) * float(np.real(sYlm(-2, L, 0, iota, 0.0)))
                for L in range(2, 9))
    Yv = C._Ylist(iota)
    Qf = 8 * np.sqrt(np.pi / 5) * (5 / (14 * np.sqrt(6)) * Yv[0] + 1 / (504 * np.sqrt(2)) * Yv[2])
    xs = dHtot / (Qf * q / (1 + q) ** 2)
    k, G = C.serie_modal(t, h, ti)
    tt = t[k:]
    hp = (G @ C._Ylist(iota)).real
    r = np.gradient(hp, tt)
    j = int(np.argmax(r))
    meia = r[j] / 2
    a = j
    while a > 0 and r[a] > meia:
        a -= 1
    b = j
    while b < len(r) - 1 and r[b] > meia:
        b += 1
    sel = tt > tt[j] - 300
    w = r[sel] / np.sum(r[sel])
    mu = np.sum(w * tt[sel])
    sig = np.sqrt(np.sum(w * (tt[sel] - mu) ** 2))
    return float(tt[b] - tt[a]), float(sig), float(xs)


def main():
    import surfinBH
    import qnm
    fit = surfinBH.LoadFits("NRSur3dq8Remnant")
    modo = qnm.modes_cache(s=-2, l=2, m=2, n=0)
    rho = {}
    with open(os.path.join(C.RES, "exp24_fisher_memoria.json")) as fh:
        J24 = json.load(fh)
    rho["A"] = {p: J24["snr"][p][0] for p in ("ET", "CE")}
    rho["baixa"] = {p: J24["baixa"][p]["rho"] for p in ("ET", "CE")}
    res = {}
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    C.estilo(plt)
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))
    for si, sist in enumerate(("A", "baixa")):
        try:
            pts = carregar(sist)
        except FileNotFoundError:
            continue
        pts = [p for p in pts if "erro" not in p]
        log("SISTEMA %s: %d pontos" % (sist, len(pts)))
        res[sist] = {}
        D_list = [400.0] if sist == "A" else [400.0, 400.0 * rho["baixa"]["CE"] / 34.09]
        for p in ("CE", "ET"):
            mm = np.array([x[p]["mm"] for x in pts])
            mmM = np.array([x[p]["mm_M"] for x in pts])
            mmA = np.array([x[p]["mm_MA"] for x in pts])
            sob = np.array([x["rotulo"] == "sobol" for x in pts])
            for D in D_list:
                r_ = rho[sist][p] * 400.0 / D
                lim = 1 / (2 * r_ ** 2)
                log("  %s, D = %.1f Mpc (rho = %.2f, limiar 1-match < %.2e): fracao dos %d pontos de Sobol dentro: "
                    "%.2f (M e iota livres) ; %.2f (so M livre, iota = 50 graus) ; %.2f (M = M_A)"
                    % (p, D, r_, lim, sob.sum(), np.mean(mm[sob] < lim), np.mean(mmM[sob] < lim), np.mean(mmA[sob] < lim)))
                res[sist]["%s_D%.0f" % (p, D)] = dict(rho=r_, lim=lim, frac=float(np.mean(mm[sob] < lim)),
                                                     frac_M=float(np.mean(mmM[sob] < lim)),
                                                     frac_MA=float(np.mean(mmA[sob] < lim)))
            # rho minimo para separar cada ponto: rho_sep = 1/sqrt(2 mm)
            rs = 1 / np.sqrt(2 * np.clip(mm[sob], 1e-30, None))
            log("  %s: rho necessario para excluir cada ponto (1/sqrt(2 mm_min)), percentis 10/50/90 dos Sobol: "
                "%.0f / %.0f / %.0f ; fracao excluida com rho = 100: %.2f, 300: %.2f, 1000: %.2f"
                % (p, *np.percentile(rs, [10, 50, 90]), np.mean(rs < 100), np.mean(rs < 300), np.mean(rs < 1000)))
            res[sist][p + "_rho_sep_pct"] = np.percentile(rs, [10, 50, 90]).tolist()
        # largura do vale em ln M (perfil na grade, CE)
        larg = []
        for x in pts:
            g = np.array(x["grade_lnM"])
            v = np.array(x["perfil_CE"])
            j = int(np.argmin(v))
            if 0 < j < len(v) - 1:
                h = g[1] - g[0]
                a = (v[j + 1] + v[j - 1] - 2 * v[j]) / (2 * h * h)
                if a > 0:
                    larg.append(a)
        a_med = float(np.median(larg))
        lim_CE = 1 / (2 * rho[sist]["CE"] ** 2)
        log("  curvatura do vale em ln M (CE, so M livre): 1-match ~ a (ln M - ln M*)^2, a mediano = %.3g ; "
            "meia largura no limiar de CE (rho = %.1f): Delta ln M = %.3f" % (a_med, rho[sist]["CE"],
                                                                             np.sqrt(lim_CE / a_med)))
        res[sist]["curv_lnM"] = a_med
        # Fisher contra perfil: ponto A (q, chi fixos), iota fixo, (D, t0, psi) livres -> 1-match = G_red dlnM^2/(2 rho^2)
        if sist in ("A", "baixa"):
            chave = "A" if sist == "A" else "baixa"
            for p in ("CE", "ET"):
                G1 = np.array(J24[chave][p]["G1"])
                nomes = J24["nomes"]
                livres = [nomes.index(n) for n in ("lnD", "t0", "psi")]
                i0 = nomes.index("lnM")
                A_ = G1[i0, i0]
                Bv = G1[i0, livres]
                Cm = G1[np.ix_(livres, livres)]
                Gr = A_ - Bv @ np.linalg.solve(Cm, Bv)
                r_ = rho[sist][p]
                xA = [x for x in pts if x["rotulo"] == "A"][0]
                g = np.array(xA["grade_lnM"])
                v = np.array(xA["perfil_" + p])
                lnMA = np.log(65.0 if sist == "A" else 6.0)
                prev = Gr * (g - lnMA) ** 2 / (2 * r_ ** 2)
                sel = np.abs(g - lnMA) < 0.35
                log("  Fisher contra perfil (%s, ponto A, iota fixo, D/t0/psi livres): d ln M | 1-match perfil | Fisher" % p)
                for gg, vv, pp in zip(g[sel], v[sel], prev[sel]):
                    log("     %+.3f  %.3e  %.3e  (razao %.2f)" % (gg - lnMA, vv, pp, vv / pp if pp > 0 else np.nan))
                res[sist]["fisher_perfil_" + p] = dict(dlnM=(g[sel] - lnMA).tolist(), perfil=v[sel].tolist(),
                                                       fisher=prev[sel].tolist())
        # pares do exp07
        for x in pts:
            if x["rotulo"].startswith("exp07") or x["rotulo"] == "A":
                log("  %-20s q %.1f chi (%.2f, %.2f): CE 1-match_min %.2e (M* %.2f, cos i* %.2f) ; ET %.2e ; "
                    "com M = 65: CE %.2e" % (x["rotulo"], x["q"], x["c1"], x["c2"], x["CE"]["mm"],
                                              np.exp(x["CE"]["lnM"]), x["CE"]["cosi"], x["ET"]["mm"], x["CE"]["mm_MA"]))
        # o que fixa o vale: so para A (as larguras usam a janela adimensional de A)
        cand = {}
        Mst = np.array([np.exp(x["CE"]["lnM_M"]) for x in pts])
        mf = np.zeros(len(pts))
        chif = np.zeros(len(pts))
        w22 = np.zeros(len(pts))
        fwhm = np.zeros(len(pts))
        sig = np.zeros(len(pts))
        xs = np.zeros(len(pts))
        for i, x in enumerate(pts):
            m_, c_, _, = fit.all(x["q"], [0, 0, x["c1"]], [0, 0, x["c2"]])[:3]
            mf[i] = m_
            chif[i] = c_[2]
            w22[i] = np.real(modo(a=abs(c_[2]))[0])
            fwhm[i], sig[i], xs[i] = largura_taxa(x["q"], x["c1"], x["c2"])
        cand["ln M*"] = np.log(Mst)
        cand["ln(M* m_f)"] = np.log(Mst * mf)
        cand["ln(M* m_f / omega_220)"] = np.log(Mst * mf / w22)
        cand["ln(M* x largura a meia altura da taxa)"] = np.log(Mst * fwhm)
        cand["ln(M* x desvio padrao da taxa)"] = np.log(Mst * sig)
        etas = np.array([x["q"] / (1 + x["q"]) ** 2 for x in pts])
        cand["ln(M* eta^0.6) (chirp)"] = np.log(Mst * etas ** 0.6)
        cand["ln(M*/(eta x*^4)) (lei 1/4, ordem dominante)"] = np.log(Mst / (etas * xs ** 4))
        mmv = np.array([x["CE"]["mm_M"] for x in pts])
        dentro = mmv < 5 * lim_CE
        log("  O que fixa o vale (pontos com 1-match_min(M) < 5 x limiar de CE, n = %d): desvio padrao de cada candidato"
            % dentro.sum())
        for k_, v in cand.items():
            log("     %-42s %.4f (todos os pontos: %.4f)" % (k_, np.std(v[dentro]), np.std(v)))
        res[sist]["vale"] = {k_: [float(np.std(v[dentro])), float(np.std(v))] for k_, v in cand.items()}
        # figuras
        if sist == "A":
            q_ = np.array([x["q"] for x in pts])
            ce = np.array([(x["q"] * x["c1"] + x["c2"]) / (1 + x["q"]) for x in pts])
            sc = ax[0].scatter(q_, [x["CE"]["mm"] for x in pts], c=ce, cmap="coolwarm", s=12, vmin=-0.8, vmax=0.8)
            ax[0].axhline(lim_CE, color=C.COR["azul"], ls="--", lw=1)
            ax[0].axhline(1 / (2 * rho["A"]["ET"] ** 2), color=C.COR["verde"], ls="--", lw=1)
            ax[0].text(5.9, lim_CE * 1.2, "limiar CE (ρ = 34)", ha="right", fontsize=7, color=C.COR["azul"])
            ax[0].text(5.9, 1.2 / (2 * rho["A"]["ET"] ** 2), "limiar ET (ρ = 8,6)", ha="right", fontsize=7,
                       color=C.COR["verde"])
            ax[0].set_yscale("log")
            ax[0].set_xlabel("q de B")
            ax[0].set_ylabel("1 − match mínimo (M, ι, ψ, D, t0 livres)")
            ax[0].set_title("memória órfã: B contra A (CE)")
            fig.colorbar(sc, ax=ax[0], label="χ_eff de B", fraction=0.04)
            sc2 = ax[1].scatter(q_, Mst, s=12, c=ce, cmap="coolwarm", vmin=-0.8, vmax=0.8)
            ax[1].axhline(65.0, color=C.COR["texto"], ls=":", lw=0.8)
            ax[1].set_xlabel("q de B")
            ax[1].set_ylabel("M* (M_⊙) que minimiza 1 − match (CE, ι = 50°)")
            ax[1].set_title("o vale M*(q, χ) (A: M = 65)")
            fig.colorbar(sc2, ax=ax[1], label="χ_eff de B", fraction=0.04)
        rr = np.logspace(0, 3.3, 80)
        for p, cor in (("CE", C.COR["azul"]), ("ET", C.COR["verde"])):
            mm = np.array([x[p]["mm"] for x in pts if x["rotulo"] == "sobol"])
            ax[2].semilogx(rr, [np.mean(mm < 1 / (2 * r * r)) for r in rr], color=cor,
                           ls="-" if sist == "A" else "--", label="%s, %s" % (p, "M = 65" if sist == "A" else "M = 6"))
    ax[2].set_xlabel("SNR da memória ρ")
    ax[2].set_ylabel("fração de (q, χ1, χ2) indistinguível")
    ax[2].set_title("tamanho da região degenerada")
    ax[2].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(C.FIG, "e26_orfa.png"), dpi=150)
    with open(os.path.join(C.RES, "exp26_analise.json"), "w") as fh:
        json.dump(res, fh, default=float)
    with open(os.path.join(C.RES, "exp26_analise.txt"), "w") as fh:
        fh.write("\n".join(LINHAS) + "\n")


if __name__ == "__main__":
    main()
