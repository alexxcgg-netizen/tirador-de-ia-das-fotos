"""Experimento 32a (linha L08, agente D5): quanto da fase do (2,2) a memoria nula recupera com ruido realista.

Usa as matrizes de Fisher da memoria nula sozinha do sistema A calculadas pelo agente D3
(resultados/exp24_fisher_memoria.json: parametros lnM, q, chi1, chi2, lnD, cos iota, t0, psi; G1 = detector unico
psi = 0, G2 = segundo detector a 45 graus; priors de exp24_comum.SIG_PRIOR). Posterior gaussiano
Sigma = (G + Sigma_p^-1)^-1. Propaga para a fase do (2,2) prevista entre dois instantes OBSERVADOS t_a < t_b = pico:
    Delta psi = Psi_theta((t_b - t0)/M) - Psi_theta((t_a - t0)/M),
com derivadas: d/dlnM = -(t_b psidot_b - t_a psidot_a) (t em M desde o pico, a M fixo em segundos), d/dt0 =
-(psidot_b - psidot_a)/M_s, d/dq, d/dchi por diferencas centrais (passos 1e-3 e 2e-3, conferidos) a t/M fixo.
Informacao sobre a fase modulo 2 pi: I = log2(2 pi) - h(normal enrolada de desvio sigma) (bits).
Cenarios: ET e CE; detector unico e rede; todos os parametros livres; q e chi conhecidos; so lnM e t0 livres.
Saidas: resultados/exp32_fase_ruido.txt, .json
"""
import json
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np                                        # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp30_comum as C                                   # noqa: E402
from deteccao import MSUN_S                               # noqa: E402

linhas = []


def log(s=""):
    print(s, flush=True)
    linhas.append(s)


F24 = json.load(open(os.path.join(C.RES, "exp24_fisher_memoria.json")))
NOMES = F24["nomes"]
SP = np.array([F24["sig_prior"][n] for n in NOMES])
M, Q, C1, C2 = 65.0, 1.2, 0.3, -0.2
MS = M * MSUN_S
log("Sistema A (M = %.0f, q = %.1f, chi = (%.1f, %.1f), D = 400 Mpc, iota = 50 graus); Fisher da memoria nula: %s"
    % (M, Q, C1, C2, "resultados/exp24_fisher_memoria.json (agente D3)"))
log("parametros: %s ; desvios do prior: %s" % (NOMES, np.round(SP, 4).tolist()))


def fase22(q, c1, c2):
    """t (M, desde o pico de |h22| refinado), psi22(t) e psidot, desde ~8 Hz (margem para parametros vizinhos)."""
    t, h, ti = C.gerar(q, c1, c2, M=M, f_ini=8.0)
    h22 = h[(2, 2)]
    del h
    a = np.abs(h22)
    k = int(np.argmax(a))
    y0, y1, y2 = a[k - 1] ** 2, a[k] ** 2, a[k + 1] ** 2
    tp = t[k] + 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2) * (t[1] - t[0])
    psi = -np.unwrap(np.angle(h22))
    sel = t <= 40
    return t[sel] - tp, psi[sel], C.D(psi, t[1] - t[0])[sel]


t0g, ps0, pd0 = fase22(Q, C1, C2)
f22 = pd0 / (2 * np.pi * MS)                              # Hz
antes = t0g < 0


def instante_f(fhz):
    j = np.nonzero(antes & (f22 >= fhz))[0][0]
    return float(np.interp(fhz, f22[j - 1:j + 1], t0g[j - 1:j + 1]))


def interp(t, tg, y):
    return float(np.interp(t, tg, y))


instantes = {}
for fhz in (10.0, 20.0, 30.0, 50.0, 100.0):
    instantes["f22 = %.0f Hz" % fhz] = instante_f(fhz)
for ms in (100.0, 30.0, 10.0, 5.0, 2.0):
    instantes["%.0f ms antes do pico" % ms] = -ms * 1e-3 / MS
# derivadas em q, chi por diferencas centrais (dois passos)
grad = {nome: np.zeros(len(NOMES)) for nome in instantes}
dpsi = {}
for nome, ta in instantes.items():
    dpsi[nome] = interp(0.0, t0g, ps0) - interp(ta, t0g, ps0)
    pa, pb = interp(ta, t0g, pd0), interp(0.0, t0g, pd0)
    grad[nome][NOMES.index("lnM")] = -(0.0 * pb - ta * pa)
    grad[nome][NOMES.index("t0")] = -(pb - pa) / MS
