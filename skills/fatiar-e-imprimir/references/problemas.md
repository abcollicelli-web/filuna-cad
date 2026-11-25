# Catálogo de problemas de impressão

Do sintoma às causas, da mais provável para a menos provável. Mude uma coisa por vez e imprima um teste pequeno.

As linhas marcadas com (geral) são conhecimento comum de impressão 3D que ainda não conferimos em impressora:
trate como ponto de partida.

| Sintoma | Causas, em ordem | O que fazer |
|---|---|---|
| **Cantos levantam da mesa** | Mesa fria; ventilador cedo demais; corrente de ar; pouco apoio | Subir a mesa, ventilador desligado nas 2 ou 3 primeiras camadas, fechar a impressora, aba de 5 a 10 mm, arredondar os cantos |
| **Primeira camada não gruda** | Altura do bico ou nivelamento; rápido demais; frio demais; mesa suja | Nivelar, 15 a 25 mm/s, 5 a 10 °C a mais, fio 105 a 120% do bico, limpar com álcool isopropílico |
| **Base mais larga que o resto** | Bico perto demais; mesa quente demais; sem compensação | Subir a primeira camada, mesa 5 °C mais fria, compensação de 0,1 a 0,2 mm por lado, chanfro no desenho |
| **Fiapos entre partes** | Quente demais; retração curta ou lenta; filamento úmido | Baixar de 5 em 5 °C, retração 0,2 a 0,5 mm maior, deslocamento mais rápido, secar a bobina |
| **Falta plástico, camada rala** | Velocidade acima do que o bico derrete; frio demais; bico meio entupido; fluxo baixo | Reduzir a velocidade naquele trecho ou subir a temperatura, limpar o bico, calibrar o fluxo |
| **Sobra plástico, superfície empelotada** (geral) | Fluxo alto | Calibrar o fluxo |
| **Balanço caído, ponte feia** | Pouca ventilação; quente demais; parede externa rápida; ângulo além do limite | Mais ventilador, menos temperatura, parede externa mais lenta, camada mais fina, suporte, ou mudar o desenho |
| **Peça abre entre camadas** | Frio demais para a velocidade; camada grossa demais; ventilador demais; filamento úmido | Subir a temperatura, camada abaixo de 65% do bico, menos ventilador, secar |
| **Ondas na parede depois de cantos** | Velocidade ou aceleração fazendo a máquina vibrar; correia frouxa | Baixar a aceleração da parede externa, calibrar a compensação de vibração, apertar correias |
| **Bolinha na costura** | Posição da costura; retração ou avanço de pressão desajustados | Costura atrás ou alinhada, limpar o bico na saída, ajustar retração |
| **Detalhe pequeno derretido** | Camada rápida demais para esfriar | Subir o tempo mínimo de camada, imprimir várias peças juntas |
| **Estalos, superfície áspera, fiapo que nada resolve** | Filamento úmido | Secar a bobina; nenhum ajuste conserta |
| **Suporte grudado na peça** (geral) | Distância entre suporte e peça pequena; interface densa | Aumentar a distância de cima do suporte; suporte em árvore |
| **Camada deslocada para o lado** (geral) | Correia ou polia frouxa; bico bateu numa parte levantada; aceleração alta | Apertar correias e polias, resolver o empenamento, baixar a aceleração |
| **Bico entupido** | Entupimento parcial; (geral) calor subindo pelo bico, sujeira | Limpeza a frio ou troca do bico |
| **Faixas regulares na altura** (geral) | Fuso do eixo Z, eixo preso, temperatura oscilando | Limpar e lubrificar o fuso, conferir o eixo, estabilizar a temperatura |
| **Esquenta e não extruda** | G-code de início de outra impressora | Fatiar de novo com o perfil certo |
| **Furos menores, encaixe não entra** | Espalhamento do fio; furo é polígono; sem compensação | Compensação de furo no fatiador ou 0,2 mm no desenho (nunca os dois); imprimir pedaço de teste |

## Antes de mexer em ajuste

1. **O filamento está seco?** Metade dos defeitos de superfície é umidade.
2. **A mesa está limpa e nivelada?**
3. **O perfil é o da impressora e do filamento certos?**
4. **O defeito aparece numa altura específica?** Então olhe o que a peça tem naquela altura: balanço, ponte,
   detalhe fino, mudança de área.

## Código de erro da impressora

Repasse o código e o texto oficial do fabricante. Não adivinhe a causa, e não limpe falha de máquina
automaticamente: quem confirma que o problema físico foi resolvido é a pessoa que está na frente dela.
