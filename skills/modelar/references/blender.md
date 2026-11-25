# Blender

Use para o que não se descreve com medidas: escultura, bichos, rostos, textura na superfície, reparo pesado de
malha e imagens de apresentação. Para peça com medida exata, os outros motores são melhores.

## Rodar sem abrir a janela

```bash
blender -b --factory-startup --python modelo.py -- argumento1 argumento2
```

- `--factory-startup` ignora a configuração da pessoa: o resultado é o mesmo em qualquer computador.
- Um processo novo por chamada, com limite de tempo. Trabalhe em cópias e com caminhos de saída explícitos.
- Os argumentos depois de `--` chegam ao script em `sys.argv`.

## Armadilhas

- **A unidade padrão é metro.** Antes de dar qualquer medida, defina a escala da cena para milímetro ou
  multiplique tudo por 0,001 de propósito, e confira o tamanho da peça depois de exportar.
- **Aplique a escala antes de qualquer corte** (`transform_apply`). Escala não aplicada, principalmente
  diferente em cada eixo, estraga o resultado do corte.
- **Objeto ativo e seleção são coisas diferentes,** e muitos comandos mudam os dois. Defina os dois antes de
  cada operação.
- **Comando no modo errado falha calado.** Confira se está em modo objeto ou modo edição.
- **Corte entre malhas:** tente o modo exato primeiro e, se ele destruir a peça, o modo rápido. Fure antes de
  cortar em pedaços. Confira o volume depois.
- **O que você vê não é o que exporta** se houver modificadores não aplicados. Aplique-os ou exporte a malha
  avaliada.
- **Só malha vai para o arquivo.** Antes de exportar, apague os objetos usados como cortador, câmeras e luzes.
- **Peça com mais de uma casca** depois de somar relevos: una tudo, tire vértices duplicados e feche os buracos
  antes de exportar. Fundo de rebaixo no mesmo plano de outra face gera malha aberta: afunde 0,05 mm a mais.

## Quando esculpir não é a resposta

Pedido de peça "idêntica" a uma referência com contorno definido (logo, silhueta, objeto técnico) se resolve
melhor traçando o contorno da imagem e extrudando do que esculpindo à mão: o contorno traçado se mede contra a
referência, a escultura não. Veja [A partir de imagem](a-partir-de-imagem.md).

## Imagens para conferir

Render simples (Workbench) com vista ortográfica de frente, de cima e de lado, sempre na mesma câmera, para as
versões poderem ser comparadas uma com a outra e com a referência. Fundo escuro para peça clara.

## Malha gerada por IA

Uma malha que saiu de um gerador de imagem para 3D não tem tamanho real, costuma ter buracos e não tem o verso
nem o interior certos. Antes de imprimir: feche, una, tire o que está solto, ponha na escala em milímetros com
uma medida que a pessoa confirmou, e crie uma base plana para ela apoiar na mesa.
