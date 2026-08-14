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
        btn_buscar_pokemon: "Buscar Pokémon",
        busca_pokemon_placeholder: "Nome do Pokémon...",
        busca_pokemon_nenhum_resultado: "Nenhum Pokémon encontrado",
        busca_pokemon_voltar: "Voltar",
        busca_pokemon_fechar: "Fechar",
        busca_pokemon_adicionar_a: "Adicionar a",
        busca_pokemon_sobrescrever: "Substituir esta cor",
        busca_pokemon_adicionar_nova: "Adicionar como nova cor",
        busca_pokemon_copiado: "Copiado!",
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

        // Tooltip ao passar o mouse sobre um Pokémon na tela, e textos do
        // pop-up do iOS ("segure pra salvar") — isso é interface (DOM) que
        // a PESSOA lê enquanto usa o site, não pixels da imagem exportada,
        // então continuam respeitando o idioma escolhido.
        tooltip_clique_salvar: "(Clique para salvar)",
        ios_titulo_paleta: "Salvar Paleta",
        ios_titulo_stories: "Salvar Paleta Stories",
        ios_titulo_moodboard: "Salvar Moodboard",
        ios_instrucao: 'Pressione e segure na imagem para "Adicionar às Fotos"',
        ios_instrucao_stories: 'Pressione e segure na imagem para "Adicionar às Fotos" e postar nos Stories!',

        // NOTA: os textos DESENHADOS DENTRO da imagem PNG (título, "PALETTE",
        // "Pantone match:", link do site etc.) NÃO ficam aqui — são fixos em
        // inglês, direto no app.py
        // (TEXTO_TITULO_PALETA, TEXTO_IOS_TITULO_PALETA etc.), de propósito,
        // pra imagem compartilhada ficar igual pra todo mundo.
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
        btn_buscar_pokemon: "Search Pokémon",
        busca_pokemon_placeholder: "Pokémon name...",
        busca_pokemon_nenhum_resultado: "No Pokémon found",
        busca_pokemon_voltar: "Back",
        busca_pokemon_fechar: "Close",
        busca_pokemon_adicionar_a: "Add to",
        busca_pokemon_sobrescrever: "Replace this color",
        busca_pokemon_adicionar_nova: "Add as new color",
        busca_pokemon_copiado: "Copied!",
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
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
        el.placeholder = window.t(el.dataset.i18nPlaceholder);
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
    const btnXFiltros = document.getElementById("btn-x-filtros");
    const overlay = document.getElementById("modal-overlay");

    // Verifica se os botões do modal existem antes de adicionar o evento
    if (btnAbrir && btnFechar && overlay) {
        btnAbrir.addEventListener("click", function() {
            overlay.classList.add("mostrar");
        });

        btnFechar.addEventListener("click", function() {
            overlay.classList.remove("mostrar");
        });

        // X no canto: mesma ação de clicar fora do modal (só fecha, sem
        // reaplicar os filtros -- quem quer aplicar usa "Aplicar e Voltar")
        if (btnXFiltros) {
            btnXFiltros.addEventListener("click", function() {
                overlay.classList.remove("mostrar");
            });
        }

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
    
    // Cria uma nova linha de cor e a insere em #lista-cores. Se `hexInicial`
    // não for passado, sorteia uma cor aleatória (comportamento original do
    // botão "+ Adicionar Cor"). Reaproveitada pela busca de Pokémon pra
    // adicionar uma cor já preenchida, sem duplicar a lógica de criação.
    function criarLinhaDeCor(hexInicial) {
        const novaLinha = document.createElement('div');
        novaLinha.className = 'color-row';

        const hex = hexInicial || ('#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0').toUpperCase());

        novaLinha.innerHTML = `
            <input type="color" class="cor-input" value="${hex}">
            <input type="text" class="hex-input" value="${hex}" maxlength="8">
            <button class="btn-excluir">X</button>
        `;

        listaCores.appendChild(novaLinha);
        sincronizarInputs(novaLinha);
        return novaLinha;
    }

    if (btnAddCor && listaCores) {
        btnAddCor.addEventListener('click', () => criarLinhaDeCor(null));
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

    // ==========================================
    // 4. MODAL DE BUSCA DE POKÉMON
    // ==========================================
    const btnAbrirBusca = document.getElementById('btn-abrir-busca-pokemon');
    const overlayBusca = document.getElementById('modal-busca-pokemon');
    const viewLista = document.getElementById('busca-pokemon-view-lista');
    const viewResultado = document.getElementById('busca-pokemon-view-resultado');
    const inputBusca = document.getElementById('busca-pokemon-input');
    const resultadosEl = document.getElementById('busca-pokemon-resultados');
    const btnVoltarBusca = document.getElementById('busca-pokemon-voltar');
    const btnFecharBusca = document.getElementById('busca-pokemon-fechar');
    const swatchEl = document.getElementById('busca-pokemon-swatch');
    const nomeCorEl = document.getElementById('busca-pokemon-nome-cor');
    const hexEl = document.getElementById('busca-pokemon-hex');
    const spriteEl = document.getElementById('busca-pokemon-sprite');
    const nomePkmnEl = document.getElementById('busca-pokemon-nome-pkmn');
    const slotsEl = document.getElementById('busca-pokemon-slots');

    if (btnAbrirBusca && overlayBusca && listaCores) {
        let pokemonSelecionado = null;

        function caminhoSprite(p) {
            const isShiny = p.name.includes('(Shiny)');
            return `./sprites/${p.id_base}${isShiny ? '_shiny' : ''}.png`;
        }

        function mostrarViewLista() {
            viewLista.style.display = '';
            viewResultado.style.display = 'none';
        }

        function mostrarViewResultado() {
            viewLista.style.display = 'none';
            viewResultado.style.display = '';
        }

        function abrirBusca() {
            overlayBusca.classList.add('mostrar');
            mostrarViewLista();
            inputBusca.value = '';
            renderizarResultados('');
            setTimeout(() => inputBusca.focus(), 50);
        }

        function fecharBusca() {
            overlayBusca.classList.remove('mostrar');
        }

        // Mostra até 8 resultados por vez -- o suficiente pra achar o que
        // se quer digitando poucas letras, sem virar uma lista infinita
        function renderizarResultados(termo) {
            resultadosEl.innerHTML = '';
            const termoNormalizado = termo.trim().toLowerCase();
            if (!termoNormalizado) return;

            const encontrados = (BUSCA_POKEMON_JS || [])
                .filter(p => p.name.toLowerCase().includes(termoNormalizado))
                .slice(0, 8);

            if (encontrados.length === 0) {
                const vazio = document.createElement('div');
                vazio.className = 'busca-pokemon-vazio';
                vazio.textContent = window.t('busca_pokemon_nenhum_resultado');
                resultadosEl.appendChild(vazio);
                return;
            }

            encontrados.forEach(p => {
                const item = document.createElement('div');
                item.className = 'busca-pokemon-item';

                const swatch = document.createElement('div');
                swatch.className = 'busca-pokemon-item-swatch';
                swatch.style.backgroundColor = p.hex;

                const sprite = document.createElement('img');
                sprite.className = 'busca-pokemon-item-sprite';
                sprite.src = caminhoSprite(p);
                sprite.alt = '';
                sprite.loading = 'lazy';

                const nome = document.createElement('span');
                nome.textContent = p.name;

                item.append(swatch, sprite, nome);
                item.addEventListener('click', () => selecionarPokemon(p));
                resultadosEl.appendChild(item);
            });
        }

        function selecionarPokemon(p) {
            pokemonSelecionado = p;

            swatchEl.style.backgroundColor = p.hex;
            hexEl.textContent = p.hex;

            spriteEl.src = caminhoSprite(p);
            nomePkmnEl.textContent = p.name;

            // Mesma busca de nome de cor usada no resto do site (recebe o
            // Lab direto, sem precisar reconverter a partir do hex)
            nomeCorEl.textContent = window.buscarNomeCorJS ? window.buscarNomeCorJS(p.lab) : '';

            renderizarSlots();
            mostrarViewResultado();
        }

        function renderizarSlots() {
            slotsEl.innerHTML = '';

            document.querySelectorAll('#lista-cores .color-row').forEach(linha => {
                const corInput = linha.querySelector('.cor-input');
                const slot = document.createElement('div');
                slot.className = 'busca-pokemon-slot';
                slot.style.backgroundColor = corInput.value;
                slot.title = window.t('busca_pokemon_sobrescrever');
                slot.addEventListener('click', () => aplicarCor(linha));
                slotsEl.appendChild(slot);
            });

            const slotAdicionar = document.createElement('div');
            slotAdicionar.className = 'busca-pokemon-slot busca-pokemon-slot-add';
            slotAdicionar.textContent = '+';
            slotAdicionar.title = window.t('busca_pokemon_adicionar_nova');
            slotAdicionar.addEventListener('click', () => aplicarCor(null));
            slotsEl.appendChild(slotAdicionar);
        }

        // linhaExistente = null -> adiciona uma cor nova; senão, sobrescreve
        // a linha clicada
        function aplicarCor(linhaExistente) {
            if (!pokemonSelecionado) return;
            const hex = pokemonSelecionado.hex;

            if (linhaExistente) {
                linhaExistente.querySelector('.cor-input').value = hex;
                const hexInput = linhaExistente.querySelector('.hex-input');
                hexInput.value = hex;
                hexInput.dataset.ultimoValido = hex;
            } else {
                criarLinhaDeCor(hex);
            }

            listaCores.dispatchEvent(new Event('input', { bubbles: true }));
            fecharBusca();
        }

        if (hexEl) {
            hexEl.addEventListener('click', () => {
                if (!pokemonSelecionado || !navigator.clipboard) return;
                navigator.clipboard.writeText(pokemonSelecionado.hex).then(() => {
                    const textoOriginal = hexEl.textContent;
                    hexEl.textContent = window.t('busca_pokemon_copiado');
                    setTimeout(() => { hexEl.textContent = textoOriginal; }, 1200);
                });
            });
        }

        btnAbrirBusca.addEventListener('click', abrirBusca);
        btnFecharBusca.addEventListener('click', fecharBusca);
        btnVoltarBusca.addEventListener('click', mostrarViewLista);
        overlayBusca.addEventListener('click', (e) => {
            if (e.target.id === 'modal-busca-pokemon') fecharBusca();
        });
        inputBusca.addEventListener('input', (e) => renderizarResultados(e.target.value));
        inputBusca.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const primeiro = resultadosEl.querySelector('.busca-pokemon-item');
                if (primeiro) primeiro.click();
            }
        });
    }
});

// ==========================================
// 5. DADOS MOVIDOS DO PYTHON PRO JS (performance)
// ==========================================
// Duas listas grandes que o Python prepara uma vez (já com Lab
// pré-calculado) e manda pro JS, pra busca/comparação rodar em loop nativo
// V8 em vez de cruzar a ponte Python<->JS a cada tecla digitada.

// Banco de ~32 mil cores (nomeação de cor)
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

// Lista de ~2678 Pokémon (nome, id, hex, Lab), pra busca por Pokémon
let BUSCA_POKEMON_JS = [];

window.prepararBuscaPokemonJS = function(dadosPy) {
    BUSCA_POKEMON_JS = dadosPy.toJs
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