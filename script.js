// ==========================================
// 0. INTERNACIONALIZAÇÃO (i18n)
// ==========================================
// Fonte única de verdade das traduções. O app.py também lê daqui (via
// window.t()), pra não duplicar texto entre JS e Python.
// Pra adicionar um novo idioma: copie o bloco "en" inteiro, traduza os
// valores e adicione a chave (ex: "es") aqui embaixo.
const TRADUCOES = {
    "pt-br": {
        titulo: "Customizador de Paleta Pokémon",
        subtitulo_html: 'Insira as suas cores do <a href="https://pantonecolors.net/pantone-birth-chart/" target="_blank" rel="noopener noreferrer" class="link-destaque">Pantone Birth Chart</a> para encontrar seus Pokémon ideais',
        ajuda_resumo: "Precisa de ajuda? Veja como pegar as cores",
        ajuda_passo1_html: '1. Abra o <a href="https://pantonecolors.net/pantone-birth-chart/" target="_blank" rel="noopener noreferrer" class="link-destaque">Pantone Birth Chart</a> em uma nova aba.',
        ajuda_passo2: "2. Insira sua data, hora e local de nascimento para gerar o seu gráfico de cores Pantone.",
        ajuda_passo3_html: "3. Copie as tags <b>HEX</b> (os códigos com #, basta clicar nela!) geradas para o seu perfil.",
        ajuda_passo4: "4. Cole as cores aqui no nosso gerador e veja a mágica acontecer!",
        btn_add_cor: "+ Adicionar Cor",
        btn_abrir_filtros: "Filtros de Pokémon",
        modal_titulo: "Filtros Avançados",
        filtro_secao_regras: "Regras do Gerador",
        filtro_secao_biologia: "Biologia e Raridade",
        filtro_secao_habitat: "Habitat",
        filtro_secao_geracao: "Região / Geração",
        filtro_secao_tipos: "Tipos",
        chk_repetidos_label: "Permitir Repetidos",
        chk_repetidos_title: "Permite que o mesmo Pokémon apareça mais de uma vez",
        chk_apenas_shiny: "Apenas Shinies",
        chk_sem_shiny: "Ocultar Shinies",
        chk_estagio_inicial: "Estágio Inicial",
        chk_estagio_intermediario: "Estágio Intermediário",
        chk_estagio_final: "Estágio Final",
        chk_megas: "Mega Evoluções",
        chk_lendarios_miticos: "Lendários e Míticos",
        habitat_floresta: "Floresta",
        habitat_mar: "Mar",
        habitat_caverna: "Caverna",
        habitat_montanha: "Montanha",
        habitat_urbano: "Urbano",
        habitat_campos: "Campos",
        tipo_fogo: "Fogo",
        tipo_agua: "Água",
        tipo_planta: "Planta",
        tipo_eletrico: "Elétrico",
        tipo_psiquico: "Psíquico",
        tipo_sombrio: "Sombrio",
        tipo_fada: "Fada",
        tipo_dragao: "Dragão",
        btn_fechar_filtros: "Aplicar e Voltar",
        btn_exportar_pantone: "Pantone Moodboard",
        btn_exportar_horizontal: "Baixar Imagem Horizontal",
        btn_exportar_stories: "Baixar Imagem para Stories",
        btn_aleatorio: "Paleta Aleatória",
        idioma_alternar: "English",

        // Usadas pelo app.py (imagens exportadas e pop-ups do iOS)
        categoria_paleta: "PALETTE",
        pantone_match_prefixo: "Pantone match: ",
        titulo_imagem_horizontal: "MINHA PALETA POKÉMON",
        tooltip_clique_salvar: "(Clique para salvar)",
        ios_titulo_paleta: "Salvar Paleta",
        ios_titulo_stories: "Salvar Paleta Stories",
        ios_titulo_moodboard: "Salvar Moodboard",
        ios_instrucao: 'Pressione e segure na imagem para "Adicionar às Fotos"',
        ios_instrucao_stories: 'Pressione e segure na imagem para "Adicionar às Fotos" e postar nos Stories!',
    },
    "en": {
        titulo: "Pokémon Palette Customizer",
        subtitulo_html: 'Enter your colors from the <a href="https://pantonecolors.net/pantone-birth-chart/" target="_blank" rel="noopener noreferrer" class="link-destaque">Pantone Birth Chart</a> to find your ideal Pokémon',
        ajuda_resumo: "Need help? See how to get your colors",
        ajuda_passo1_html: '1. Open the <a href="https://pantonecolors.net/pantone-birth-chart/" target="_blank" rel="noopener noreferrer" class="link-destaque">Pantone Birth Chart</a> in a new tab.',
        ajuda_passo2: "2. Enter your birth date, time and place to generate your Pantone color chart.",
        ajuda_passo3_html: "3. Copy the <b>HEX</b> tags (the codes with #, just click on it!) generated for your profile.",
        ajuda_passo4: "4. Paste the colors here in our generator and watch the magic happen!",
        btn_add_cor: "+ Add Color",
        btn_abrir_filtros: "Pokémon Filters",
        modal_titulo: "Advanced Filters",
        filtro_secao_regras: "Generator Rules",
        filtro_secao_biologia: "Biology & Rarity",
        filtro_secao_habitat: "Habitat",
        filtro_secao_geracao: "Region / Generation",
        filtro_secao_tipos: "Types",
        chk_repetidos_label: "Allow Repeats",
        chk_repetidos_title: "Allows the same Pokémon to appear more than once",
        chk_apenas_shiny: "Shinies Only",
        chk_sem_shiny: "Hide Shinies",
        chk_estagio_inicial: "Base Stage",
        chk_estagio_intermediario: "Middle Stage",
        chk_estagio_final: "Final Stage",
        chk_megas: "Mega Evolutions",
        chk_lendarios_miticos: "Legendaries & Mythicals",
        habitat_floresta: "Forest",
        habitat_mar: "Sea",
        habitat_caverna: "Cave",
        habitat_montanha: "Mountain",
        habitat_urbano: "Urban",
        habitat_campos: "Grassland",
        tipo_fogo: "Fire",
        tipo_agua: "Water",
        tipo_planta: "Grass",
        tipo_eletrico: "Electric",
        tipo_psiquico: "Psychic",
        tipo_sombrio: "Dark",
        tipo_fada: "Fairy",
        tipo_dragao: "Dragon",
        btn_fechar_filtros: "Apply and Close",
        btn_exportar_pantone: "Pantone Moodboard",
        btn_exportar_horizontal: "Download Horizontal Image",
        btn_exportar_stories: "Download Stories Image",
        btn_aleatorio: "Random Palette",
        idioma_alternar: "Português",

        // Used by app.py (exported images and iOS pop-ups)
        categoria_paleta: "PALETTE",
        pantone_match_prefixo: "Pantone match: ",
        titulo_imagem_horizontal: "MY POKÉMON PALETTE",
        tooltip_clique_salvar: "(Click to save)",
        ios_titulo_paleta: "Save Palette",
        ios_titulo_stories: "Save Stories Palette",
        ios_titulo_moodboard: "Save Moodboard",
        ios_instrucao: 'Press and hold the image to "Add to Photos"',
        ios_instrucao_stories: 'Press and hold the image to "Add to Photos" and post it to your Stories!',
    }
};

