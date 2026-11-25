# Modelar a partir de uma imagem de referência

Ler a imagem é a parte que mais erra, mais do que modelar. Por isso a leitura é conferida pela pessoa antes de
qualquer modelagem, e o resultado é medido contra a imagem com número, não no olho.

## O que uma imagem não dá

- **Tamanho real.** Peça uma medida de verdade (a largura total, o diâmetro de um furo) ou um objeto conhecido
  na foto. Sem isso, o tamanho é chute e precisa ser dito como chute.
- **O verso, o interior e a espessura.** Pergunte ou assuma dizendo.
- **Medida exata.** Número escrito num desenho técnico vale; medida tirada de pixel é aproximada.

## Passo 1: descreva antes de modelar

1. Uma frase dizendo o que é o objeto.
2. Conte as partes. Poucas partes num objeto real quer dizer que alguma ficou de fora.
3. Para cada parte: forma, tamanho, posição, se é saliência ou rebaixo, e para que serve.
4. As relações: o que é cópia, o que é contorno de outra parte engordado, o que é simétrico.
5. As dúvidas: tudo o que você não conseguiu ver.

Mostre essa lista e peça a confirmação. Uma descrição corrigida pela pessoa dá um resultado várias vezes melhor
do que uma descrição que ninguém conferiu.

Erros comuns de leitura: contorno derivado de outra forma virar um retângulo arredondado qualquer; detalhe da
face escondida ser esquecido; número do carimbo do desenho ser lido como medida.

## Passo 2: escolha entre traçar e medir

| A referência é | Faça |
|---|---|
| Desenho técnico com cotas | Tabela de medidas a partir das cotas; a imagem serve só para a forma |
| Foto de frente de um objeto de contorno definido (logo, silhueta, letra, objeto plano) | Trace o contorno da imagem e use-o como perfil |
| Foto em perspectiva | Descrição por partes e medidas confirmadas; não trace |
| Forma orgânica | Blender, com a imagem ao fundo na mesma vista |

Para traçar: separe o objeto do fundo, ache o contorno, simplifique, converta de pixel para milímetro com a
medida real (`mm = pixels / escala`) e guarde os pontos num arquivo. O modelo lê esse arquivo: se o contorno
mudar, o modelo acompanha.

## Passo 3: o raio-x

O raio-x põe a silhueta da peça sobre a silhueta da referência, na mesma vista, e mede quanto coincide.

```bash
python -m filuna_cad raio-x peca.stl referencia.png --vista frente --saida raio_x.png
```

Sai a semelhança de 0 a 1 e uma imagem: branco é igual, **vermelho é o que falta na peça**, **azul é o que sobra
na peça**. O vermelho e o azul dizem onde mexer.

- A referência precisa ter fundo liso ou transparente e mostrar o objeto de frente, sem perspectiva.
- A vista da peça tem que ser a mesma da foto: `frente`, `lado` ou `cima`.
- Áreas que não fazem parte da peça (o nome que será gravado depois, uma argola de metal) saem da referência
  antes de medir.
- O raio-x mede contorno. Não mede relevo interno, espessura nem cor: uma peça com silhueta certa e relevo
  errado tira nota alta. Diga isso junto com a nota.

## Passo 4: afinar com conta

Quando um detalhe (largura de uma alça, raio de uma orelha) puder variar, deixe-o como parâmetro e varie um de
cada vez, medindo o raio-x a cada rodada: fique com a mudança só se a nota subir. Ponha limites nos parâmetros
que protegem a peça (parede em volta de um furo, espessura mínima): a busca não pode afinar uma parede para
ganhar semelhança.

## O que dizer no fim

A nota medida, com o número de verdade, em qual vista, o que ficou fora da medição e o que o raio-x não enxerga.
Uma meta de semelhança só está cumprida quando o número medido passa dela; "parece igual" não conta.
