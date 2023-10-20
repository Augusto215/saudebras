function filterOptions(searchInputId, selectId) {
  console.log("Função filterOptions chamada");  // Debug
  const searchInput = document.getElementById(searchInputId);
  const select = document.getElementById(selectId);

  console.log("searchInput:", searchInput);  // Debug
  console.log("select:", select);  // Debug

  searchInput.addEventListener("input", function() {
    const query = searchInput.value.toLowerCase();
    console.log("Query:", query);  // Debug

    for (let i = 0; i < select.options.length; i++) {
      const option = select.options[i];
      if (option.text.toLowerCase().includes(query)) {
        option.style.display = "";
      } else {
        option.style.display = "none";
      }
    }
    
    // Abre o select
    const event = new MouseEvent("mousedown");
    select.dispatchEvent(event);
  });
}

document.addEventListener('DOMContentLoaded', function() {

  const estadoSelect = document.getElementById("estado_select");
  const cidadeSelect = document.getElementById("cidade_select");

  document.getElementById("mostrarPrincipal").addEventListener("click", function() {
    let params = {};

  

    
    
    
    const estado = estadoSelect.value;
    const cidade = cidadeSelect.value;
    if (estado) params['estados'] = estado;
    if (cidade) params['cidades'] = cidade;
  
    const origin = window.location.origin;
    const combinedURL = generateURL(`${origin}/clinicas?tipo_clinica=Laboratório`, params);

  
    if (Object.keys(params).length > 1) {
      window.location.href = combinedURL;
    } else {
      console.log("Preencha ao menos um campo para gerar a URL");
    }
  });





  const estadoInitialOption = document.createElement("option");
  estadoInitialOption.value = "";
  estadoInitialOption.text = "Estados";
  estadoSelect.appendChild(estadoInitialOption);

  const cidadeInitialOption = document.createElement("option");
  cidadeInitialOption.value = "";
  cidadeInitialOption.text = "Cidades";
  cidadeSelect.appendChild(cidadeInitialOption);




  function fetchEstados() {
    return fetch('/buscar_estados_por_tipo_clinica/?tipo_clinica=Laboratório')
    .then(response => response.json())
    .then(data => {
      console.log("Dados recebidos em fetchEstados: ", data);
      return data.estados;
    });
}

  function fetchCidades(estado) {
    return fetch(`/buscar_cidades_por_tipo_clinica/?tipo_clinica=Laboratório&estados=${estado}`)
    .then(response => response.json())
    .then(data => {
      console.log("Dados recebidos em fetchCidades: ", data);
      return data.cidades;
    });
}

// Carrega Estados ao carregar a página
fetchEstados().then(estados => {
  estados.forEach(estado => {
    const option = document.createElement("option");
    option.value = estado;
    option.text = estado;
    estadoSelect.appendChild(option);
  });
  estadoSelect.disabled = false;
});

// Evento change para Estados
estadoSelect.addEventListener("change", function() {
  cidadeSelect.innerHTML = "";
  cidadeSelect.appendChild(cidadeInitialOption);
  cidadeSelect.disabled = false;

  const estadoSelecionado = estadoSelect.value;
  fetchCidades(estadoSelecionado).then(cidades => {
    cidades.forEach(cidade => {
      const option = document.createElement("option");
      option.value = cidade;
      option.text = cidade;
      cidadeSelect.appendChild(option);
    });
  });
});
})

function generateURL(base, params) {
  const url = new URL(base);
  Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
  return url;
}

