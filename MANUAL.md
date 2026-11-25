# Manual do Filuna CAD

Este manual ensina, passo a passo, a colocar o Filuna CAD na sua inteligência artificial e a usar cada parte
dele. Não precisa saber programar: na maior parte do tempo você só conversa com o assistente, e ele roda os
comandos. Os comandos estão aqui para você entender o que ele faz e para quem quiser rodar na mão.

**Sumário**

1. [O que é e como funciona](#parte-1-o-que-é-e-como-funciona)
2. [Colocar na sua IA](#parte-2-colocar-na-sua-ia)
3. [Instalar as ferramentas de conferência](#parte-3-instalar-as-ferramentas-de-conferência)
4. [Primeira conversa: o que pedir](#parte-4-primeira-conversa-o-que-pedir)
5. [Cada comando explicado](#parte-5-cada-comando-explicado)
6. [Ver a peça ao vivo](#parte-6-ver-a-peça-ao-vivo)
7. [Com a sua conta do Filuna](#parte-7-com-a-sua-conta-do-filuna)
8. [Problemas comuns](#parte-8-problemas-comuns)
9. [Palavras que aparecem no resultado](#parte-9-palavras-que-aparecem-no-resultado)

---

## Parte 1: o que é e como funciona

O Filuna CAD tem duas coisas:

- **Habilidades (skills):** textos que ensinam o assistente a modelar peças por código, projetar para imprimir,
  fatiar, e ir além da impressão (usinagem, injeção, chapa, simulação, desenho técnico, placas e robôs). Ficam
  na pasta [`skills/`](skills/). Cada habilidade é um arquivo `SKILL.md` com referências ao lado.
- **Ferramentas de conferência:** um programa em Python (`filuna_cad`) que mede a peça e devolve números,
  achados e uma nota de 0 a 100. Ficam em [`ferramentas/`](ferramentas/).

Como uma conversa corre:

```text
você pede            →  o assistente lê a habilidade certa
                     →  escreve o código da peça (OpenSCAD, Python ou build123d) e gera o arquivo
                     →  roda a conferência (python -m filuna_cad ...)
                     →  lê os números, corrige o desenho e confere de novo
                     →  mostra a você a peça, a nota e o que não foi conferido
```

A regra que vale em tudo: **número primeiro, opinião depois.** O assistente não deve dizer que a peça "está boa"
sem ter rodado a conferência, e deve dizer o que ela não prova (por exemplo, nada impresso é nada testado).

### A nota

Toda conferência devolve achados com gravidade:

| Gravidade | Quer dizer | Efeito na nota |
|---|---|---|
| `erro` | Do jeito que está, não imprime, não fabrica ou quebra | Reprova a peça e tira 25 pontos |
| `aviso` | Funciona, mas tem risco ou custo a mais | Tira 8 pontos |

"APROVADA" quer dizer que não achou erro **no que mede**. Não quer dizer que a peça funciona.

---

## Parte 2: colocar na sua IA

Escolha o seu assistente. A coluna "Conferido" diz o que nós testamos de verdade.

| Assistente | Como | Conferido |
|---|---|---|
| Claude Code (terminal, VS Code, aplicativo de computador) | Plugin, dois comandos | Sim: o plugin passa no `claude plugin validate` |
| Claude (claude.ai e aplicativo) | Enviar as habilidades em ZIP | Formato seguido, não testado em todas as contas |
| ChatGPT, Codex, Cursor, Gemini e outros | Arquivo `AGENTS.md` ou copiar as habilidades | Não testado: depende de cada programa |

### Claude Code

No terminal:

```bash
claude plugin marketplace add abcollicelli-web/filuna-cad
```

```bash
claude plugin install filuna-cad@filuna
```

Feche e abra o Claude Code. Para conferir, pergunte: *"Quais habilidades do Filuna CAD você tem?"*. Ele deve
citar `modelar`, `validar`, `engenharia` e as outras.

Para atualizar depois: `claude plugin update filuna-cad@filuna`.

### Claude (claude.ai e aplicativo)

1. No GitHub, abra [o repositório](https://github.com/abcollicelli-web/filuna-cad), clique em **Code** e em
   **Download ZIP**.
2. Descompacte. Dentro de `skills/` há uma pasta por habilidade.
3. Compacte cada pasta que você quer usar (por exemplo `skills/engenharia`) num ZIP próprio, com o `SKILL.md`
   dentro.
4. No Claude, vá em configurações, na parte de habilidades (Skills), e envie o ZIP. Repita para cada habilidade.

O Claude da web não roda programas no seu computador. Ele usa as habilidades para modelar e explicar; para os
números da conferência, rode os comandos você mesmo (Parte 3) ou ligue a conta do Filuna (Parte 7).

### ChatGPT, Codex, Cursor, Gemini e outros

- Programas que leem `AGENTS.md` na pasta do projeto (Codex, Cursor e outros): baixe o repositório e abra a
  pasta nele. O [`AGENTS.md`](AGENTS.md) aponta para cada habilidade.
- Programas com "instruções personalizadas" ou "projetos": envie os arquivos `SKILL.md` que for usar e as
  referências que eles citam, e escreva na instrução: *"Antes de modelar ou conferir uma peça, siga o SKILL.md
  correspondente."*

---

## Parte 3: instalar as ferramentas de conferência

Precisa do Python 3.10 ou mais novo ([python.org](https://www.python.org/downloads/); no Windows, marque
"Add Python to PATH" na instalação).

### Passo 1: uma pasta só para isso (recomendado)

Windows (PowerShell):

```powershell
python -m venv filuna
.\filuna\Scripts\Activate.ps1
```

Mac e Linux:

```bash
python3 -m venv filuna && source filuna/bin/activate
```

### Passo 2: instalar

Só a conferência de impressão:

```bash
pip install "git+https://github.com/abcollicelli-web/filuna-cad#subdirectory=ferramentas"
```

Com a parte de engenharia (STEP, simulação, desenho técnico, DXF, robótica):

```bash
pip install "filuna-cad[engenharia] @ git+https://github.com/abcollicelli-web/filuna-cad#subdirectory=ferramentas"
```

Peças com centenas de milhares de triângulos ficam muito mais rápidas com `pip install embreex`.

### Passo 3: programas de fora (só se for usar)

| Para | Instale | Confira com |
|---|---|---|
| `simular` | CalculiX: no Linux `sudo apt install calculix-ccx`; no Windows e no Mac, o pacote do [calculix.de](http://www.calculix.de), com o `ccx` no PATH | `ccx -v` |
| `pcb` | KiCad 8 ou mais novo: [kicad.org/download](https://www.kicad.org/download/) | `kicad-cli version` |
| Gerar peça `.scad` no `ver` | OpenSCAD: [openscad.org/downloads](https://openscad.org/downloads.html) | `openscad --version` |

### Passo 4: conferir a instalação

```bash
python -m filuna_cad --help
```

Deve listar `validar`, `orientar`, `vistas`, `comparar`, `raio-x`, `cupom`, `conferir`, `fabricar`,
`simular`, `desenho`, `pcb`, `robo` e `ver`.

Para provar que tudo funciona no seu computador, baixe o repositório e rode os testes (eles plantam defeitos e
conferem que cada um é achado; o que precisa de programa que você não instalou é pulado):

```bash
cd ferramentas && python -m pytest -q
```

---

## Parte 4: primeira conversa: o que pedir

Fale normalmente. Dê as medidas do que a peça segura ou encaixa: o assistente não deve inventar medida de peça
comprada. Exemplos que funcionam bem:

| Você quer | Peça assim |
|---|---|
| Modelar e imprimir | *"Modele um suporte de celular para mesa, celular de 8 mm de espessura, apoio a 65 graus. Valide antes de me mostrar."* |
| Saber se vai imprimir bem | *"Confira este STL para imprimir na minha A1 (256 x 256 x 256 mm) e diga a melhor posição na mesa."* |
| Mandar usinar | *"Esta peça em STEP dá para usinar numa CNC de 3 eixos? Quantas fixações e onde a fresa não chega?"* |
| Injetar | *"Analise esta caixa para injeção: tem rebaixo? Falta ângulo de saída?"* |
| Fazer em chapa | *"Este suporte pode ser de chapa dobrada? Qual a espessura e quanto pesa em aço?"* |
| Saber se aguenta | *"Prenda a base e ponha 5 kg em cima: a peça em PETG aguenta? Quanto entorta?"* |
| Desenho para orçar | *"Gere o desenho técnico em PDF deste suporte, material aço 1020, título Suporte de motor."* |
| Placa eletrônica | *"Rode o DRC desta placa KiCad e me dê o STEP dela para eu desenhar a caixa."* |
| Robô | *"Confira este URDF antes de eu abrir no simulador."* |

O que esperar de volta: a nota, os números principais, cada achado explicado em palavras simples, a mudança no
desenho que resolve, e o que a conferência não prova.

---

## Parte 5: cada comando explicado

Todos os comandos seguem o mesmo jeito:

```bash
python -m filuna_cad <comando> <arquivo> [opções] --texto
```

- Sem `--texto`, os comandos de engenharia devolvem JSON completo, que é o que o assistente lê.
- Com `--texto`, sai um resumo para gente ler.
- O comando termina com código 1 quando há erro, para servir em automação.
- Aceitam STL, 3MF, OBJ, GLB e STEP. STEP dá resultado mais exato (precisa do extra `engenharia`).

As saídas abaixo são reais, do [suporte de celular em forma de 4](exemplos/suporte-celular-4/) e dos
[exemplos de engenharia](exemplos/engenharia/), rodadas em 25/11/2026. Algumas linhas foram omitidas para
caber.

### validar: a peça imprime bem?

```bash
python -m filuna_cad validar peca.stl --mesa 256x256x256
```

Mede malha fechada, área apoiada na mesa, balanço que pede suporte, parede mais fina, se a peça tomba e se
cabe na impressora. Explicação completa em [`skills/validar`](skills/validar/SKILL.md). Junto com ele:
`orientar` (melhor das seis posições na mesa), `vistas` (folha com vistas e corte), `comparar` (duas peças
são a mesma?), `raio-x` (a peça bate com uma foto?) e `cupom` (teste de folga da sua impressora).

### conferir: o arquivo é o que diz ser?

```bash
python -m filuna_cad conferir suporte4_filuna.stl --texto
```

```text
APROVADA  nota 100/100  suporte4_filuna.stl
  formato: STL
  malhas: 1
  fechada: True
  faces para fora: True
  triangulos sem area: 0
  volume cm3: 520.848
  medidas mm: 160.0 x 110.0 x 80.0
```

Use antes de tudo, principalmente com arquivo que veio de outra pessoa. No STEP confere se a forma é válida e
tem sólido; no GLB, se a escala parece metro em vez de mm; no DXF, a unidade, contornos abertos e splines que
máquinas de corte não leem.

### fabricar cnc: dá para usinar?

```bash
python -m filuna_cad fabricar cnc suporte4_filuna.stl --texto
```

```text
APROVADA  nota 76/100  suporte4_filuna.stl
  processo: usinagem CNC 3 eixos
  bloco bruto mm: 164.0 x 114.0 x 84.0
  material removido: 0.668
  fixacoes: -Z, +Z
  area sem alcance mm2: 11.7
  sem alcance em: [36.9, 52.0, 11.2]
  cantos internos vivos mm: -Z 1120.0, +Z 1120.0
  [aviso] Possível: 11.7 mm² (só 1 ponto(s) da amostra) não são alcançados de nenhum dos 6 lados: ...
  [aviso] 1120.0 mm de canto interno vivo na fixação -Z: arredonde com raio maior que o da fresa.
```

Como ler:

- **fixacoes:** de quantos lados a peça precisa ser presa e usinada. Aqui, por cima e por baixo.
- **material removido 0.668:** dois terços do bloco viram cavaco.
- **cantos internos vivos:** a fresa é redonda e não faz canto interno reto. Arredonde esses cantos.
- **Possível... só 1 ponto:** a conferência usa pontos espalhados na superfície. Um ponto só pode ser engano
  rente a uma aresta, por isso vira aviso com o lugar (`sem alcance em`) para você olhar. Com três pontos ou
  mais vira erro.

### fabricar injecao: dá para fazer molde?

```bash
python -m filuna_cad fabricar injecao suporte4_filuna.stl --texto
```

```text
APROVADA  nota 68/100  suporte4_filuna.stl
  eixo de extracao: Z
  area sem saida mm2: 57315.6
  parede: mínima 3.57 mm, típica 20.0 mm
  [aviso] 57315.6 mm² de parede reta no sentido do molde: dê pelo menos 1 grau de saída.
  [aviso] Espessura muito desigual: a parte grossa encolhe mais e afunda ou empena.
  [aviso] Parede típica de 20.0 mm: acima de 4.0 mm afunda; esvazie com nervuras.
```

O suporte foi desenhado para impressão (maciço, paredes retas). Para injetar ele teria de ser oco, com paredes
de 1 a 4 mm, nervuras e paredes inclinadas. É isso que a conferência mostra.

### fabricar chapa: pode ser chapa dobrada?

```bash
python -m filuna_cad fabricar chapa peca.step --texto
```

Devolve a espessura, se ela é única (chapa tem uma espessura só), a área da chapa antes de dobrar e o peso em
aço, alumínio e inox. Uma chapa de 2 mm de teste foi medida como 2,0 mm.

### simular: aguenta a força?

```bash
python -m filuna_cad simular suporte4_filuna.stl --fixar zmin --forca-em zmax --forca 0,0,-20 --material pla --texto
```

```text
APROVADA  nota 100/100  suporte4_filuna.stl
  material: PLA impresso
  presa em: zmin
  forca em: zmax
  forca n: 0.0 x 0.0 x -20.0
  nos: 12827
  deslocamento max mm: 0.0008
  tensao max mpa: 0.17
  tensao 995 mpa: 0.03
  fator de seguranca 995: 1287.54
  fator pedido: 3.0
  [aviso] Peça impressa é mais fraca entre camadas: deite a peça para a força não puxar as camadas.
```

Como pedir:

- `--fixar` é a face presa e `--forca-em` a face onde a força é aplicada: `xmin`, `xmax`, `ymin`, `ymax`,
  `zmin` (a base) ou `zmax` (o topo).
- `--forca` é em newtons, nas direções X, Y e Z. **1 kg pesa cerca de 9,8 N**: 20 N são uns 2 kg. Para baixo é
  Z negativo.
- `--material`: `pla`, `petg`, `abs`, `asa`, `nylon`, `aco` ou `aluminio`.

Como ler: olhe o **fator de segurança 995** (99,5% da peça está abaixo dessa tensão). Para peça impressa ele
precisa passar de 3; para metal, de 1,5. Aqui 20 N num bloco maciço de 520 cm³ não fazem diferença.

A conta foi conferida contra a de livro: viga de aço de 100 x 10 x 10 mm presa numa ponta, 10 N na outra. O
livro dá 0,0195 mm de flecha; a simulação deu de 0,0191 a 0,0196 mm. Esse caso é um dos testes do repositório.

### desenho: folha técnica em PDF

```bash
python -m filuna_cad desenho suporte4_filuna.stl suporte4.pdf --titulo "Suporte de celular 4" --material PLA --texto
```

```text
  escala: 1:2
  vistas: frente, cima, lateral esquerda, perspectiva
  medidas mm: 160.0 x 110.0 x 80.0
  limites: Cotas gerais e diâmetros de furos verticais. Sem tolerâncias, rugosidade nem cotas de cada detalhe.
```

Folha A3 deitada no 1º diedro (o padrão no Brasil): frente, vista de cima embaixo dela, lateral esquerda à
direita, perspectiva, cotas gerais, diâmetro dos furos e legenda. Com `.png` no lugar de `.pdf`, sai em
imagem. Quem fabrica vai perguntar as tolerâncias: elas não saem daqui.

### pcb: placa KiCad

```bash
python -m filuna_cad pcb drc exemplos/engenharia/placa.kicad_pcb --texto
```

```text
REPROVADA  nota 59/100  placa.kicad_pcb
  medidas mm: 50.0 x 30.0
  camadas de cobre: 2
  violacoes: 3
  [erro] Clearance violation ( clearance 0.2000 mm; actual 0.0500 mm). Track [A] on F.Cu, length 40.0000 mm
  [aviso] Track has unconnected end. Track [A] on F.Cu, length 40.0000 mm
```

As mensagens vêm do próprio KiCad, em inglês. "Clearance violation" é distância entre trilhas menor que a regra:
aqui 0,05 mm onde o projeto pede 0,2 mm. Também há `pcb erc esquema.kicad_sch` (pino solto, saídas em curto) e
`pcb step placa.kicad_pcb placa.step` (a placa em 3D para desenhar a caixa em volta).

### robo: URDF, SRDF e MJCF

```bash
python -m filuna_cad robo exemplos/engenharia/braco.urdf --texto
```

```text
REPROVADA  nota 50/100  braco.urdf
  elos: 3
  juntas: 2
  raiz: base
  [erro] Junta cotovelo: limite inferior maior que o superior.
  [erro] Elo antebraco: inércia impossível (um momento maior que a soma dos outros dois).
```

Os dois erros foram plantados de propósito. Para SRDF passe também o URDF: `robo braco.srdf --urdf braco.urdf`.
Para MJCF (`.xml` do MuJoCo), o próprio MuJoCo compila o modelo e simula 500 passos.

---

## Parte 6: ver a peça ao vivo

```bash
python -m filuna_cad ver peca.py
```

Abre `http://localhost:8765` no navegador com a peça em 3D, a nota, as medidas e cada achado. A cada vez que
você (ou o assistente) salva o arquivo, a peça é refeita e conferida de novo.

| Arquivo | O que acontece |
|---|---|
| `peca.py` | O script roda com o caminho do STL de saída como primeiro argumento (`sys.argv[1]`) |
| `peca.scad` | O OpenSCAD gera a peça |
| STL, 3MF, OBJ, GLB, STEP | Só mostra e confere |

Exemplo de `peca.py` que funciona com o `ver`:

```python
import sys
import trimesh

trimesh.creation.box((30, 20, 10)).export(sys.argv[1])
```

Opções: `--porta 9000` para outra porta, `--sem-abrir` para não abrir o navegador. Se o script quebrar, a
página mostra o erro e espera o próximo salvamento. Roda só no seu computador.

---

## Parte 7: com a sua conta do Filuna

O plugin já traz o conector da IA Filuna. Com conta no [filuna3d.com](https://filuna3d.com), o assistente entra
com a sua permissão e passa a:

- ver impressoras, erros, estoque e pedidos;
- conferir no servidor do Filuna o arquivo que você enviou à Farm (`filuna_conferir_peca`), sem instalar nada
  no seu computador;
- analisar o mesmo arquivo para usinagem, injeção, chapa ou esforço (`filuna_analisar_engenharia`);
- fatiar com o perfil oficial da impressora e mandar imprimir **só depois do seu sim**.

Nas duas conferências pelo conector, o assistente recebe só números e avisos, nunca o arquivo. Modelos,
paramétricos e ferramentas do catálogo do Filuna são protegidos: não são conferidos nem entregues.

---

## Parte 8: problemas comuns

| Mensagem ou sintoma | Causa | O que fazer |
|---|---|---|
| `No module named filuna_cad` | A pasta do Passo 1 não está ativa, ou a instalação não rodou | Ative a pasta (`Activate.ps1` ou `source`) e rode o `pip install` de novo |
| `No module named build123d` (ou `gmsh`, `ezdxf`, `mujoco`) | Instalou sem o extra de engenharia | Rode o `pip install` com `[engenharia]` |
| `CalculiX (ccx) não está instalado` | O `simular` precisa do programa CalculiX | Instale (Parte 3) e confira com `ccx -v` |
| `O kicad-cli não está instalado` | O `pcb` precisa do KiCad 8 ou mais novo | Instale o KiCad e confira com `kicad-cli version` |
| `A peça não forma um volume fechado` | Malha aberta | Rode `conferir`; conserte a malha ou exporte de novo do programa de origem |
| Acentos estranhos no terminal do Windows | Terminal antigo | Use o Windows Terminal ou o PowerShell 7 |
| A simulação dá tensão zero | Presa e força na mesma face | Use faces diferentes em `--fixar` e `--forca-em` |
| Peça que mede menos de 5 mm em tudo | O arquivo está em metros (comum no GLB) | Exporte em mm ou multiplique a escala por 1000 |
| O assistente diz "está bom" sem números | Ele pulou a conferência | Peça: *"Rode a conferência e me mostre a nota e os achados."* |

---

## Parte 9: palavras que aparecem no resultado

| Palavra | Quer dizer |
|---|---|
| Malha fechada | A superfície não tem buracos: dá para saber o que é dentro e o que é fora |
| Balanço | Parte da peça no ar, inclinada mais que 45 graus: pede suporte na impressão |
| Fixação | Cada vez que a peça é presa na CNC para usinar um lado |
| Rebaixo | Parte que fica escondida: a fresa não alcança ou o molde não solta |
| Ângulo de saída | Inclinação da parede que deixa a peça sair do molde |
| Área planificada | Tamanho da chapa antes de dobrar |
| Tensão (MPa) | O quanto o material está sendo puxado ou apertado por dentro |
| Fator de segurança | Quantas vezes o material aguenta a mais que a força pedida |
| 1º diedro | Jeito de arrumar as vistas no desenho, o padrão no Brasil |
| DRC e ERC | Conferência de regras da placa e do esquema eletrônico |
| URDF, SRDF, MJCF | Arquivos que descrevem um robô para simuladores e planejadores |

Dúvida ou correção: abra uma issue no [GitHub](https://github.com/abcollicelli-web/filuna-cad/issues). Com
medida de peça impressa ou fabricada (máquina, material, resultado), melhor ainda.
