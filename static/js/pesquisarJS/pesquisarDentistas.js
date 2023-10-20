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
  const especialidadeSelect = document.getElementById("especialidade_select");
  const estadoSelect = document.getElementById("estado_select");
  const cidadeSelect = document.getElementById("cidade_select");

  document.getElementById("mostrarPrincipal").addEventListener("click", function() {
    let params = {};

  

    
    
    
  
    const estado = estadoSelect.value;
    const especialidade = especialidadeSelect.value;
    const cidade = cidadeSelect.value;
  
    if (estado) params['estado'] = estado;
    if (especialidade) params['especialidade'] = especialidade;
    if (cidade) params['cidade'] = cidade;
    

    
    const combinedURL = generateURL('http://127.0.0.1:8000/profissionais?tipo_profissional=Dentista', params);
  
     
if (Object.keys(params).length > 2) {

  window.location.href = combinedURL;
} else {
  console.log("Preencha ao menos um campo para gerar a URL");
}
});











  const especialidadeInitialOption = document.createElement("option");
  especialidadeInitialOption.value = "";
  especialidadeInitialOption.text = "Especialidades";
  especialidadeSelect.appendChild(especialidadeInitialOption);

  const estadoInitialOption = document.createElement("option");
  estadoInitialOption.value = "";
  estadoInitialOption.text = "Estados";
  estadoSelect.appendChild(estadoInitialOption);

  const cidadeInitialOption = document.createElement("option");
  cidadeInitialOption.value = "";
  cidadeInitialOption.text = "Cidades";
  cidadeSelect.appendChild(cidadeInitialOption);



  function fetchEspecialidades() {
    const url = `/buscar_especialidades/?tipo_profissional=Dentista}`;
    console.log("URL completa: ", url);
    
    return fetch(`/buscar_especialidades/?tipo_profissional=Dentista`)
    .then(response => response.json())
    .then(data => {
      console.log("Dados recebidos em fetchEspecialidades: ", data);
      return data.especialidades;
      
      
    });
    
}

  function fetchEstados(especialidade) {
    return fetch(`/buscar_estados/?tipo_profissional=Dentista&especialidade=${especialidade}`)
    .then(response => response.json())
    .then(data => {
      console.log("Dados recebidos em fetchEstados: ", data);
      return data.estados;
    });
}

  function fetchCidades(estado, especialidade) {
    return fetch(`/get_cities/?estado=${estado}&tipo_profissional=Dentista&especialidade=${especialidade}`)
    .then(response => response.json())
    .then(data => {
      console.log("Dados recebidos em fetchCidades: ", data);
      return data.cities;
    });
}

// Carrega Especialidades ao carregar a página
fetchEspecialidades().then(especialidades => {
  especialidades.forEach(especialidade => {
    const option = document.createElement("option");
    option.value = especialidade;
    option.text = especialidade;
    especialidadeSelect.appendChild(option);
  });
  especialidadeSelect.disabled = false;
  // Você pode adicionar o seu filtro aqui, caso necessário
});

// Evento change para Especialidades
especialidadeSelect.addEventListener("change", function() {
  estadoSelect.innerHTML = "";
  estadoSelect.appendChild(estadoInitialOption);
  estadoSelect.disabled = false;

  cidadeSelect.innerHTML = "";
  cidadeSelect.appendChild(cidadeInitialOption);
  cidadeSelect.disabled = true;

  const especialidadeSelecionada = especialidadeSelect.value;
    fetchEstados(especialidadeSelecionada).then(estados => {
      estados.forEach(estado => {
        const option = document.createElement("option");
        option.value = estado;
        option.text = estado;
        estadoSelect.appendChild(option);
      });
      filterOptions('estadoSearch', 'estado_select'); // Chamada única fora do forEach
    });
});
  estadoSelect.addEventListener("change", function() {
    cidadeSelect.innerHTML = "";
    cidadeSelect.appendChild(cidadeInitialOption);
    cidadeSelect.disabled = false;

    const estadoSelecionado = estadoSelect.value;
    const especialidadeSelecionada = especialidadeSelect.value;

    fetchCidades(estadoSelecionado,  especialidadeSelecionada).then(cidades => {
      cidades.forEach(cidade => {
        const option = document.createElement("option");
        option.value = cidade;
        option.text = cidade;
        cidadeSelect.appendChild(option);
        
      });
    });
  });
});



function generateURL(base, params) {
  const url = new URL(base);
  Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
  return url;
}

