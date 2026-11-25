# Robótica: URDF, SRDF e MJCF

## URDF

`python -m filuna_cad robo robo.urdf` confere:

| Regra | Por quê |
|---|---|
| Uma raiz só e cada elo com um pai só | URDF é árvore; elo solto ou com dois pais quebra o carregamento |
| Nomes de elo únicos, juntas ligando elos que existem | Erro de digitação some sem aviso em muitos programas |
| Tipo de junta válido, eixo não nulo | Eixo 0 0 0 faz a junta girar em torno de nada |
| Junta `revolute` e `prismatic` com limite, inferior menor que superior | Sem limite o planejador rejeita |
| Massa positiva e inércia possível | Inércia não positiva ou com um momento maior que a soma dos outros dois explode a simulação |
| Malhas que existem | Caminho relativo é a partir da pasta do URDF; `package://` não é conferido |

Inércia de uma caixa de massa m e lados a, b, c: ixx = m(b²+c²)/12, iyy = m(a²+c²)/12, izz = m(a²+b²)/12.
Calcule pela peça modelada (`trimesh` dá `moment_inertia`) em vez de chutar.

## SRDF (MoveIt)

`python -m filuna_cad robo robo.srdf --urdf robo.urdf`: grupos, correntes, poses e pares sem colisão só podem
citar elos, juntas e grupos que existem no URDF.

## MJCF (MuJoCo)

`python -m filuna_cad robo cena.xml`: o próprio MuJoCo compila o modelo e simula 500 passos. Reprova se não
compila ou se a simulação vira NaN; avisa cada alerta do MuJoCo (contato demais, aceleração instável). Devolve
corpos, juntas, atuadores e massa total.

## Peças do robô

As peças impressas do robô passam pelas skills `projetar-para-imprimir` e `validar`, e as que levam carga pela
simulação. Exporte cada elo em STL no mesmo referencial da junta: a origem do arquivo é a origem do elo.
