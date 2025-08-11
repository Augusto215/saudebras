// Obtendo a URL atual
console.log("Obtendo a URL atual...");
const currentURL = window.location.href;
console.log("URL atual: ", currentURL);

// Parsing dos parâmetros
console.log("Parsing dos parâmetros...");
const urlObj = new URL(currentURL);

const tipoClinica = urlObj.searchParams.get("tipo_clinica");
const tipoProfissional = urlObj.searchParams.get("tipo_profissional");
const estado = urlObj.searchParams.get("estado");
const especialidade = urlObj.searchParams.get("especialidade");
const cidade = urlObj.searchParams.get("cidade");
const convenioAtual = urlObj.searchParams.get("convenios");
console.log(`Tipo Clinica: ${tipoClinica}, Estado: ${estado}, Especialidade: ${especialidade}, Cidade: ${cidade}, Convênio: ${convenioAtual}`);

// Fetch dos Convênios
function fetchConvenios(tipoClinica, tipoProfissional, estado, especialidade, cidade) {
  console.log("Iniciando fetch para obter convênios...");
  let url = `/buscar_convenios_por_tipo_clinica/?`;
  if (tipoClinica) url += `tipo_clinica=${encodeURIComponent(tipoClinica)}&`;
  if (tipoProfissional) url += `tipo_profissional=${encodeURIComponent(tipoProfissional)}&`;
  if (estado) url += `estado=${encodeURIComponent(estado)}&`;
  if (especialidade) url += `especialidade=${encodeURIComponent(especialidade)}&`;
  if (cidade) url += `cidade=${encodeURIComponent(cidade)}&`;
  url = url.replace(/&$/, "");
  return fetch(url)
    .then(response => response.json())
    .then(data => {
      console.log("Dados recebidos para convênios: ", data);
      return data.convenios;
    })
    .catch(error => {
      console.error("Erro ao buscar convênios:", error);
      return [];
    });
}

// Obter os Convênios com base nos parâmetros atuais
fetchConvenios(tipoClinica, tipoProfissional, estado, especialidade, cidade)
.then(convenios => {
  console.log("Convênios obtidos: ", convenios);
  const convenioSelect = document.getElementById("convenios_select");

  // Limpar opções existentes
  convenioSelect.innerHTML = '';

  // Opção padrão
  const initialOption = document.createElement("option");
  initialOption.value = "";
  initialOption.text = "Todos os convênios";
  convenioSelect.appendChild(initialOption);

  // Adicionando as opções ao select com base nos convênios obtidos
  convenios.forEach(convenio => {
    const option = document.createElement("option");
    option.value = convenio;
    option.text = convenio;
    convenioSelect.appendChild(option);
  });

  // Definir o valor selecionado baseado no parâmetro da URL
  if (convenioAtual) {
    convenioSelect.value = convenioAtual;
  }

  // Atualizando o DOM com base nos parâmetros da URL
  document.getElementById("especialidadeSpan").innerHTML = ` ${especialidade || 'Todas as especialidades'}`;
  document.getElementById("estadoSpan").innerHTML = ` ${estado || ''}`;
  document.getElementById("cidadeSpan").innerHTML = `${cidade || 'Todas as cidades'}`;

  // Lógica baseada no tipo_clinica
  let tipoDisplay = "Clínicas";
  if (tipoClinica === 'Emergência') {
    tipoDisplay = "Urgências e Emergências 24h";
  } else if (tipoClinica === 'Laboratório') {
    tipoDisplay = "Exames e Laboratórios";
  } else if (tipoClinica) {
    tipoDisplay = tipoClinica;
  }
  
  document.getElementById("tipoProfissionalSpan").innerHTML = tipoDisplay;

  // Evento para filtrar por convênio
  convenioSelect.addEventListener("change", function() {
    const selectedConvenio = convenioSelect.value;
    console.log("Convênio selecionado: ", selectedConvenio);

    // Criando nova URL
    const newUrlObj = new URL(currentURL);
    
    if (selectedConvenio) {
      newUrlObj.searchParams.set("convenios", selectedConvenio);
    } else {
      newUrlObj.searchParams.delete("convenios");
    }
    
    // Remover o parâmetro de página ao filtrar
    newUrlObj.searchParams.delete("page");
    
    window.location.href = newUrlObj.toString();
  });
})
.catch(error => {
  console.error("Erro ao carregar convênios:", error);
  // Mesmo em caso de erro, atualizar o DOM básico
  document.getElementById("especialidadeSpan").innerHTML = ` ${especialidade || 'Todas as especialidades'}`;
  document.getElementById("estadoSpan").innerHTML = ` ${estado || ''}`;
  document.getElementById("cidadeSpan").innerHTML = `${cidade || 'Todas as cidades'}`;
  
  let tipoDisplay = "Clínicas";
  if (tipoClinica === 'Emergência') {
    tipoDisplay = "Urgências e Emergências 24h";
  } else if (tipoClinica === 'Laboratório') {
    tipoDisplay = "Exames e Laboratórios";
  } else if (tipoClinica) {
    tipoDisplay = tipoClinica;
  }
  
  document.getElementById("tipoProfissionalSpan").innerHTML = tipoDisplay;
});
