document.addEventListener('DOMContentLoaded', function() {
  const tipoClinicaSelect = document.getElementById('clinica_select');
  const especialidadeSelect = document.getElementById("especialidade_select");
  const estadoSelect = document.getElementById("estado_select");
  const cidadeSelect = document.getElementById("cidade_select");
  const tipoProfissionalSelect = document.getElementById("tipo_profissional_select")
  const conveniosSelect = document.getElementById('convenios_select')
  
  
  document.getElementById("mostrarPrincipal").addEventListener("click", function() {
    let params = {};
      
    const tipoClinica = tipoClinicaSelect.value;
    const tipoProfissional = tipoProfissionalSelect.value;
    const estado = estadoSelect.value;
    const especialidade = especialidadeSelect.value;
    const cidade = cidadeSelect.value;
    const convenios = conveniosSelect.value;
     
    if (tipoClinica) params['tipo_clinica'] = tipoClinica;
    if (tipoProfissional) params['tipo_profissional'] = tipoProfissional;
    if (estado) params['estados'] = estado;
    if (especialidade) params['especialidade'] = especialidade;
    if (cidade) params['cidades'] = cidade;
    if (convenios) params['convenios'] = convenios;
  
    const combinedURL = generateURL('http://127.0.0.1:8000/clinicas', params);
  
    if (Object.keys(params).length > 0) {
      window.location.href = combinedURL;
    } else {
      console.log("Preencha ao menos um campo para gerar a URL");
    }
  


  
});
  // Initial Options

  const tipoClinicaInitialOption = document.createElement("option");
  tipoClinicaInitialOption.value = "";
  tipoClinicaInitialOption.text = "Tipos de Clínicas";
  tipoClinicaSelect.appendChild(tipoClinicaInitialOption);

  const tipoProfissionalInitialOption = document.createElement("option");
  tipoProfissionalInitialOption.value = "";
  tipoProfissionalInitialOption.text = "Tipos de Profissionais";
  tipoProfissionalSelect.appendChild(tipoProfissionalInitialOption);

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

  const conveniosInitialOption = document.createElement("option");
  conveniosInitialOption.value = "";
  conveniosInitialOption.text = "Convênios";
  conveniosSelect.appendChild(conveniosInitialOption);

  // Enable initial select
  tipoClinicaSelect.disabled = false;
  
  
  
  function fetchTiposClinicas() {
      return fetch("/buscar_tipos_clinicas/")
      .then(response => response.json())
      .then(data => {
          console.log("Dados recebidos em fetchTiposClinicas: ", data);
        return data; // Ou data.tipos_clinicas, dependendo do seu formato JSON
      });
    }

    
    function fetchTiposProfissionais(tipoClinica) {
      return fetch(`/buscar_profissionais_por_tipo_clinica/?tipo_clinica=${tipoClinica}`)
      .then(response => response.json())
      .then(data => {
          console.log("Dados recebidos em fetchTiposProfissionais: ", data);
          return data.profissionais;
      });
  } 

 
    
  

  function fetchEspecialidades(tipoProfissional, tipoClinica) {
    return fetch(`/buscar_especialidades_por_tipo_clinica/?tipo_profissional=${tipoProfissional}&tipo_clinica=${tipoClinica}`)
      .then(response => response.json())
      .then(data => {
        return data;
      });
  }
  

  function fetchEstados(tipoClinica, tipoProfissional, especialidade) {
    const url = `/buscar_estados_por_tipo_clinica/?tipo_profissional=${tipoProfissional}&especialidade=${especialidade}&tipo_clinica=${tipoClinica}`;
    console.log(`Buscando URL: ${url}`);
  
    return fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log("Dados recebidos em fetchEstados: ", data);
        if (data && data.estados) {
          return data.estados;
        } else {
          console.log("Campo 'estados' não encontrado na resposta.");
          return [];
        }
      })
      .catch(e => {
        console.log("Ocorreu um erro durante o fetch: ", e);
      });
  }
  



  function fetchCidades(estado, tipoClinica, tipoProfissional, especialidade) {
    return fetch(`/buscar_cidades_por_tipo_clinica/?estados=${estado}&tipo_clinica=${tipoClinica}&tipo_profissional=${tipoProfissional}&especialidade=${especialidade}`)
    .then(response => response.json())
    .then(data => {
      console.log("Dados recebidos em fetchCidades: ", data);
      return data.cidades;
    });
}


