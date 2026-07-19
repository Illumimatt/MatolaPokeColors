document.addEventListener("DOMContentLoaded", function() {
    const btnAbrir = document.getElementById("btn-abrir-filtros");
    const btnFechar = document.getElementById("btn-fechar-filtros");
    const overlay = document.getElementById("modal-overlay");

    // Abre o modal
    btnAbrir.addEventListener("click", function() {
        overlay.classList.add("mostrar");
    });

    // Fecha no botão Voltar
    btnFechar.addEventListener("click", function() {
        overlay.classList.remove("mostrar");
    });

    // Fecha se clicar fora da caixa do modal
    overlay.addEventListener("click", function(event) {
        if (event.target.id === 'modal-overlay') {
            overlay.classList.remove("mostrar");
        }
    });
});