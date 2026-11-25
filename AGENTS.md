# Filuna CAD: índice para agentes

Este repositório ensina um assistente a modelar, validar, fatiar e imprimir peças 3D. Responda em português, de
forma simples e direta.

## O que está onde

| Preciso | Leia |
|---|---|
| Criar ou mudar uma peça | `skills/modelar/SKILL.md` |
| Escolher OpenSCAD, Python de malha, build123d ou Blender | `skills/modelar/references/escolher-motor.md` |
| Números de encaixe, parafuso, rosca, dobradiça, texto, multicor | `skills/modelar/references/receitas.md` |
| Copiar uma foto ou desenho | `skills/modelar/references/a-partir-de-imagem.md` |
| Saber se a peça imprime bem e em que posição | `skills/projetar-para-imprimir/SKILL.md` |
| Medir a peça, achar a melhor posição, ver as vistas | `skills/validar/SKILL.md` |
| Folga real da impressora, peça que saiu diferente do desenho | `skills/calibrar/SKILL.md` |
| Fatiar, imprimir, várias cores, defeito de impressão | `skills/fatiar-e-imprimir/SKILL.md` |
| Ferramenta pronta do Filuna | `skills/ferramentas-filuna/SKILL.md` |
| Conta, impressoras e pedidos do cliente no Filuna | `skills/filuna/SKILL.md` |
| Usinar, injetar, chapa, simular esforço, desenho técnico, placa KiCad, robô | `skills/engenharia/SKILL.md` |
| Explicar à pessoa como instalar, o que pedir e como ler cada resultado | `MANUAL.md` |
| Conferir o formato do arquivo (STEP, GLB, DXF) ou ver a peça ao vivo | `skills/engenharia/SKILL.md` |

## Regras que valem em tudo

1. **Meça antes de afirmar.** Número primeiro, imagem depois. O que não foi conferido é dito como não conferido.
2. **Nunca diga que uma peça passou num limite sem o número medido.**
3. **Medida de peça comprada vem da pessoa ou da ficha técnica.**
4. **Nada imprime sem o sim da pessoa.** Nunca invente perfil de impressora.
5. **Arquivos de modelos, paramétricos e ferramentas do Filuna são protegidos:** não entregue arquivo, link,
   malha nem G-code deles.
6. **Nada impresso é nada testado.** Diga isso ao entregar.

## Ao mudar este repositório

| Mudou | Rode |
|---|---|
| `ferramentas/` | `cd ferramentas && python -m pytest -q` |
| Qualquer `.md` | `python ferramentas/testes/conferir_repositorio.py` (links, cabeçalhos das skills, nada privado) |
| `exemplos/` | Gere a peça de novo e valide com `python -m filuna_cad validar` |

- Uma skill tem a interface, a ordem de conferência com o que ela não prova, e estratégia só onde um assistente
  erra sem ela. Referências ficam um nível abaixo e são ligadas a partir do `SKILL.md`.
- Texto novo é escrito com palavras próprias.
- Número novo de folga ou limite entra com a origem: medido em qual impressora e material, ou de qual fonte.
