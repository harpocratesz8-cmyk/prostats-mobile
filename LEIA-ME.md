# ProStats Mobile 2.0

App de celular do ProStats. Fica instalado no celular, funciona sem internet e usa o mesmo arquivo de save (`.json`) do ProStats para PC.

## O que tem nesta pasta

| Pasta | O que é |
|---|---|
| `web/www/` | O app em si (telas, estatísticas, salvamento no celular) |
| `android/` | Projeto Android que empacota o app como `.apk` |
| `.github/workflows/` | Receitas que fazem o GitHub gerar o `.apk` de graça |

## Como gerar o APK (uma vez, uns 10 minutos)

1. Crie uma conta grátis em **github.com** (ou entre na sua).
2. Clique em **New repository**. Dê o nome `prostats-mobile` e clique em **Create repository**.
3. Na página do repositório, clique em **uploading an existing file**. Arraste **todo o conteúdo** desta pasta, incluindo a pasta `.github`, e clique em **Commit changes**.
4. Abra a aba **Actions**. O processo "Gerar APK Android" começa sozinho e leva uns 5 minutos. Quando ficar verde, o APK está pronto.
5. No **celular**, abra `github.com/SEU-USUARIO/prostats-mobile/releases` e toque em **ProStats.apk** para baixar.
6. Toque no arquivo baixado. O Android pede para **permitir instalar apps desta fonte**. Permita e instale.

### Atualizações

Quando houver uma versão nova, envie os arquivos novos para o mesmo repositório (passo 3). O GitHub gera outro APK, que instala **por cima** do anterior. Seus saves ficam guardados, porque todo APK é assinado com a mesma chave (`android/app/prostats-release.keystore`). Não apague esse arquivo: sem ele, o celular não aceita a atualização e seria preciso desinstalar o app (e os saves junto).

## Como passar o save do PC para o celular

1. No PC, o save fica na pasta `saves` do ProStats (ex.: `saves/save_rafael_duarte.json`).
2. Mande esse arquivo para o celular: WhatsApp (para você mesmo), Google Drive, e-mail ou cabo USB.
3. No celular, toque no arquivo e escolha **Abrir com ProStats**. Outra opção: no app, vá em **Mais → Carreiras e dados → Importar save**.

Se a carreira já existir no celular (mesmo nome de jogador), a importação **atualiza** essa carreira.

### Do celular para o PC

No app, abra **Mais → Carreiras e dados → Exportar save**. Escolha **Salvar em Downloads** (fica em `Downloads/ProStats`) ou **Compartilhar** (WhatsApp, Drive…). No PC, coloque o arquivo na pasta `saves` e use **Carregar Carreira**.

### Escudos

Toque no escudo de um clube (no perfil ou em Stats → Clubes) para escolher uma imagem da galeria. Para trazer todos os escudos do PC de uma vez, copie as imagens da pasta `Logos` do ProStats para o celular. Depois use **Mais → Carreiras e dados → Importar imagens de escudos** e selecione todas. O nome do arquivo vira o nome do clube.

## iPhone

A Apple não permite instalar `.apk`. Para iPhone, ative o GitHub Pages: **Settings → Pages → Source: GitHub Actions**. Depois rode o processo **"Publicar app web"** na aba Actions. Abra o link gerado no Safari e toque em **Compartilhar → Adicionar à Tela de Início**. O app fica no celular e funciona offline.
