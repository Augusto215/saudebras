// Variáveis globais
let estados = [];
let especialidades = [];
let nomes = [];
let tipos = [];

// Funções assíncronas para carregar dados
async function fetchJSON(url) {
  const response = await fetch(url);
  return response.json();
}

async function loadInitialData() {
  try {
    const statesData = await fetchJSON('/get_states/');
    estados = statesData.states;
    
    const specialitiesData = await fetchJSON('/buscar_especialidades/');
    especialidades = specialitiesData.especialidades;

    const nomesData = await fetchJSON('/buscar_nomes/');
    nomes = nomesData.nomes;
    
    const tiposData = await fetchJSON('/buscar_tipos/');
    tipos = tiposData.tipos;

  } catch (error) {
    console.error("Erro ao carregar dados iniciais:", error);
  }
}

// Função para carregar bairros
async function loadBairros() {
  const estado = document.getElementById("estado_input").value;
  const especialidadeInput = document.getElementById("especialidade_input").value;

  let filter = "estado=" + estado;
  if (especialidadeInput) {
    filter += "&especialidade=" + especialidadeInput;
  }

  const bairrosData = await fetchJSON('/buscar_bairros/?' + filter);
  const bairros = bairrosData.bairros;

  const bairrosSection = document.getElementById('bairros_section');
  bairrosSection.innerHTML = '';

  bairros.forEach(bairro => {
    const checkbox = document.createElement('input');
    checkbox.type = "checkbox";
    checkbox.value = bairro.nome;  // Assumindo que o objeto bairro tem uma propriedade "nome"
    checkbox.id = bairro.nome;

    const label = document.createElement('label');
    label.htmlFor = bairro.nome;
    label.textContent = bairro.nome;

    bairrosSection.appendChild(checkbox);
    bairrosSection.appendChild(label);
  });
}

// Função para filtrar opções
function filterOptions(inputId, especialidadesArray, nomesArray, tiposArray, listId) {
  const inputElement = document.getElementById(inputId);
  const listElement = document.getElementById(listId);
  const query = inputElement.value.toLowerCase();
  
  let filteredOptions = [];
  
  // Condicionais para verificar qual input está sendo utilizado
  if (inputId === "estado_input" && estados) {
    filteredOptions.push(...estados.filter(option => option.toLowerCase().includes(query)).slice(0, 10));
  }
  
  if (inputId === "especialidade_input") {
    if (especialidadesArray) filteredOptions.push(...especialidadesArray.filter(option => option.toLowerCase().includes(query)).slice(0, 10));
    if (nomesArray) filteredOptions.push(...nomesArray.filter(option => option.toLowerCase().includes(query)).slice(0, 10));
    if (tiposArray) filteredOptions.push(...tiposArray.filter(option => option.toLowerCase().includes(query)).slice(0, 10));
  }
  
  listElement.innerHTML = '';
  
  filteredOptions.forEach(option => {
    const listItem = document.createElement('li');
    const optionText = document.createTextNode(option);
    listItem.appendChild(optionText);
    
    const span = document.createElement('span');
    
    if (especialidadesArray && especialidadesArray.includes(option)) {
      span.textContent = ' (Especialidade)';
    }
    
    if (nomesArray && nomesArray.includes(option)) {
      span.textContent = ' (Nome)';
    }
    
    if (tiposArray && tiposArray.includes(option)) {
      span.textContent = ' (Tipo Profissional)';
    }
    
    if (estados && estados.includes(option)) {
      span.innerHTML = '<i class="bi bi-geo-alt"></i>';
      span.classList.add("icon-localizacao");
    }
    
    listItem.appendChild(span);
    
    listItem.onclick = () => { 
      inputElement.value = option; 
      listElement.innerHTML = ''; 
      if (nomes.includes(option)) {
        window.location.href = "?nome=" + option;
        return;
      }
    };
    
    listElement.appendChild(listItem);
  });
}


// Event listeners
document.getElementById("estado_input").addEventListener("input", function() {
  filterOptions('estado_input', estados, null, null, 'estado_list');
  loadBairros();
});

document.getElementById("especialidade_input").addEventListener("input", function() {
  filterOptions('especialidade_input', especialidades, nomes, tipos, 'especialidade_list');
  loadBairros();
});

document.getElementById("search_button").addEventListener("click", function() {
  const estado = document.getElementById("estado_input").value;
  const especialidadeInput = document.getElementById("especialidade_input").value;
  let newUrl = "/profissionais/?";
  
  if (estado) newUrl += "estado=" + estado + "&";
  if (especialidadeInput) {
    if (nomes.includes(especialidadeInput)) {
      newUrl += "nome=" + especialidadeInput;
    } else if (tipos.includes(especialidadeInput)) {
      newUrl += "tipo_profissional=" + especialidadeInput;
    } else if (especialidades.includes(especialidadeInput)) {
      newUrl += "especialidade=" + especialidadeInput;
    }
  }
  window.location.href = newUrl;
});

// Carregamento inicial
document.addEventListener('DOMContentLoaded', () => {
  loadInitialData().then(() => loadBairros());
});