function fetchConvenios(estado, tipoClinica, tipoProfissional, especialidade, cidade) {
  return fetch(`/buscar_convenios_por_tipo_clinica/?estados=${estado}&tipo_clinica=${tipoClinica}&tipo_profissional=${tipoProfissional}&especialidade=${especialidade}&cidade=${cidade}`)
  .then(response => response.json())
  .then(data => {
    console.log("Dados recebidos em fetchConvenios: ", data);
    return data.convenios;
  });
}
  // Load Tipos de Profissionais
  function atualizaSelect(selectElement, opcoes) {
    // Limpa as opções existentes
    selectElement.innerHTML = "";
  
    // Adiciona as novas opções
    opcoes.forEach(opcao => {
      const optionElement = document.createElement("option");
      optionElement.value = opcao;
      optionElement.text = opcao;
      selectElement.appendChild(optionElement);
    });
  }
  

  fetchTiposClinicas().then(response => {
    console.log('Response:', response);
      console.log("Processed data:", response);
      const tipos = response.tipos_clinicas;
      console.log("Tipo dos dados recebidos:", typeof response.profissionais);
      console.log("Conteúdo:", response.profissionais);

      console.log('tipo de dados:', typeof tipos)  // Assumindo que os dados vêm em um campo chamado 'tipos_clinicas'
      tipos.forEach(tipo => {
        const option = document.createElement("option");
        option.value = tipo;
        option.text = tipo;
        tipoClinicaSelect.appendChild(option);
      });
      tipoClinicaSelect.disabled = false;
    });
    
    // ..

    tipoClinicaSelect.addEventListener("change", function() {
      tipoProfissionalSelect.innerHTML = "";
      tipoProfissionalSelect.appendChild(tipoProfissionalInitialOption);
      tipoProfissionalSelect.disabled = false;

      
      especialidadeSelect.innerHTML = "";
      especialidadeSelect.appendChild(especialidadeInitialOption);
      especialidadeSelect.disabled = true;
    
      // Limpa os outros dropdowns, se necessário
      estadoSelect.innerHTML = "";
      estadoSelect.appendChild(estadoInitialOption);
      estadoSelect.disabled = true;
    
      cidadeSelect.innerHTML = "";
      cidadeSelect.appendChild(cidadeInitialOption);
      cidadeSelect.disabled = true; 

      conveniosSelect.innerHTML = "";
      conveniosSelect.appendChild(conveniosInitialOption);
      conveniosSelect.disabled = true; 

      const tipoClinicaSelecionado = tipoClinicaSelect.value;
      tipoProfissionalSelect.innerHTML = "";
      tipoProfissionalSelect.appendChild(tipoProfissionalInitialOption);
      fetchTiposProfissionais(tipoClinicaSelecionado).then(response => {
        if (response) {
          const tiposProfissionais = response;
          console.log("TiposProfissionais:", tiposProfissionais);
              
          tiposProfissionais.forEach(profissional =>  {
            const option = document.createElement("option");
            option.value = profissional;
            option.text = profissional;
            tipoProfissionalSelect.appendChild(option);
          });
              
          tipoProfissionalSelect.disabled = false;
          
          
        }
      });
    
      tipoProfissionalSelect.addEventListener("change", function() {

        
        const tipoProfissionalSelecionado = tipoProfissionalSelect.value;
        const tipoClinicaSelecionado = tipoClinicaSelect.value;
      
        fetchEspecialidades(tipoProfissionalSelecionado, tipoClinicaSelecionado).then(response => {
          if (response && response.especialidades) {
            especialidadeSelect.innerHTML = "";
            especialidadeSelect.appendChild(especialidadeInitialOption);
      
            const especialidades = response.especialidades;
            especialidades.forEach(especialidade => {
              const option = document.createElement("option");
              option.value = especialidade;
              option.text = especialidade;
              especialidadeSelect.appendChild(option);
            });
      
            especialidadeSelect.disabled = false;
          }
        });
      });

      especialidadeSelect.addEventListener("change", function() {
        // Limpa e desabilita outros campos que dependem deste, se necessário
        estadoSelect.innerHTML = "";
      estadoSelect.appendChild(estadoInitialOption);
      estadoSelect.disabled = false;
      
        const especialidadeSelecionada = especialidadeSelect.value;
        const tipoProfissionalSelecionado = tipoProfissionalSelect.value;
        const tipoClinicaSelecionado = tipoClinicaSelect.value;
      
  fetchEstados(tipoClinicaSelecionado, tipoProfissionalSelecionado, especialidadeSelecionada)
.then(response => {
  
  console.log("Response completa do fetchEstados:", JSON.stringify(response));
  
  if (Array.isArray(response)) {
    estadoSelect.innerHTML = "";
    estadoSelect.appendChild(estadoInitialOption)
    // Seu código para popular o dropdown aqui
    response.forEach(estado => {
      const option = document.createElement("option");
      option.value = estado;
      option.text = estado;
      estadoSelect.appendChild(option);
    });
    
    
    estadoSelect.disabled = false;

  } else {
    console.log('fetchEstados não retornou estados válidos:', response);
  }
});
       
      });
      
      
      // Quando o estado mudar, este evento é disparado.
// Quando o estado mudar, este evento é disparado.
estadoSelect.addEventListener("change", function() {
  cidadeSelect.innerHTML = "";
  cidadeSelect.appendChild(cidadeInitialOption);
  cidadeSelect.disabled = false;

  const estadoSelecionado = estadoSelect.value;
  const tipoProfissionalSelecionado = tipoProfissionalSelect.value;
  const tipoClinicaSelecionado = tipoClinicaSelect.value;
  const especialidadeSelecionada = especialidadeSelect.value;

  fetchCidades(estadoSelecionado, tipoClinicaSelecionado, tipoProfissionalSelecionado, especialidadeSelecionada)
  .then(response => {
    console.log("Response completa do fetchCIDDES:", JSON.stringify(response));
  
    if (Array.isArray(response)) {
      cidadeSelect.innerHTML = "";
        cidadeSelect.appendChild(cidadeInitialOption); // Verifica se response e response.cidades existem e se response.cidades é um array
      response.forEach(cidade => { 
        
        const option = document.createElement("option");
        option.value = cidade;
        option.text = cidade;
        cidadeSelect.appendChild(option);
      });
      
     
      
      cidadeSelect.disabled = false;  // Habilita o dropdown de cidades
    } else {
      console.log('fetchCIDADES não retornou cidades válidas:', response);
    }
  })
  .catch(error => {
    console.log('Erro ao buscar cidades:', error);
  });
});


cidadeSelect.addEventListener("change", function() {
  conveniosSelect.innerHTML = "";
  conveniosSelect.appendChild(conveniosInitialOption);
  conveniosSelect.disabled = false;

  const estadoSelecionado = estadoSelect.value;
  const tipoProfissionalSelecionado = tipoProfissionalSelect.value;
  const tipoClinicaSelecionado = tipoClinicaSelect.value;
  const especialidadeSelecionada = especialidadeSelect.value;
  const cidadeSelecionada = cidadeSelect.value;

  fetchConvenios(estadoSelecionado, tipoClinicaSelecionado, tipoProfissionalSelecionado, especialidadeSelecionada, cidadeSelecionada)
  .then(response => {
    console.log("Response completa do fetchCIDDES:", JSON.stringify(response));
  
    if (Array.isArray(response)) {
      conveniosSelect.innerHTML = "";
      conveniosSelect.appendChild(conveniosInitialOption); // Verifica se response e response.cidades existem e se response.cidades é um array
      response.forEach(convenio => { 
        
        const option = document.createElement("option");
        option.value = convenio;
        option.text = convenio;
        conveniosSelect.appendChild(option);
      });
      
     
      
      conveniosSelect.disabled = false;  // Habilita o dropdown de cidades
    } else {
      console.log('fetchConvenios não retornou cidades válidas:', response);
    }
  })
  .catch(error => {
    console.log('Erro ao buscar convenios:', error);
  });
});

// Função para popular os convênios usando checkboxes
function populateConveniosCheckboxes(convenios) {
  const container = document.getElementById("convenios_checkboxes");
  container.innerHTML = ""; // Limpa os checkboxes existentes

  convenios.forEach((convenio, index) => {
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.id = `convenio${index}`;
      checkbox.value = convenio;

      const label = document.createElement("label");
      label.htmlFor = `convenio${index}`;
      label.appendChild(document.createTextNode(convenio));

      container.appendChild(checkbox);
      container.appendChild(label);
      container.appendChild(document.createElement("br")); // para a próxima linha
  });
}

// Ao receber dados de convênios
fetchConvenios(estadoSelecionado, tipoClinicaSelecionado, tipoProfissionalSelecionado, especialidadeSelecionada, cidadeSelecionada).then(response => {
  console.log("Response completa do fetchConvenios:", JSON.stringify(response));
  if (Array.isArray(response)) {
      populateConveniosCheckboxes(response);
  } else {
      console.log('fetchConvenios não retornou convênios válidos:', response);
  }
})
.catch(error => {
  console.log('Erro ao buscar convênios:', error);
});

// Ouvinte de eventos para os checkboxes de convênios
document.getElementById("convenios_checkboxes").addEventListener("click", function(event) {
  if (event.target.tagName === "INPUT") {
      const convenioSelecionado = event.target.value;
      console.log("Checkbox de convênio clicado:", convenioSelecionado);
      // Aqui você pode adicionar a lógica necessária quando um checkbox é clicado
  }
});




    })
  })  

  let lat_inicial = -23.550520;  // Coloque valores padrão aqui
  let lng_inicial = -46.633308;  // Coloque valores padrão aqui
  
  const url = window.location.href;
  const urlObj = new URL(url);
  const params = new URLSearchParams(urlObj.search);
  const estado = params.get('estados');
  const cidade = params.get('cidades');
  
  if (estado && cidade) {
    fetch(`https://nominatim.openstreetmap.org/search?city=${cidade}&state=${estado}&format=json`)
      .then(response => response.json())
      .then(data => {
        if (data.length > 0) {
          lat_inicial = data[0].lat;
          lng_inicial = data[0].lon;
          
          // Agora inicialize o mapa aqui
          var mymap = L.map('mapid').setView([lat_inicial, lng_inicial], 13);
          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
          }).addTo(mymap);
  
          // Código para adicionar marcadores, etc.
  
        } else {
          console.log('Nenhum resultado encontrado');
        }
      })
      .catch((error) => console.error('Erro ao buscar dados:', error));
  } else {
    // Inicialize o mapa com valores padrão
    var mymap = L.map('mapid').setView([lat_inicial, lng_inicial], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
    }).addTo(mymap);
  
    // Código para adicionar marcadores, etc.
  }
  

  
function generateURL(base, params) {
  const url = new URL(base);
  Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
  return url;
}

