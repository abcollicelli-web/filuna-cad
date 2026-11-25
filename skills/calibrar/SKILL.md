---
name: calibrar
description: Descobre a folga de encaixe real de uma impressora com um teste impresso (cupom de folga) e leva o resultado de volta para os parâmetros do modelo, e corrige um modelo a partir de uma peça impressa e medida. Use antes de imprimir peças que encaixam, quando um encaixe sair apertado ou frouxo, quando um furo ou medida sair diferente do desenho, ou ao começar a usar uma impressora ou um material novo.
---

# Calibrar: da peça impressa de volta ao modelo

Nenhuma tabela sabe a folga da sua impressora. Bico, material, temperatura e até a bobina mudam o resultado em
décimos de milímetro, e encaixe se decide em décimos. O caminho curto é imprimir um teste de 20 minutos, medir e
usar o número medido como parâmetro.

## O cupom de folga

```bash
python -m filuna_cad cupom saida/ --diametro 8
```

Gera duas peças pequenas:

- **Régua:** uma placa de 6 mm com seis furos, para folgas de 0,10 / 0,15 / 0,20 / 0,25 / 0,30 / 0,40 mm por
  lado. O canto cortado marca o lado do furo mais justo.
- **Pino:** um pino no diâmetro exato, com uma pega quadrada e a ponta chanfrada.

Como fazer o teste:

1. Imprima as duas peças deitadas como saem, **no material, na camada e no perfil da peça final**.
2. Deixe esfriar. Tente o pino em cada furo, começando pelo mais folgado.
3. Anote três números:
   - o furo mais justo em que o pino **entra com a mão**: é a folga justa;
   - o furo mais justo em que o pino **entra e gira solto**: é a folga de deslizar;
   - o furo em que o pino **só entra forçando**: é a folga de pressão.
4. Guarde os números com a impressora, o material e a data. Trocar de material pede teste novo.

Use o diâmetro do encaixe real (`--diametro`) quando ele for muito diferente de 8 mm: furo pequeno fecha mais.

## Levar o resultado para o modelo

- A folga é **um parâmetro no topo do modelo**, nunca um número espalhado: `FOLGA_JUSTA`, `FOLGA_DESLIZA`.
- O modelo guarda as medidas nominais; a folga entra somada no furo ou tirada do pino, em um lugar só.
- Se o fatiador já compensa furo e contorno, a folga medida já inclui essa compensação: não some outra.
- Diga de onde veio cada folga: medida no cupom (qual impressora e material) ou tirada de tabela.

## Quando a peça saiu diferente do desenho

Peça à pessoa a medida com paquímetro, em milímetros, e o que era esperado. Depois:

| Saiu | Causa provável | Correção |
|---|---|---|
| Furo vertical menor | Fio espalha para dentro; furo é polígono | Compensação de furo no fatiador, ou somar a diferença no parâmetro do furo |
| Medida externa maior | Fluxo alto ou compensação de contorno | Calibrar fluxo; só depois mexer no modelo |
| Base mais larga que o resto | Primeira camada espalhada | Chanfro de 0,5 mm na base; compensação de pé de elefante |
| Encaixe entra e depois afrouxa | Plástico cede com o tempo | Trocar pressão por trava, nervuras ou parafuso |
| Só uma direção errada (X certo, Y errado) | Mecânica da impressora | Não corrija no modelo: é ajuste da máquina |
| Altura errada em múltiplos da camada | Detalhe fora da grade de camadas | Alturas em múltiplo da camada |

Regras:

1. **Uma correção por vez**, e imprima só o pedaço que tem o encaixe.
2. **Corrija a causa onde ela está.** Erro da máquina se corrige na máquina; erro de desenho, no desenho. Mudar a
   escala do modelo para compensar esconde o problema e estraga as outras medidas.
3. **Erro igual em todas as peças** é calibração; **erro só nesta peça** é desenho.
4. Depois de corrigir, gere de novo e compare com a versão anterior
   (`python -m filuna_cad comparar antes.stl depois.stl`) para confirmar que só mudou o que devia.

## Outros testes que valem os minutos

| Dúvida | Teste |
|---|---|
| Este balanço sai sem suporte? | Uma fatia fina da peça só com o balanço |
| Esta ponte sai? | Duas colunas e a ponte no vão real |
| A trava aguenta? | Só o braço da trava, na posição em que vai imprimir |
| O texto dá para ler? | Uma plaquinha com o texto no tamanho real |
| A rosca entra? | 10 mm de cada lado da rosca |

Corte o pedaço do próprio modelo (interseção com uma caixa) em vez de redesenhar: o teste vale porque é a mesma
geometria.

## O que dizer

Sem teste impresso, toda folga é estimativa: diga isso. Com teste, diga o número medido, em qual impressora e
material, e que ele vale para essa combinação.
