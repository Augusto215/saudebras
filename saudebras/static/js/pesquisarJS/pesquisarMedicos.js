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
    const buscarButton = document.getElementById("mostrarPrincipal");
    
    // Função para verificar se todos os campos estão preenchidos
    function verificarCamposObrigatorios() {
      const especialidade = especialidadeSelect.value;
      const estado = estadoSelect.value;
      const cidade = cidadeSelect.value;
      
      if (especialidade && estado && cidade) {
        buscarButton.disabled = false;
        buscarButton.style.opacity = "1";
        buscarButton.style.cursor = "pointer";
      } else {
        buscarButton.disabled = true;
        buscarButton.style.opacity = "0.5";
        buscarButton.style.cursor = "not-allowed";
      }
    }
    
    // Inicialmente desabilitar o botão
    verificarCamposObrigatorios();
  
    document.getElementById("mostrarPrincipal").addEventListener("click", function() {
      let params = {};
  
      const estado = estadoSelect.value;
      const especialidade = especialidadeSelect.value;
      const cidade = cidadeSelect.value;
    
      // Verificar se todos os campos obrigatórios estão preenchidos
      if (!especialidade || !estado || !cidade) {
        alert("Por favor, selecione a especialidade, o estado e a cidade para realizar a pesquisa.");
        return;
      }
    
      if (estado) params['estado'] = estado;
      if (especialidade) params['especialidade'] = especialidade;
      if (cidade) params['cidade'] = cidade;
      

      const origin = window.location.origin;
      const combinedURL = generateURL(`${origin}/profissionais?tipo_profissional=Médico`, params);

      window.location.href = combinedURL;
    });

    function fetchEspecialidades() {
      const url = `/buscar_especialidades/?tipo_profissional=Médico`;
      console.log("URL completa: ", url);
      
      return fetch(`/buscar_especialidades/?tipo_profissional=Médico`)
      .then(response => response.json())
      .then(data => {
        console.log("Dados recebidos em fetchEspecialidades: ", data);
        return data.especialidades;
      });
    }
  
    function fetchEstados(especialidade) {
      return fetch(`/buscar_estados/?tipo_profissional=Médico&especialidade=${especialidade}`)
      .then(response => response.json())
      .then(data => {
        console.log("Dados recebidos em fetchEstados: ", data);
        return data.estados;
      });
    }
  
    function fetchCidades(estado, especialidade) {
      return fetch(`/get_cities/?estado=${estado}&tipo_profissional=Médico&especialidade=${especialidade}`)
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
        // Verificar campos após carregar especialidades
        verificarCamposObrigatorios();
      });
  
    // Evento change para Especialidades
    especialidadeSelect.addEventListener("change", function() {
      // Limpar estados
      estadoSelect.innerHTML = "";
      const estadoInitialOption = document.createElement("option");
      estadoInitialOption.value = "";
      estadoInitialOption.text = "Selecione um estado";
      estadoSelect.appendChild(estadoInitialOption);
      estadoSelect.disabled = false;
  
      // Limpar cidades
      cidadeSelect.innerHTML = "";
      const cidadeInitialOption = document.createElement("option");
      cidadeInitialOption.value = "";
      cidadeInitialOption.text = "Selecione uma cidade";
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
          // Verificar campos após carregar estados
          verificarCamposObrigatorios();
        });
    });
    
    estadoSelect.addEventListener("change", function() {
      // Limpar cidades
      cidadeSelect.innerHTML = "";
      const cidadeInitialOption = document.createElement("option");
      cidadeInitialOption.value = "";
      cidadeInitialOption.text = "Selecione uma cidade";
      cidadeSelect.appendChild(cidadeInitialOption);
      cidadeSelect.disabled = false;
  
      const estadoSelecionado = estadoSelect.value;
      const especialidadeSelecionada = especialidadeSelect.value;
  
      fetchCidades(estadoSelecionado, especialidadeSelecionada).then(cidades => {
        cidades.forEach(cidade => {
          const option = document.createElement("option");
          option.value = cidade;
          option.text = cidade;
          cidadeSelect.appendChild(option);
        });
        // Verificar campos após carregar cidades
        verificarCamposObrigatorios();
      });
    });
    
    // Adicionar event listeners para verificar campos em mudanças
    especialidadeSelect.addEventListener("change", verificarCamposObrigatorios);
    estadoSelect.addEventListener("change", verificarCamposObrigatorios);
    cidadeSelect.addEventListener("change", verificarCamposObrigatorios);
  });
  
  function generateURL(base, params) {
    const url = new URL(base);
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
    return url;
  }