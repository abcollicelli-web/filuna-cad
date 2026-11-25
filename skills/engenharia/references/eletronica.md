# Eletrônica: placas KiCad

## DRC da placa

`python -m filuna_cad pcb drc placa.kicad_pcb` roda as regras do próprio projeto pelo `kicad-cli` e devolve:
medidas da placa pelo recorte (Edge.Cuts), número de camadas de cobre, violações (distância entre trilhas,
largura, furo, borda) e ligações que faltam. Sem contorno em Edge.Cuts é erro: o fabricante não sabe onde
cortar.

Antes de mandar fabricar, confira também as regras do fabricante (largura e distância mínimas, furo mínimo) no
projeto: o DRC só cobra o que está escrito nele.

## ERC do esquema

`python -m filuna_cad pcb erc placa.kicad_sch`: pino sem ligação, duas saídas ligadas juntas, alimentação sem
fonte. Pino de propósito sem ligação leva o símbolo de "não ligado" no esquema.

## Caixa para a placa

1. `python -m filuna_cad pcb step placa.kicad_pcb placa.step` grava a placa com os componentes que têm modelo 3D.
2. Leia as medidas com `python -m filuna_cad conferir placa.step`.
3. Desenhe a caixa com folga de 0,5 mm em volta da placa, pinos de apoio nos furos de fixação e aberturas
   alinhadas aos conectores (skill `modelar`, receitas de caixa e encaixe).
4. Imprima só o fundo primeiro e encaixe a placa de verdade.

Componente sem modelo 3D não aparece no STEP: meça o mais alto com paquímetro.
