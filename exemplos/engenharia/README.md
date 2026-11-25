# Exemplos de engenharia

Arquivos pequenos com defeitos plantados, para você ver cada conferência funcionando. O passo a passo e a saída
esperada estão no [manual](../../MANUAL.md#parte-5-cada-comando-explicado).

| Arquivo | Defeito de propósito | Comando |
|---|---|---|
| `braco.urdf` | Limite da junta invertido e inércia impossível | `python -m filuna_cad robo braco.urdf --texto` |
| `placa.kicad_pcb` | Duas trilhas a 0,05 mm uma da outra (a regra pede 0,2 mm) | `python -m filuna_cad pcb drc placa.kicad_pcb --texto` |
