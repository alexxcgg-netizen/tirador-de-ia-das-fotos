# Revela

App de câmera para iPhone que fotografa em **RAW** e revela a foto com uma curva própria, sem o processamento de "aparência" da Apple (sem boost de contraste e sem tone mapping local).

## O que ele faz

- **ProRAW** (até 48 MP) ou **RAW puro** (Bayer, um único quadro, sem o processamento computacional da Apple).
- ISO, obturador, balanço de branco (Kelvin) e foco manuais; no automático, compensação de EV.
- Lentes 0.5×, 1× e 4×.
- Três looks de revelação: **Neutro**, **Filme** (cor suave, preto levemente levantado, grão) e **P&B**.
- Salva na galeria como um único item: a foto revelada (HEIC) + o **DNG original**. Dá pra revelar o DNG de novo depois no Lightroom etc.

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
- `Revela/Tone.ci.metal`: a curva fílmica, cor, contraste e grão (kernel de Core Image).
- `Revela/ContentView.swift`: interface.
