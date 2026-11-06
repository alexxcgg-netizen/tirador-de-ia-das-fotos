# Pesquisa — Bosch F01R00DT75 / Volvo 32313196 (TCU-053-19)

Investigação de documentação pública sobre o módulo específico. Data: 06/11/2026.

## Resumo do que foi encontrado

**Não existe página pública** que documente diretamente o P/N Volvo `32313196`,
o Bosch `F01R00DT75` ou o tipo `TCU-053-19` com detalhes de chipset. O que há é
contexto indireto, abaixo.

### 1. Natureza do módulo (DCT vs. Aisin)
As versões **2.0L** do XC40 (T4/T5 gasolina/mild-hybrid) usam automático **Aisin
8 marchas** (conversor de torque) — TCMs como `31380617`/`32249308`. O **T5 Twin
Engine híbrido** (1.5 3-cil) usa a **dupla embreagem 7DCTH**, cujo controlador é
este Bosch. **São famílias diferentes de TCM** — não são intercambiáveis.
→ Consequência prática: ignorar referências das versões 2.0L para compatibilidade.

### 2. Arquitetura típica de TCU Bosch
O datasheet público de TCU da Bosch descreve:
- Arquitetura **multicore em lockstep**
- Software base **AUTOSAR 4.0**
- Segurança funcional **ISO 26262 até ASIL D**
- Montagem **no módulo eletrônico ou sobre a transmissão**

Isso casa com a construção selada do nosso módulo.

### 3. Microcontrolador provável
A família **Infineon AURIX (TriCore)** é citada pela própria Infineon como típica
para **DCT (dupla embreagem)**. Geração **TC2xx** é a provável para 2019. **Não
confirmado** para este módulo — só abertura/teardown confirma.

### 4. ⚠️ Achado mais importante: pareamento NÃO é plug-and-play
Vendedores de módulos usados para esses Volvo são explícitos:
> "NOT plug-and-play. Requires professional EEPROM cloning or dealer reprogramming."
> "O sucesso depende de o part number bater com a unidade substituída."

**Implicação para o nosso objetivo:** mesmo que o firmware seja recuperado, fazer o
módulo voltar a funcionar no carro provavelmente depende de **clonagem de EEPROM**
(dados de pareamento/adaptação) e/ou reprogramação de nível concessionária. Esta é,
confirmadamente, a parte mais difícil — como já antecipado.

## Lacunas (o que ainda falta)
- [ ] Chipset interno real (MCU/flash/EEPROM) — depende de abrir
- [ ] Código de erro exato do VIDA na gravação — **dado nº 1**, ainda pendente
- [ ] Confirmar faixa de chassi / compatibilidade exata via VIN em catálogo oficial
- [ ] Localização da EEPROM de pareamento na placa

## Fontes
- [Bosch — Transmission Control Unit (datasheet PDF)](https://www.bosch-mobility.com/media/global/solutions/passenger-cars-and-light-commercial-vehicles/powertrain-solutions/transmission-technology/transmission-control-unit/productdatasheet_transmission-control-unit.pdf)
- [Infineon AURIX (Wikipedia)](https://en.wikipedia.org/wiki/Infineon_AURIX)
- [Infineon AURIX TC3xx — EV Engineering News](https://chargedevs.com/newswire/infineon-launches-aurix-family-of-tc3xx-microcontrollers-for-automotive-applications)
- [Volvo parts — TCM 32240939 (XC40 e outros)](https://parts.volvocars.ca/p/Volvo__/Control-Unit-Automatic-Transmission-TCM/97588071/32240939.html)
- [Volvo parts US — 31686384 (superseded 31461858, faixa de chassi XC40)](https://www.volvopartswebstore.com/products/Volvo/XC40/Automatic-Transmission-Control-Module/12580938/31686384.html)
- [Volvo parts — TCM 32249308 (XC40 2.0L, supersede 31380617)](https://usparts.volvocars.com/p/Volvo_2024_S90/Automatic-Transmission-Control-Module/102569134/32249308.html)
