"""Experimento 26c: o que fixa o vale M*(q, chi1, chi2) da memoria orfa (complemento de exp26_analise).

O exp26_analise mostrou que nenhuma escala fisica simples (M_f, M_f/omega_220, largura da taxa, massa de chirp,
lei de ordem dominante M/(eta x*^4)) e mais constante ao longo do vale do que o proprio M*. Aqui testo:
  (1) regressoes de ln M* em (q, chi1, chi2) e em (eta, chi_eff, chi_a), lineares e quadraticas (descricao);
  (2) ln M* + k chi_eff com k otimo; ln(M* E_rad) com E_rad = 1 - m_f (surfinBH NRSur3dq8Remnant);
  (3) a hipotese "inclinacao espectral": com amplitude livre, o que a banda ve e a forma de |T(F)| a menos de escala;
      a combinacao medida seria o indice local n = d ln|F S+^(F)| / d ln F no centro de massa da SNR (f_c, CE).
      Calculo n(M* f_c) ao longo do vale (espectros adimensionais de exp24_comum) e comparo seu desvio padrao
      com o de n(M_A f_c) (M fixo): se o vale e "indice constante", o primeiro deve ser bem menor.
Saidas: resultados/exp26_vale.txt e .json
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp24_comum as C                                   # noqa: E402

LINHAS = []


def log(s=""):
    print(s, flush=True)
    LINHAS.append(s)


def r2_ajuste(X, y):
    Xd = np.column_stack([np.ones(len(y)), X])
    coef, *_ = np.linalg.lstsq(Xd, y, rcond=None)
    res = y - Xd @ coef
    return 1 - np.sum(res ** 2) / np.sum((y - y.mean()) ** 2), coef, np.std(res)


def main():
    import surfinBH
    fit = surfinBH.LoadFits("NRSur3dq8Remnant")
    out = {}
    for sist, Mref, f0 in (("A", 65.0, 0.0032015), ("baixa", 6.0, 0.0016)):
        with open(os.path.join(C.RES, "exp26_orfa_%s.json" % sist)) as fh:
            pts = [p for p in json.load(fh)["pontos"] if "erro" not in p]
        q = np.array([p["q"] for p in pts])
        c1 = np.array([p["c1"] for p in pts])
        c2 = np.array([p["c2"] for p in pts])
        eta = q / (1 + q) ** 2
        m1, m2 = q / (1 + q), 1 / (1 + q)
        ce = m1 * c1 + m2 * c2
        ca = 0.5 * (c1 - c2)
        lnM = np.array([p["CE"]["lnM_M"] for p in pts])
        lnM_ET = np.array([p["ET"]["lnM_M"] for p in pts])
        mf = np.array([fit.all(a, [0, 0, b], [0, 0, c])[0] for a, b, c in zip(q, c1, c2)])
        log("SISTEMA %s (%d pontos): desvio padrao de ln M* (CE, iota fixo) = %.4f ; ln M*(CE) - ln M*(ET): media %.4f, "
            "desvio %.4f" % (sist, len(pts), np.std(lnM), np.mean(lnM - lnM_ET), np.std(lnM - lnM_ET)))
        for rot, X in (("linear em (q, chi1, chi2)", np.column_stack([q, c1, c2])),
                       ("linear em (eta, chi_eff, chi_a)", np.column_stack([eta, ce, ca])),
                       ("quadratico em (q, chi1, chi2)", np.column_stack([q, c1, c2, q * q, c1 * c1, c2 * c2, q * c1,
                                                                          q * c2, c1 * c2])),
                       ("so chi_eff", ce[:, None]), ("so eta", eta[:, None])):
            r2, coef, sr = r2_ajuste(X, lnM)
            log("  ln M* %-34s R^2 = %.3f ; desvio do resto %.4f ; coef %s" % (rot, r2, sr,
                                                                            " ".join("%+.3f" % c for c in coef[:4])))
        ks = np.linspace(-1, 1, 201)
        sd = [np.std(lnM + k * ce) for k in ks]
        kb = ks[int(np.argmin(sd))]
        log("  ln M* + k chi_eff: k otimo %+.2f, desvio %.4f ; ln(M* E_rad): %.4f ; ln(M* m_f): %.4f"
            % (kb, min(sd), np.std(lnM + np.log(1 - mf)), np.std(lnM + np.log(mf))))
        # hipotese do indice espectral
        Ms = Mref * C.MSUN_S
        # centro da SNR de A em CE: media de f ponderada por |s|^2/S (exp24/25: f_rms ~ 27 Hz; uso a media geometrica)
        E0 = C.EspectroMemoria(1.2, 0.3, -0.2, Mref, f0 / Ms, N=2 ** 19 if sist == "A" else 2 ** 20,
                               T_tap=1500.0 if sist == "A" else 10000.0, Fmax=0.6)
        iota = np.radians(50.0)
        hp = E0.canais(iota)[0]
        f = E0.F / Ms
        w = C.psd_grade("CE", len(f), f[1] - f[0])
        pw = np.abs(hp) ** 2 * w
        fc = float(np.exp(np.sum(pw * np.log(np.where(f > 0, f, 1))) / np.sum(pw)))
        log("  centro geometrico da SNR^2 da memoria (CE): f_c = %.1f Hz" % fc)
        del E0
        n_vale, n_fixo = [], []
        for i, p in enumerate(pts):
            E = C.EspectroMemoria(p["q"], p["c1"], p["c2"], Mref, f0 / Ms, N=2 ** 19 if sist == "A" else 2 ** 20,
                                  T_tap=1500.0 if sist == "A" else 10000.0, Fmax=0.6)
            Tm = np.abs(E.F * (E.Sp_ @ C._Ylist(iota)))
            lnF, lnT = np.log(E.F[1:]), np.log(Tm[1:])
            for lista, lm in ((n_vale, lnM[i]), (n_fixo, np.log(Mref))):
                Fc = np.exp(lm) * C.MSUN_S * fc
                j = int(np.searchsorted(E.F, Fc))
                sel = slice(max(j - 40, 1), j + 40)
                lista.append(np.polyfit(np.log(E.F[sel]), np.log(Tm[sel]), 1)[0])
            del E
        n_vale, n_fixo = np.array(n_vale), np.array(n_fixo)
        log("  indice local n = d ln|F h+^| / d ln F em f_c: ao longo do vale (M = M*) media %.4f desvio %.4f ; "
            "com M = M_A fixo: media %.4f desvio %.4f" % (n_vale.mean(), n_vale.std(), n_fixo.mean(), n_fixo.std()))
        out[sist] = dict(sd_lnM=float(np.std(lnM)), n_vale=n_vale.tolist(), n_fixo=n_fixo.tolist(), fc=fc,
                         k_ce=float(kb), sd_k=float(min(sd)))
    with open(os.path.join(C.RES, "exp26_vale.json"), "w") as fh:
        json.dump(out, fh)
    with open(os.path.join(C.RES, "exp26_vale.txt"), "w") as fh:
        fh.write("\n".join(LINHAS) + "\n")


if __name__ == "__main__":
    main()
