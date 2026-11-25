---
name: fatiar-e-imprimir
description: Fatia uma peça e leva até a impressora com segurança - pelo Filuna (conta, Farm e Filuna Slicer) ou pela linha de comando do OrcaSlicer - conferindo tempo, gramas, suporte e trocas de cor antes de imprimir, e diagnostica defeitos de impressão. Use quando pedirem para fatiar, imprimir, estimar tempo ou filamento, preparar um 3MF em várias cores, ou quando uma impressão sair com defeito.
---

# Fatiar e imprimir

Fatiar transforma a peça em instruções para uma impressora específica. O resultado só vale para aquela
impressora, aquele bico e aquele filamento: perfil errado pode danificar a máquina.

## Regras que não mudam

1. **Nunca invente nem empreste um perfil.** Tamanho de mesa ou temperatura errados podem quebrar a impressora.
   Use o perfil que a pessoa imprime, ou o perfil oficial da impressora dela.
2. **Nada imprime sem o sim da pessoa**, dado depois de ver o resumo: impressora, material, cor, tempo e gramas.
3. **"Enviado" não é "imprimindo".** Só diga que a impressão começou se a impressora confirmar.
4. **Ninguém prova pela conversa que a mesa está limpa.** Pergunte, e peça alguém por perto na primeira camada.
5. **Se o fatiamento falhar, não envie o arquivo sem fatiar como alternativa**, e não repita o envio sozinho.
6. **Não mexa** em G-code de início e fim, scripts de pós-processamento ou chaves de conexão da impressora.

## Pelo Filuna

Com o conector Filuna ligado (skill `filuna`), o caminho é o mais curto e usa o perfil oficial da impressora do
cliente:

1. A pessoa envia o arquivo em Farm › Novo pedido, no site (o Claude não entrega anexo a conectores).
2. `filuna_pedido` mostra peças, tempo, gramas e camadas quando o cálculo termina.
3. `filuna_configurar_pedido` muda material, cópias e cores, só no que a pessoa aceitar.
4. `filuna_preparar_impressao` devolve o resumo e um código; com o sim, `filuna_confirmar_impressao`.
5. A impressora começa com a mesa limpa e o Filuna Slicer aberto no computador.

## Pela linha de comando do OrcaSlicer

```bash
orca-slicer peca.stl \
  --load-settings "processo.json;impressora.json" \
  --load-filaments "filamento.json" \
  --arrange 1 --slice 0 \
  --outputdir /caminho/absoluto/saida --export-3mf peca.gcode.3mf
```

- `--outputdir` precisa de caminho absoluto. `--info` mostra o tamanho da peça.
- **O jeito mais seguro é um projeto 3MF salvo pelo programa** (Arquivo › Salvar projeto): ele carrega modelos e
  todos os ajustes.
- **Um perfil guardado só tem as diferenças em relação ao perfil pai.** Dependendo da versão, a linha de
  comando não busca o pai e fatia com valores padrão, sem avisar. Confira no fim do G-code se a impressora, o
  bico e as temperaturas são os esperados.
- Com mais de um filamento, a lista de cores precisa ter uma entrada por filamento, ou o programa cai.
- A matriz de purga tem N × N valores para N filamentos (9 para 3). Tamanho errado dá "configurações inválidas".
- A partir do OrcaSlicer 2.5 os perfis do sistema ficam em arquivos binários: use projeto 3MF.

Mais ajustes e multicor em [Fatiador](references/fatiador.md).

## Conferir o fatiamento antes de imprimir

| Leia | Desconfie quando |
|---|---|
| Tempo | Muito maior que o esperado: suporte demais, camada fina demais, muitas trocas de cor |
| Gramas (peça, suporte, purga, torre) | Purga e torre pesam mais que a peça |
| Suporte | Existe, e a validação tinha dado balanço zero: a posição mudou |
| Camadas e altura | Não batem com a altura da peça dividida pela camada |
| Trocas de filamento | Centenas: redesenhe as cores |
| Avisos do fatiador | Qualquer um: leia antes de seguir |

- Qualquer mudança invalida o fatiamento: fatie de novo antes de falar em tempo e gramas.
- Número que o fatiador não deu é desconhecido, não é zero.
- Para escolher entre duas configurações, fatie as duas e compare com números.

## Quando a impressão sai com defeito

Peça uma foto, pergunte material e impressora, e use o [catálogo de problemas](references/problemas.md): do
sintoma às causas em ordem de probabilidade. Proponha uma mudança de cada vez. Com o conector Filuna,
`filuna_explicar_erro` traz a ficha do fabricante para o código de erro da impressora: repasse o texto oficial,
não adivinhe a causa.
