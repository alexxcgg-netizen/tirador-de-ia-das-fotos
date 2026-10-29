# Revela

App de câmera para iPhone que fotografa em **RAW** e revela a foto com uma curva própria, sem o processamento de "aparência" da Apple (sem boost de contraste e sem tone mapping local).

## O que ele faz

**Captura**
- **ProRAW** (até 48 MP) ou **RAW puro** (Bayer, um único quadro, sem o processamento computacional da Apple).
- Lentes **Macro**, 0.5×, 1×, **2×**, 4× e **8×**. O 2×, o 8× e o Macro são um recorte central do sensor de 48 MP (12 MP com qualidade óptica).
- **Macro**: usa a ultra-angular, que foca a 2 cm, com recorte 2× para aproximar ainda mais. Liga o peaking sozinho.
- **Foco empilhado**: 7 fotos com o foco indo do perto ao longe, alinhadas e juntadas pegando o pedaço mais nítido de cada uma. É o modo para macro de cabelo, pele, tecido, insetos: tudo nítido, mesmo com a profundidade de campo minúscula do macro.
- **Média**: 8 fotos alinhadas e somadas. À noite tira o ruído sem o processamento da Apple; com obturador lento deixa água e nuvens lisas.
- ISO, obturador, balanço de branco (Kelvin) e foco manuais; no automático, compensação de EV.
- Proporções 4:3, 1:1, 16:9 e 65:24 (panorâmica de cinema).
- Timer de 3 ou 10 segundos. Dispara pelo botão de volume e pelo **Controle da Câmera**, que também ajusta exposição, foco e look.

**Visor**
- **Look ao vivo**: o vídeo da câmera passa pela mesma curva da revelação.
- **Focus peaking** (bordas em foco em âmbar) e **lupa 4×** enquanto você arrasta o foco manual.
- Toque para focar e medir a luz naquele ponto.
- Histograma, zebra (listras onde a luz estourou), grade de terços e nível do horizonte.

**Revelação**
- Cinco looks: **Neutro**, **Filme**, **Cine**, **Suave** e **Prata** (P&B), com intensidade e grão ajustáveis.
- Salva na galeria a foto revelada (HEIC de 10 bits) + o **DNG original** num único item. Nas sequências, o DNG que vai junto é o do primeiro quadro.

## Como gerar o app

Cada push que mexe na pasta `camera-raw/` compila o app no GitHub Actions (num Mac da nuvem).
Em **Actions → Revela (IPA) → (última execução) → Artifacts**, baixe `Revela-ipa`. É um .zip com o `Revela.ipa` dentro.

## Como instalar no iPhone (Windows, grátis)

1. No PC, instale o **iTunes** e o **iCloud** baixados do site da Apple (não da Microsoft Store), e depois o **[Sideloadly](https://sideloadly.io)**.
2. Ligue o iPhone no PC pelo cabo e toque em "Confiar neste computador".
3. Abra o Sideloadly, arraste o `Revela.ipa`, digite o seu Apple ID e clique em **Start**.
   Dica: dá pra usar um Apple ID secundário, criado só para isso.
4. No iPhone:
   - **Ajustes → Privacidade e Segurança → Modo de Desenvolvedor** → ativar (o iPhone reinicia).
   - **Ajustes → Geral → VPN e Gerenciamento de Dispositivo** → tocar no seu Apple ID → **Confiar**.
5. Com Apple ID grátis o app vale **7 dias**. Depois é só repetir o passo 3 (as fotos ficam na galeria, nada se perde).

## Estrutura

- `project.yml`: projeto do Xcode (gerado com XcodeGen).
- `Revela/CameraModel.swift`: sessão da câmera, controles manuais, captura e salvamento.
- `Revela/Developer.swift`: revelação do DNG (CIRAWFilter em luz linear + kernel próprio).
- `Revela/LivePreview.swift`: visor ao vivo com o look e o histograma.
- `Revela/Tone.ci.metal`: a curva fílmica, cor, contraste, split toning, grão e zebra (kernels de Core Image).
- `Revela/ContentView.swift`: interface.
