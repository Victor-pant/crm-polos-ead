/**
 * JavaScript do CRM (lado do cliente).
 * Todo comportamento aqui é progressivo: se o JS falhar ao carregar,
 * os formulários continuam funcionando normalmente via submissão HTTP comum.
 */
document.addEventListener("DOMContentLoaded", function () {
  // --- Contador de caracteres da caixa de mensagem ---
  const mensagem = document.getElementById("mensagem");
  const contador = document.getElementById("contadorMensagem");
  if (mensagem && contador) {
    const atualizarContador = () => {
      contador.textContent = `${mensagem.value.length}/1000 caracteres`;
    };
    mensagem.addEventListener("input", atualizarContador);
    atualizarContador();
  }

  // --- Confirmação antes de marcar um lead como "Perdido" ---
  const selectStatus = document.querySelector('select[data-confirmar-perdido="true"]');
  if (selectStatus) {
    let valorAnterior = selectStatus.value;
    selectStatus.addEventListener("change", function (evento) {
      if (evento.target.value === "Perdido") {
        const confirmado = window.confirm(
          "Tem certeza que deseja marcar este lead como Perdido?"
        );
        if (!confirmado) {
          evento.target.value = valorAnterior;
          return;
        }
      }
      valorAnterior = evento.target.value;
    });
  }

  // --- Filtros da lista de leads: aplica automaticamente ao trocar select ---
  const formFiltros = document.querySelector('form[aria-label="Filtros de leads"]');
  if (formFiltros) {
    formFiltros.querySelectorAll("select").forEach((select) => {
      select.addEventListener("change", () => formFiltros.submit());
    });
  }
});
