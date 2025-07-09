document.addEventListener('DOMContentLoaded', function () {
  const estadoSelect = document.getElementById("estado_select");
  const cidadeSelect = document.getElementById("cidade_select");
  const buscarButton = document.getElementById("mostrarPrincipal");

  // Função para verificar se deve habilitar o botão
  function verificarCampos() {
    const estado = estadoSelect.value;
    const cidade = cidadeSelect.value;

    if (estado && cidade) {
      buscarButton.disabled = false;
      buscarButton.style.opacity = "1";
      buscarButton.style.cursor = "pointer";
    } else {
      buscarButton.disabled = true;
      buscarButton.style.opacity = "0.5";
      buscarButton.style.cursor = "not-allowed";
    }
  }

  buscarButton.addEventListener("click", function () {
    const estado = estadoSelect.value;
    const cidade = cidadeSelect.value;
    const params = {};

    if (estado) params["estados"] = estado;
    if (cidade) params["cidades"] = cidade;

    if (!estado || !cidade) {
      alert("Por favor, selecione um estado e uma cidade.");
      return;
    }

    const origin = window.location.origin;
    const combinedURL = generateURL(`${origin}/clinicas?tipo_clinica=Laboratório`, params);

    window.location.href = combinedURL;
  });

  function generateURL(base, params) {
    const url = new URL(base);
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
    return url;
  }

  function fetchEstados() {
    return fetch('/buscar_estados_por_tipo_clinica/?tipo_clinica=Laboratório')
      .then(response => response.json())
      .then(data => {
        console.log("Estados:", data);
        return data.estados;
      });
  }

  function fetchCidades(estado) {
    return fetch(`/buscar_cidades_por_tipo_clinica/?tipo_clinica=Laboratório&estados=${estado}`)
      .then(response => response.json())
      .then(data => {
        console.log("Cidades:", data);
        return data.cidades;
      });
  }

  // Carregar estados ao iniciar
  fetchEstados().then(estados => {
    estadoSelect.innerHTML = `<option value="">Selecione um estado</option>`;
    estados.forEach(estado => {
      const option = document.createElement("option");
      option.value = estado;
      option.text = estado;
      estadoSelect.appendChild(option);
    });
    estadoSelect.disabled = false;
    filterOptions('estadoSearch', 'estado_select');
  });

  // Quando mudar estado, carregar cidades
  estadoSelect.addEventListener("change", function () {
    cidadeSelect.innerHTML = `<option value="">Selecione uma cidade</option>`;
    const estadoSelecionado = estadoSelect.value;

    if (!estadoSelecionado) {
      cidadeSelect.disabled = true;
      return;
    }

    fetchCidades(estadoSelecionado).then(cidades => {
      cidades.forEach(cidade => {
        const option = document.createElement("option");
        option.value = cidade;
        option.text = cidade;
        cidadeSelect.appendChild(option);
      });
      cidadeSelect.disabled = false;
      filterOptions('cidadeSearch', 'cidade_select');
      verificarCampos();
    });
  });

  // Monitorar seleção para habilitar botão
  estadoSelect.addEventListener("change", verificarCampos);
  cidadeSelect.addEventListener("change", verificarCampos);
});

// Filtro de pesquisa em selects
function filterOptions(searchInputId, selectId) {
  const searchInput = document.getElementById(searchInputId);
  const select = document.getElementById(selectId);

  if (!searchInput || !select) {
    console.warn(`Elementos não encontrados: ${searchInputId}, ${selectId}`);
    return;
  }

  searchInput.addEventListener("input", function () {
    const query = searchInput.value.toLowerCase();
    for (let i = 0; i < select.options.length; i++) {
      const option = select.options[i];
      option.style.display = option.text.toLowerCase().includes(query) ? "" : "none";
    }

    // Abre o select (simula clique)
    const event = new MouseEvent("mousedown");
    select.dispatchEvent(event);
  });
}
