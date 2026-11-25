---
name: engenharia
description: Engenharia além da impressão 3D - análise de fabricação por usinagem CNC de 3 eixos, injeção plástica e chapa metálica; simulação estrutural com CalculiX (deformação, tensão, fator de segurança); folha de desenho técnico cotada em PDF; placas KiCad (DRC, ERC, STEP da placa para a caixa); e conferência de robôs em URDF, SRDF e MJCF do MuJoCo. Use quando pedirem para fabricar de outro jeito que não imprimir, saber se a peça aguenta uma força, gerar desenho técnico, conferir uma placa eletrônica ou a descrição de um robô.
---

# Engenharia além da impressão

Cada comando mede e devolve achados com gravidade e nota, como o `validar`. Rode o que a pergunta pede, leia
os números e só então responda. Todos aceitam STL, 3MF, OBJ, GLB e STEP; STEP dá resultado mais exato.

## Preparar

```bash
pip install "filuna-cad[engenharia] @ git+https://github.com/abcollicelli-web/filuna-cad#subdirectory=ferramentas"
```

Simular precisa do CalculiX no sistema (`apt install calculix-ccx`, ou o `ccx` no PATH). Placas precisam do
KiCad 8 ou mais novo (`kicad-cli`).

## O que cada comando responde

| Pergunta | Comando | Referência |
|---|---|---|
| Dá para usinar? Quantas fixações? Onde a fresa não chega? | `python -m filuna_cad fabricar cnc peca.step` | [fabricação](references/fabricacao.md) |
| Dá para injetar? Tem rebaixo, falta saída, parede desigual? | `python -m filuna_cad fabricar injecao peca.step` | [fabricação](references/fabricacao.md) |
| É chapa? Qual espessura, área planificada e peso? | `python -m filuna_cad fabricar chapa peca.step` | [fabricação](references/fabricacao.md) |
| Aguenta a força? Quanto entorta? | `python -m filuna_cad simular peca.step --fixar zmin --forca-em zmax --forca 0,0,-100 --material pla` | [simulação](references/simulacao.md) |
| Preciso de um desenho para orçar ou mandar fazer | `python -m filuna_cad desenho peca.step folha.pdf --titulo "Suporte" --material "Aço 1020"` | abaixo |
| A placa passa nas regras? Qual o tamanho? | `python -m filuna_cad pcb drc placa.kicad_pcb` | [eletrônica](references/eletronica.md) |
| O esquema tem pino solto ou saída em curto? | `python -m filuna_cad pcb erc placa.kicad_sch` | [eletrônica](references/eletronica.md) |
| Quero a placa em 3D para desenhar a caixa | `python -m filuna_cad pcb step placa.kicad_pcb placa.step` | [eletrônica](references/eletronica.md) |
| O URDF, SRDF ou MJCF do robô está certo? | `python -m filuna_cad robo robo.urdf` | [robótica](references/robotica.md) |
| O arquivo é o que diz ser? | `python -m filuna_cad conferir peca.step` (também STL, 3MF, GLB, DXF) | abaixo |
| Quero ver a peça mudando enquanto edito | `python -m filuna_cad ver peca.py` | abaixo |

## Ordem de trabalho

1. **Confira o arquivo** (`conferir`). Sólido inválido ou malha aberta estraga tudo o que vem depois.
2. **Escolha o processo pela quantidade e pelo material**, não pelo hábito: 1 a 50 peças em plástico, imprimir;
   peças de metal ou de precisão, usinar; milhares de peças de plástico, injetar; metal fino dobrado, chapa.
3. **Rode a análise do processo** e corrija o desenho até não sobrar erro.
4. **Simule** se a peça segura carga. Simule na pior situação real, não na média.
5. **Gere o desenho** para quem vai fabricar, e diga o que ele não traz (tolerâncias).

## Desenho técnico

Folha A3 deitada no 1º diedro: frente, vista de cima embaixo dela, lateral esquerda à direita, perspectiva sem
escala, cotas gerais, diâmetro dos furos verticais e legenda com título, material, escala e data. Arestas
visíveis em traço cheio, escondidas em tracejado. A escala é escolhida entre as normais (1:1, 1:2, 2:1, 1:5…).
Com saída `.png` em vez de `.pdf` sai a mesma folha em imagem, para olhar antes de mandar.

Não traz tolerância, rugosidade, rosca nem cota de cada detalhe: quem fabrica vai perguntar. Diga isso ao
entregar.

## Conferência formal pelo formato

| Formato | O que confere |
|---|---|
| STEP | Forma válida no núcleo de CAD, quantos sólidos, cascas abertas, volume |
| STL, 3MF, OBJ | Malha fechada, faces viradas para fora, triângulos sem área, volume |
| GLB | O mesmo da malha, número de materiais, e se a escala parece metro em vez de mm |
| DXF | Unidade (corte espera mm), polilinhas abertas, pontas soltas, splines que máquina não lê |

## Ver ao vivo

`python -m filuna_cad ver peca.py` abre `http://localhost:8765` com a peça em 3D, a nota e os achados do
`validar`. A cada vez que o arquivo é salvo a peça é refeita e conferida de novo. Um script `.py` recebe o
caminho do STL de saída como primeiro argumento; `.scad` é gerado pelo OpenSCAD; STL, 3MF, GLB e STEP só são
mostrados. Se o script quebrar, a página mostra o erro e espera o próximo salvamento.

## O que nada disto prova

- A análise de fabricação mostra o que o processo não alcança; não faz orçamento nem escolhe ferramenta.
- A simulação é linear e com material maciço: não prevê fadiga, impacto, flambagem nem a força real de uma
  peça impressa. Fator de segurança pedido: 3 para peça impressa, 1,5 para metal.
- DRC e ERC são as regras do próprio projeto KiCad: regra errada passa.
- Robô que compila pode estar com medidas erradas. Compare com o robô de verdade.
