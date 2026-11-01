"""Extrai expressoes PN de dois arquivos auxiliares publicados no arXiv (lidos como DADOS, so texto) e grava em JSON.

Uso (rodar com python -I, os arquivos baixados ficam fora do repositorio):
  python -I exp20_pn_extrair.py <Supplementary_Material.dat.wl> <ABFO09.m> <saida.json>

1. Cunningham, Kavanagh, Pound, Trestini, Warburton, Neef, CQG 42, 135009 (2025), arXiv:2410.23950v2, material
   suplementar (anc/Supplementary_Material.dat.wl): E(x) 3.5PN com spins (eq. 40), fluxo no infinito (eq. 41), fluxo
   no horizonte (eq. 44), xdot (eq. 45), dU_20/dt (eq. 39), H_20 (eq. 50) e H_40, H_60, H_80 (spins alinhados,
   SO + SS + SSS). Variaveis: s = (m1^2 chi1 + m2^2 chi2)/M^2, sigma = (m2 chi2 - m1 chi1)/M, delta = (m1 - m2)/M.
2. Arun, Buonanno, Faye, Ochsner, PRD 79, 104023 (2009), arXiv:0810.5336v3 (anc/ABFO09.m): modos h_lm (l <= 4,
   m >= 0) ate 1.5PN com spin-orbita. Limite nao precessante: iota = 0, alpha = pi (secao II do artigo), spins no
   plano nulos. chi_s = (chi1 + chi2)/2, chi_a = (chi1 - chi2)/2, delta = (m1 - m2)/M.

As expressoes sao convertidas por sympy.parsing.mathematica.parse_mathematica (nao executa codigo) e gravadas como
texto sympy (srepr nao e necessario: str + sympify com os simbolos declarados).
"""
import json
import re
import sys

import sympy as sp
from sympy.parsing.mathematica import parse_mathematica

TROCA = {r"\[Nu]": "nu", r"\[Delta]": "delta", r"\[Sigma]": "sigma", r"\[CapitalPsi]": "Psi", r"\[Iota]": "iota",
         r"\[Alpha]": "alpha", r"\[Theta]": "theta", r"\[Chi]sz": "chisz", r"\[Chi]az": "chiaz",
         r"\[Chi]sx": "chisx", r"\[Chi]ax": "chiax", r"\[Chi]sy": "chisy", r"\[Chi]ay": "chiay", r"\[Tau]": "tau"}


def limpar(txt):
    for a, b in TROCA.items():
        txt = txt.replace(a, b)
    return txt


def blocos(txt):
    """Divide o arquivo em atribuicoes 'nome = expr;' (nivel superior)."""
    txt = re.sub(r"\(\*.*?\*\)", " ", txt, flags=re.S)        # comentarios
    out = {}
    for parte in txt.split(";"):
        if "=" not in parte:
            continue
        nome, expr = parte.split("=", 1)
        nome = " ".join(nome.split())
        out[nome] = " ".join(expr.split())
    return out


def conv(expr):
    e = parse_mathematica(expr)
    return e


if __name__ == "__main__":
    sup, abfo, saida = sys.argv[1:4]
    res = {}
    b = blocos(limpar(open(sup).read()))
    alvo = {"E": "E$3p5PN", "F": "F$infinity$3p5PN", "dF_H": "\\[Delta]F$3p5PN".replace("\\[Delta]", "delta"),
            "xdot": "xdot$3p5PN", "U20dot": "Ulm$dot$3p5PN[2,0]", "U40dot": "Ulm$dot$3p5PN[4,0]",
            "H20": "Hlm$3p5PN[2,0]", "H40": "Hlm$3p5PN[4,0]", "H60": "Hlm$3p5PN[6,0]", "H80": "Hlm$3p5PN[8,0]",
            "norm": "normalization$Hlm"}
    c, G = sp.symbols("c G")
    for k, nome in alvo.items():
        if nome not in b:
            print("faltou", nome, [n for n in b if n.startswith(nome[:4])])
            continue
        e = conv(b[nome])
        e = e.subs({c: 1, G: 1})
        res[k] = str(sp.simplify(e) if k == "norm" else e)
        print(k, "ok", len(res[k]))
    # ABFO: modos l <= 4, m >= 0, limite alinhado
    b2 = blocos(limpar(open(abfo).read()))
    iota, alpha, Psi = sp.symbols("iota alpha Psi")
    zeros = {sp.Symbol(n): 0 for n in ("chisx", "chisy", "chiax", "chiay")}
    for l in (2, 3, 4):
        for m in range(0, l + 1):
            nome = "hlm[%d, %d]" % (l, m)
            if nome not in b2:
                print("faltou", nome)
                continue
            e = conv(b2[nome])
            e = e.subs(zeros).subs({iota: 0, alpha: sp.pi})
            e = sp.simplify(sp.expand(e))
            # dependencia em Psi deve ser exp(-i m Psi): confere e tira
            r = sp.simplify(e * sp.exp(sp.I * m * Psi))
            if sp.simplify(sp.diff(r, Psi)) != 0:
                print("AVISO: dependencia em Psi nao e exp(-i m Psi) em", nome)
            res["h%d%d" % (l, m)] = str(sp.expand(r.subs(Psi, 0)))
            print(nome, "ok:", res["h%d%d" % (l, m)][:160])
    json.dump(res, open(saida, "w"), indent=1)