const IDIOMA_PADRAO = "pt-br";

// Detecta o idioma ativo: preferência salva manualmente > idioma do
// navegador > português como padrão.
function idiomaAtual() {
    const salvo = localStorage.getItem("idioma");
    if (salvo && TRADUCOES[salvo]) return salvo;

    const navegador = (navigator.language || "").toLowerCase();
    if (navegador.startsWith("pt")) return "pt-br";
    return "en";
}

// Tradução de uma chave no idioma ativo, com fallback pro português e,
// em último caso, pra própria chave (nunca quebra a tela por falta de chave).
window.t = function(chave) {
    const idioma = idiomaAtual();
    const dicionario = TRADUCOES[idioma] || TRADUCOES[IDIOMA_PADRAO];
    return dicionario[chave] ?? TRADUCOES[IDIOMA_PADRAO][chave] ?? chave;
};

// Aplica as traduções em todos os elementos marcados no HTML:
// - data-i18n="chave"       -> define o textContent
// - data-i18n-html="chave"  -> define o innerHTML (pra textos com <a>/<b> dentro)
// - data-i18n-title="chave" -> define o atributo title (tooltip)
function aplicarTraducoes() {
    document.documentElement.lang = idiomaAtual();
    document.title = window.t("titulo");

    document.querySelectorAll("[data-i18n]").forEach((el) => {
        el.textContent = window.t(el.dataset.i18n);
    });
    document.querySelectorAll("[data-i18n-html]").forEach((el) => {
        el.innerHTML = window.t(el.dataset.i18nHtml);
    });
    document.querySelectorAll("[data-i18n-title]").forEach((el) => {
        el.title = window.t(el.dataset.i18nTitle);
    });

    const btnIdioma = document.getElementById("btn-idioma");
    if (btnIdioma) btnIdioma.textContent = "🌐 " + window.t("idioma_alternar");
}

document.addEventListener("DOMContentLoaded", function() {
    aplicarTraducoes();

    // Botão de troca de idioma: salva a escolha e recarrega a página, pra
    // garantir que o texto gerado pelo Python (imagens, pop-ups) também
    // já nasça no idioma certo na próxima renderização.
    const btnIdioma = document.getElementById("btn-idioma");
    if (btnIdioma) {
        btnIdioma.addEventListener("click", () => {
            const proximo = idiomaAtual() === "pt-br" ? "en" : "pt-br";
            localStorage.setItem("idioma", proximo);
            window.location.reload();
        });
    }

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