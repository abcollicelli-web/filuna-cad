# Escolher o motor

Não existe motor melhor: existe o motor certo para o tipo de peça. Escolha pelo tipo, não pelo costume.

## Por tipo de peça

| Tipo de peça | Motor | Por quê |
|---|---|---|
| Peça mecânica sob medida (suporte, gancho, adaptador) | OpenSCAD, ou Python com Manifold | Poucas linhas, tudo por parâmetro, malha sempre fechada |
| Perfil 2D extrudado (letra, número, silhueta, placa) | Python: shapely para o perfil, Manifold para extrudar | O perfil se mede e se corrige em 2D antes de virar 3D |
| Caixa para eletrônica, peça com arredondamento e chanfro em tudo | build123d | Arredonda arestas de verdade e exporta STEP editável |
| Peça que outra pessoa vai editar num CAD | build123d (STEP) | STL e 3MF não se editam com medida |
| Vaso, taça, peça de revolução | OpenSCAD (`rotate_extrude`) ou build123d (`revolve`) | Um perfil e um giro |
| Logo, foto ou desenho que vira relevo ou peças por cor | Ferramenta pronta do Filuna; por código, Canvas 2D + earcut | Tirar fundo e separar cor é trabalho de imagem, não de CAD |
| Forma orgânica, bicho, rosto, escultura | Blender | Motores de CAD são ruins em forma livre |
| Textura na superfície (couro, madeira, colmeia) | Ferramenta Texturizador do Filuna; ou Blender (deslocamento) | Mexe em milhares de triângulos |
| Peça articulada impressa já montada | OpenSCAD ou build123d, com cada elo como sólido separado | A folga entre os sólidos precisa ser exata e medida |
| Arte plana em várias cores | Python: um sólido por cor num 3MF | Cada cor vira um objeto que o fatiador liga a um filamento |
| Mudar ou consertar um STL existente | Python: trimesh + Manifold | Importa a malha e corta ou soma em volta; não se redesenha |
| Peça igual no navegador e no servidor | three.js + earcut | É o motor dos paramétricos do Filuna |

## O que cada motor entrega

| Motor | Forte em | Fraco em | Sai em |
|---|---|---|---|
| **OpenSCAD** | Peças por soma e corte, parâmetros, biblioteca BOSL2 (roscas, engrenagens, dobradiças) | Arredondar aresta, forma livre, não gera STEP | STL, 3MF, PNG |
| **Manifold** (Python ou JavaScript) | União e corte que nunca abrem a malha, muito rápido | Não arredonda aresta | malha |
| **shapely + trimesh** | Perfil 2D com conta exata, extrusão, medir e consertar malha | Não é CAD: não tem "aresta" para arredondar | STL, 3MF, OBJ |
| **build123d** | Arredondamento, chanfro, casca, corte exato, montagem | Mais lento, falha em raios impossíveis | STEP, STL, 3MF |
| **three.js + earcut** | Mesma geometria no navegador e no servidor, pré-visualização ao vivo | Soma e corte de sólidos (use Manifold junto) | malha |
| **Canvas 2D** | Ler imagem, tirar fundo, separar cor, desenhar texto | Só 2D | pixels, contornos |
| **Blender** | Escultura, textura, render, reparo pesado | Peça com medida exata | STL, 3MF, PNG |

## Regras de decisão

1. Se a ferramenta pronta do Filuna faz, use a ferramenta.
2. Se a peça é um perfil que sobe reto, faça em 2D e extrude: é o caminho com menos erro.
3. Se precisa de arredondamento em muitas arestas ou de STEP, vá de build123d.
4. Se a forma não se descreve com medidas, vá de Blender e depois ajuste a escala em milímetros.
5. Na dúvida entre dois motores, faça nos dois e compare com `filuna_cad comparar`: sobreposição 1,0 prova que a
   peça é a mesma e que o erro não é do motor.

## Passar de um motor para outro

Cada troca de programa é uma chance de errar a escala. Depois de cada passagem, confira as medidas da caixa da
peça: o Blender trabalha em metros por padrão, o STL não guarda unidade, e uma malha gerada por IA não tem
tamanho real nenhum.
