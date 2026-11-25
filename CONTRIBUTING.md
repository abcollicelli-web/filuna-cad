# Contribuir

O que mais ajuda é **medida de peça impressa**. Uma folga que funcionou vale mais do que dez regras teóricas.

## Receita ou número novo

Abra uma issue ou um pull request com:

- impressora, bico, material e altura de camada;
- o que foi desenhado (a folga, a parede, o ângulo) e o que saiu medido;
- o que aconteceu: entrou, ficou frouxo, quebrou, colou.

Números entram nas referências com a origem dita. Quando o seu número discorda do que está escrito, ele entra
como faixa: não apagamos a divergência.

## Texto

- Português simples, para quem imprime e não é engenheiro.
- Palavras próprias. Não copie texto de outros lugares.
- Diga os limites: o que a regra não cobre e o que não foi testado.

## Código

```bash
cd ferramentas
pip install -e ".[testes]"
python -m pytest -q
python testes/conferir_repositorio.py
```

Toda conferência nova do validador vem com um teste que planta o defeito e mostra que ela o acha.

## O que não entra

Código das ferramentas, paramétricos e modelos do site Filuna, arquivos de modelos protegidos, chaves e dados
de clientes.
