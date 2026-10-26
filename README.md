[# Meus Lugares

Mapa pessoal de cachoeiras, morros, grutas, praias e pontos de acampamento em
Santa Catarina e no Rio Grande do Sul. Um arquivo HTML só, sem servidor, sem
build, sem dependência instalada. Abre com dois cliques.

**58 lugares no mapa.** A lista vem de links do Google Maps salvos ao longo do
tempo — os links curtos foram resolvidos para coordenadas pelo script incluído.

---

## Arquivos

| Arquivo | O que é |
|---|---|
| `mapa.html` | O site. É só isso que você precisa para usar. |
| `resolver_links.py` | Converte links curtos do Maps em coordenadas. Só para acrescentar lugares novos. |
| `README.md` | Este arquivo. |

---

## Como abrir

Dois cliques no `mapa.html`. Ele abre no navegador e funciona offline, exceto
pelas imagens do mapa, que vêm do OpenStreetMap e precisam de internet.

Se abrir no Bloco de Notas: botão direito → Abrir com → Chrome ou Edge.

### Colocar na internet

Como é um arquivo único, qualquer hospedagem estática serve.

**Netlify Drop** (mais rápido, sem cadastro):
renomeie o arquivo para `index.html`, ponha numa pasta sozinha e arraste a
pasta para `app.netlify.com/drop`. Em 20 segundos você tem um link.

**GitHub Pages** (melhor se quiser editar de qualquer lugar):
suba os arquivos num repositório, vá em Settings → Pages, escolha a branch
`main` e a pasta raiz. O endereço fica `usuario.github.io/repositorio`.
Depois dá para editar o `mapa.html` direto pelo site do GitHub, do celular
inclusive, e a página se atualiza sozinha.

---

## Onde ficam os saves

Dentro do `mapa.html`, num bloco marcado:

```js
/* ===============  INÍCIO DOS SAVES  =============== */
const LUGARES = [
  {id:"L04", nome:"Cachoeira Rio Vermelho", lat:-26.5885801, lng:-50.4001908,
   tipo:"cachoeira", nota:"", link:"https://maps.app.goo.gl/KkBjPbHKzNo9NUHR8"},
  ...
];
/* ===============  FIM DOS SAVES  ================== */
```

| Campo | O que faz |
|---|---|
| `id` | Identificador único. Não repita. |
| `nome` | Vazio (`""`) deixa o lugar sem nome e com pin de barraca. |
| `lat` | Latitude. `null` joga o lugar na aba Pendentes. |
| `lng` | Longitude. `null` idem. |
| `tipo` | Define o ícone do pin. Lista abaixo. |
| `nota` | Anotação livre, aparece no popup e entra na busca. |
| `link` | Link original do Google Maps. |

Para acrescentar um lugar na mão, copie uma linha, troque o `id` e os valores.

### Tipos disponíveis

`cachoeira` · `morro` · `gruta` · `canion` · `represa` · `praia` · `trilha` ·
`mirante` · `camping` · `ponto`

Lugar sem nome sempre recebe o pin de barraca, independente do tipo.

---

## Usando o site

**Lugares** — busca por nome ou anotação, filtro por categoria, lista clicável
que voa até o pin.

**Pendentes** — lugares sem coordenada. Abra o link, espere o mapa carregar,
copie o endereço da barra do navegador e cole no campo. Nome e coordenadas
entram sozinhos.

**Adicionar** — cole quantas linhas quiser de uma vez:

```
https://www.google.com/maps/place/...        link completo do Maps
https://maps.app.goo.gl/...                  link curto, entra como pendente
-26.9627, -49.2630                           coordenadas soltas
-26.9627, -49.2630 bom pra acampar           coordenadas + anotação
```

Ou ligue o modo clique e clique no mapa para criar um pin ali.

**Dados** — "Copiar código dos saves" devolve o bloco `const LUGARES` pronto
para colar no arquivo. "Copiar JSON" e "Colar JSON" servem de backup.

### Onde as edições ficam guardadas

No `localStorage` do navegador, sob a chave `meus_lugares_v1`. Isso quer dizer:

- Vale só naquele navegador, naquele computador
- Sobrevive a fechar e reabrir
- **Não entra no arquivo sozinho**

Para tornar permanente: aba Dados → Copiar código dos saves → cole no
`mapa.html` no lugar do bloco entre as marcas. Aí vale em qualquer lugar.

O botão "Descartar alterações do navegador" volta para o que está no arquivo.

---

## O resolver

Links curtos (`maps.app.goo.gl`) não revelam coordenada para quem não abre o
link. O navegador também não consegue abrir por conta própria, por causa das
regras de origem cruzada. Daí o script.

```
Windows:    python resolver_links.py
Mac/Linux:  python3 resolver_links.py
```

Deixe o script na mesma pasta do `mapa.html`. Ele segue cada link pendente,
pega nome e coordenadas, reescreve só o bloco dos saves e grava um
`mapa.html.bak` antes de mexer em qualquer coisa. Usa só a biblioteca padrão
do Python 3.

Ele também decodifica Plus Codes completos (`584H542H+W5`) e deduz o tipo pelo
nome do lugar.

### O que ele não resolve

- **Links de endereço.** Quando o Maps aponta para um bairro ou uma rodovia em
  vez de um ponto fixado, não existe coordenada no link. Resolva pela aba
  Pendentes.
- **Plus Codes curtos** (`542H+W5`). Dependem de uma cidade de referência para
  serem decodificados. O script avisa qual é a cidade e segue adiante.
- **Limite do Google.** Resolver dezenas de links seguidos pode ser bloqueado
  por um tempo. Ele avisa quais falharam; é só rodar de novo mais tarde.

---

## Pendências conhecidas

Dois lugares ainda sem coordenada, os dois links de endereço:

- `L02` Morro Alto - Bela Vista, Campos Novos - SC
- `L03` Ponte de Ferro do Passo do Inferno, RS-476, São Francisco de Paula - RS

Dois pares repetidos na lista original, marcados na anotação:

- `L45` e `L49` — Cachoeira Salto Pilão
- `L01` e `L52` — Cachoeira da Cortina

---

## Por dentro

[Leaflet 1.9.4](https://leafletjs.com) para o mapa. Três camadas: ruas
(OpenStreetMap), satélite (Esri World Imagery) e relevo (OpenTopoMap). Os pins
são SVG inline, sem imagem externa. Tema claro e escuro, acompanhando o sistema,
com botão para forçar um dos dois. O painel vira gaveta em tela de celular.
](https://brennobenk1.github.io/Picos-de-SC/)
