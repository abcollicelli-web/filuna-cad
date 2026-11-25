// Suporte de celular em forma de "4", três ângulos (55, 65 e 82 graus).
// Perfil no plano XY, extrudado em Z; imprime deitado sobre a face do número, sem suporte.

PROFUNDIDADE = 80;      // largura do apoio (eixo Z ao imprimir)
FENDA = 11;             // abertura para celular com capa
FUNDO = 10;             // profundidade vertical da fenda
CANTO = [70, 110];      // quina do topo da haste onde o celular encosta

module quatro() {
    union() {
        translate([20, 0]) square([140, 16]);   // pé
        translate([50, 0]) square([20, 110]);   // haste
        translate([0, 34]) square([94, 18]);    // barra
        polygon([[0, 34], [22, 34], [70, 92], [70, 110], [50, 110], [0, 52]]);  // diagonal
    }
}

// Fenda cuja face de trás passa pela quina CANTO, saindo da superfície y_sup no ângulo a.
module fenda(y_sup, a) {
    x = CANTO[0] + (CANTO[1] - y_sup) / tan(a);
    translate([x, y_sup]) rotate(90 - a)
        translate([0, -FUNDO / sin(a)]) square([FENDA, FUNDO / sin(a) + 40]);
}

linear_extrude(PROFUNDIDADE)
    difference() {
        quatro();
        fenda(16, 55);
        fenda(16, 65);
        fenda(52, 82);
    }
