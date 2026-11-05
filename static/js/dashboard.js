/**
 * Busca os dados do dashboard via fetch (API interna /dashboard/dados)
 * e monta os gráficos com Chart.js. Mantém acessibilidade usando os
 * atributos role="img" e aria-label já definidos no HTML dos <canvas>.
 */
document.addEventListener("DOMContentLoaded", async function () {
  try {
    const resposta = await fetch("/dashboard/dados");
    if (!resposta.ok) throw new Error("Falha ao carregar dados do dashboard");
    const dados = await resposta.json();

    new Chart(document.getElementById("graficoStatus"), {
      type: "bar",
      data: {
        labels: dados.status.labels,
        datasets: [{ label: "Leads", data: dados.status.valores, backgroundColor: "#0b5ed7" }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
      },
    });

    new Chart(document.getElementById("graficoOrigem"), {
      type: "pie",
      data: {
        labels: dados.origem.labels,
        datasets: [{ data: dados.origem.valores }],
      },
      options: { responsive: true },
    });

    new Chart(document.getElementById("graficoPolo"), {
      type: "pie",
      data: {
        labels: dados.polo.labels,
        datasets: [{ data: dados.polo.valores }],
      },
      options: { responsive: true },
    });
  } catch (erro) {
    console.error(erro);
    document.querySelectorAll("canvas").forEach((canvas) => {
      const aviso = document.createElement("p");
      aviso.className = "text-danger";
      aviso.textContent = "Não foi possível carregar este gráfico.";
      canvas.replaceWith(aviso);
    });
  }
});
