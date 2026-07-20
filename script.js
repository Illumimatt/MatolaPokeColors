document.addEventListener("DOMContentLoaded", function() {
    // ==========================================
    // 1. LÓGICA DO MODAL DE FILTROS
    // ==========================================
    const btnAbrir = document.getElementById("btn-abrir-filtros");
    const btnFechar = document.getElementById("btn-fechar-filtros");
    const overlay = document.getElementById("modal-overlay");

    // Verifica se os botões do modal existem antes de adicionar o evento
    if (btnAbrir && btnFechar && overlay) {
        btnAbrir.addEventListener("click", function() {
            overlay.classList.add("mostrar");
        });

        btnFechar.addEventListener("click", function() {
            overlay.classList.remove("mostrar");
        });

        overlay.addEventListener("click", function(event) {
            if (event.target.id === 'modal-overlay') {
                overlay.classList.remove("mostrar");
            }
        });
    }

    // ==========================================
    // 2. LÓGICA DAS CORES DINÂMICAS
    // ==========================================
    const btnAddCor = document.getElementById('btn-add-cor');
    const listaCores = document.getElementById('lista-cores');

    // Adiciona o # caso o usuário não tenha colocado (ex: colou "7A59C7" em vez de "#7A59C7")
    function normalizarHex(valor) {
        let v = (valor || '').trim();
        if (v && !v.startsWith('#')) {
            v = '#' + v;
        }
        return v.toUpperCase();
    }

    // Valida de verdade: exatamente # seguido de 6 dígitos hexadecimais (0-9, A-F)
    function hexValido(v) {
        return /^#[0-9A-F]{6}$/.test(v);
    }

    // Função para manter o color picker e o texto sincronizados
    function sincronizarInputs(linha) {
        const corInput = linha.querySelector('.cor-input');
        const hexInput = linha.querySelector('.hex-input');
        
        if (!corInput || !hexInput) {
            return; 
        }

        // Guarda o último valor válido conhecido, pra poder reverter se o
        // usuário digitar/colar algo inválido
        hexInput.dataset.ultimoValido = corInput.value.toUpperCase();

        corInput.addEventListener('input', (e) => {
            const novoHex = e.target.value.toUpperCase();
            hexInput.value = novoHex;
            hexInput.dataset.ultimoValido = novoHex;
        });

        // Enquanto digita/cola: normaliza (adiciona # se faltar) e, se já
        // ficou um hex válido, atualiza o color picker em tempo real
        hexInput.addEventListener('input', (e) => {
            const normalizado = normalizarHex(e.target.value);
            if (normalizado !== e.target.value) {
                e.target.value = normalizado;
            }
            if (hexValido(normalizado)) {
                corInput.value = normalizado;
                hexInput.dataset.ultimoValido = normalizado;
            }
        });

        // Ao sair do campo: se o valor final não for um hex válido,
        // volta pro último valor válido (não deixa o campo "quebrado")
        hexInput.addEventListener('blur', (e) => {
            const normalizado = normalizarHex(e.target.value);
            if (hexValido(normalizado)) {
                e.target.value = normalizado;
                corInput.value = normalizado;
                hexInput.dataset.ultimoValido = normalizado;
            } else {
                e.target.value = hexInput.dataset.ultimoValido;
            }
        });

        // Enter também confirma/valida, sem precisar clicar fora do campo
        hexInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                hexInput.blur();
            }
        });
    }

    document.querySelectorAll('#lista-cores .color-row').forEach(sincronizarInputs);
    
    if (btnAddCor && listaCores) { 
        btnAddCor.addEventListener('click', () => {
            const novaLinha = document.createElement('div');
            novaLinha.className = 'color-row';

            const corAleatoria = '#' + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0').toUpperCase();
            
            novaLinha.innerHTML = `
                <input type="color" class="cor-input" value="${corAleatoria}">
                <input type="text" class="hex-input" value="${corAleatoria}" maxlength="8">
                <button class="btn-excluir">X</button>
            `;

            // Agora o listaCores com certeza existe!
            listaCores.appendChild(novaLinha);
            
            // Sincroniza a nova linha gerada
            sincronizarInputs(novaLinha);
        });
    }
    // ==========================================
    // 3. LÓGICA DE EXCLUIR COR
    // ==========================================
    if (listaCores) {
        listaCores.addEventListener('click', (e) => {
            // Verifica se o clique foi no botão de excluir
            if (e.target.classList.contains('btn-excluir')) {
                
                // Remove a div da linha inteira
                e.target.closest('.color-row').remove();
                
                // Dispara um evento de "input" falso para o Python perceber
                // que a lista mudou e atualizar as imagens na mesma hora!
                const eventoInput = new Event('input', { bubbles: true });
                listaCores.dispatchEvent(eventoInput);
            }
        });
    }
});

// ==========================================
// 4. BUSCA DE NOME DE COR (movida do Python pro JS por performance)
// ==========================================

// Guarda o banco de ~32 mil cores já com o Lab pré-calculado (feito 1x pelo Python no load)
let BANCO_CORES_JS = [];

window.prepararBancoCoresJS = function(dadosPy) {
    // IMPORTANTE: sem dict_converter, o Pyodide converte os dicts Python
    // aninhados em Map do JS (não em objeto comum), e item.l / item.name
    // ficam undefined silenciosamente. Object.fromEntries corrige isso.
    BANCO_CORES_JS = dadosPy.toJs
        ? dadosPy.toJs({ dict_converter: Object.fromEntries })
        : dadosPy;
    return true;
};

window.buscarNomeCorJS = function(labAlvoPy) {
    const labAlvo = labAlvoPy.toJs ? labAlvoPy.toJs() : labAlvoPy;
    const [tL, tA, tB] = labAlvo;

    let menorDist = Infinity;
    let nomeAchado = "Custom Color";

    // Loop nativo em V8: muito mais rápido que o mesmo loop em Python/Pyodide
    for (let i = 0; i < BANCO_CORES_JS.length; i++) {
        const item = BANCO_CORES_JS[i];
        const dL = tL - item.l;
        const dA = tA - item.a;
        const dB = tB - item.b;
        const dist = Math.sqrt(dL * dL + dA * dA + dB * dB);
        if (dist < menorDist) {
            menorDist = dist;
            nomeAchado = item.name;
        }
    }
    return nomeAchado;
};

window.ordenarPokemonPorCorJS = function(dadosFiltradosJS, corLabAlvo) {
    // Converte o proxy do Pyodide para um array JS nativo se necessário
    const lista = dadosFiltradosJS.toJs ? dadosFiltradosJS.toJs() : dadosFiltradosJS;
    const [targetL, targetA, targetB] = corLabAlvo;

    // Função interna de distância (calculada de forma nativa e ultraveloz)
    function calcularDistancia(colorArray) {
        const dL = targetL - colorArray[0];
        const dA = targetA - colorArray[1];
        const dB = targetB - colorArray[2];
        return Math.sqrt(dL * dL + dA * dA + dB * dB);
    }

    // Ordena a lista diretamente no motor V8/SpiderMonkey
    lista.sort((a, b) => calcularDistancia(a.color) - calcularDistancia(b.color));

    // Retorna apenas a lista organizada para o Python
    return lista;
};