# Revela

App de câmera para iPhone que fotografa em **RAW** e revela a foto com uma curva própria, sem o processamento de "aparência" da Apple (sem boost de contraste e sem tone mapping local).

## O que ele faz

**Captura**
- **ProRAW** (até 48 MP) ou **RAW puro** (Bayer, um único quadro, sem o processamento computacional da Apple).
- Lentes **Macro**, 0.5×, 1×, **2×**, 4× e **8×**, e a câmera da frente. O 2×, o 8× e o Macro são um recorte central do sensor de 48 MP (12 MP com qualidade óptica).
- **Macro**: usa a ultra-angular, que foca a 2 cm, com recorte 2× para aproximar ainda mais. Liga o peaking sozinho.
- **Foco empilhado**: 7 fotos com o foco indo do perto ao longe, alinhadas e juntadas pegando o pedaço mais nítido de cada uma. É o modo para macro de cabelo, pele, tecido, insetos: tudo nítido, mesmo com a profundidade de campo minúscula do macro.
- **Rápido**: disparo sem atraso em 12 MP (HEIC, ou RAW no RAW puro); segurar o botão faz rajada.
- **Ação**: grava 4K a 120 fps enquanto o botão está apertado e salva as 8 fotos mais nítidas + o vídeo.
- **Congelar**: obturador de 1/1000 a 1/16000 s com ISO automático; MÁX usa o formato de 240 fps do sensor (menos distorção de obturador, ~2 MP).
- **Noite**: 8 fotos a 1/15 s alinhadas e somadas: noite limpa sem o processamento da Apple.
- **Estrelas**: 16 exposições longas com foco no infinito, somadas (tripé ou iPhone apoiado).
- **Lua**: vai para a lente 8×, foco no infinito, exposição para a Lua e 8 fotos somadas.
- **Flash**: RAW com flash.
- **Retrato**: vai para o 2×, segue o rosto com o foco e a luz e usa o look Retrato. Um quadro no rosto mostra a distância estimada e avisa até você chegar em 1,3 m ou mais, onde a perspectiva não deforma o rosto.
- **Câmera da frente**: botão de virar ao lado do disparador. Se ela não oferecer RAW, o app fotografa em HEIC e aplica o look por cima.
- **Espelhar** (menu `…`): salva a foto invertida, como você se vê no espelho.
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
- Vinte looks de filme (Portra 400, Gold 200, Ektar 100, Velvia 50, Kodachrome, Pro 400H, CineStill 800T, Blockbuster, Technicolor, Bleach Bypass, Matrix, Pastel, Cross-process, Polaroid, Super 8, Tri-X 400, HP5, Noir, Sépia), com mistura de canais, curva por cor, vinheta, halation e grão de tamanhos diferentes; intensidade e grão ajustáveis.
- Salva na galeria a foto revelada (HEIC de 10 bits) + o **DNG original** num único item. Nas sequências, o DNG que vai junto é o do primeiro quadro.

**Relatório**
- Menu `…` → **Relatório para o Claude**: junta o modelo do iPhone, o que cada lente suporta, os ajustes atuais, o tempo de cada etapa das últimas fotos, erros, avisos de memória e temperatura, e os travamentos que o iOS registrar. Dá para escrever o que você notou e compartilhar o arquivo.

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
- `Revela/Diagnostics.swift` e `Revela/ReportView.swift`: registro e tela do relatório.