conf = {}
for j, (par, base) in enumerate((("q", Q), ("c1", C1), ("c2", C2))):
    ests = []
    for hstep in (1e-3, 2e-3):
        vals = []
        for s in (+1, -1):
            args = [Q, C1, C2]
            args[j] = base + s * hstep
            tg, pg, _ = fase22(*args)
            vals.append({nome: interp(0.0, tg, pg) - interp(ta, tg, pg) for nome, ta in instantes.items()})
        ests.append({nome: (vals[0][nome] - vals[1][nome]) / (2 * hstep) for nome in instantes})
    for nome in instantes:
        grad[nome][NOMES.index(par)] = ests[0][nome]
        conf["%s %s" % (par, nome)] = float(abs(ests[1][nome] / ests[0][nome] - 1))
log("conferencia das derivadas (passo 2e-3 contra 1e-3, |razao - 1|): max %.1e" % max(conf.values()))


def entropia_enrolada(sig, n=4096):
    x = np.linspace(-np.pi, np.pi, n, endpoint=False)
    dx = x[1] - x[0]
    k = np.arange(-60, 61)
    p = np.sum(np.exp(-0.5 * ((x[:, None] + 2 * np.pi * k[None, :]) / sig) ** 2), axis=1) / (sig * np.sqrt(2 * np.pi))
    p = p / (np.sum(p) * dx)
    return float(-np.sum(p * np.log2(np.maximum(p, 1e-300))) * dx)


def bits_fase(sig):
    return max(0.0, _bits_fase(sig))


def _bits_fase(sig):
    if sig < 1e-3:
        return float(np.log2(2 * np.pi) - np.log2(sig * np.sqrt(2 * np.pi * np.e)))
    return float(np.log2(2 * np.pi) - entropia_enrolada(sig))


def posterior(G, livres):
    idx = [NOMES.index(n) for n in livres]
    Fp = G + np.diag(1 / SP ** 2)
    S = np.zeros((len(NOMES), len(NOMES)))
    S[np.ix_(idx, idx)] = np.linalg.inv(Fp[np.ix_(idx, idx)])
    return S


res = dict(instantes={k: float(v) for k, v in instantes.items()}, dpsi=dpsi, grad={k: v.tolist() for k, v in grad.items()},
           conf=max(conf.values()), cenarios={})
log("")
log("fase verdadeira acumulada ate o pico Delta psi (rad) e gradiente (d/dlnM, d/dq, d/dchi1, d/dchi2, d/dt0 [rad/ms]):")
for nome in instantes:
    g = grad[nome]
    log("  %-22s t_a = %9.1f M (%7.1f ms): Delta psi = %7.2f ; grad = %+.1f, %+.2f, %+.2f, %+.2f, %+.3f"
        % (nome, instantes[nome], instantes[nome] * MS * 1e3, dpsi[nome], g[0], g[1], g[2], g[3], g[6] * 1e-3))
CENARIOS = {"todos livres": NOMES, "q, chi conhecidos": ["lnM", "lnD", "cosi", "t0", "psi"],
            "so lnM e t0 livres": ["lnM", "t0"], "so prior (sem dados)": NOMES}
for det in ("ET", "CE"):
    A = F24["A"][det]
    G1, G2 = np.array(A["G1"]), np.array(A["G2"])
    for conf_det, G in (("detector unico", G1), ("rede (h+ e hx)", G1 + G2)):
        for cen, livres in CENARIOS.items():
            Gx = 0 * G if cen.startswith("so prior") else G
            S = posterior(Gx, livres)
            chave = "%s | %s | %s" % (det, conf_det, cen)
            out = {}
            partes = []
            for nome in instantes:
                g = grad[nome]
                sig = float(np.sqrt(g @ S @ g))
                out[nome] = dict(sigma=sig, bits=bits_fase(sig))
                partes.append("%s: %.2g rad (%.2f bits)" % (nome.replace(" antes do pico", ""), sig, out[nome]["bits"]))
            out["sigma_lnM"] = float(np.sqrt(S[0, 0]))
            out["sigma_t0_ms"] = float(np.sqrt(S[6, 6]) * 1e3)
            res["cenarios"][chave] = out
            log("")
            log("%s (rho+ = %.2f, rhox = %.2f; sigma_lnM = %.3f, sigma_t0 = %.2f ms):" % (chave, A["rho"], A["rho2"],
                                                                                       out["sigma_lnM"], out["sigma_t0_ms"]))
            log("   desvio da fase prevista ate o pico: " + " ; ".join(partes))
log("")
log("Leitura: a fase modulo 2 pi so e conhecida (> 1 bit) onde o desvio cai abaixo de ~1 rad.")
with open(os.path.join(C.RES, "exp32_fase_ruido.txt"), "w") as f:
    f.write("\n".join(linhas) + "\n")
with open(os.path.join(C.RES, "exp32_fase_ruido.json"), "w") as f:
    json.dump(res, f, indent=1)
