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
console.log(`Tipo Clinica: ${tipoClinica}, Estado: ${estado}, Especialidade: ${especialidade}, Cidade: ${cidade}`);

// Fetch dos Convênios (exemplo)
function fetchConvenios(tipoClinica, tipoProfissional, estado, especialidade, cidade) {
  console.log("Iniciando fetch para obter convênios...");
  // Ajuste a URL conforme o endpoint correto do seu backend
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
    });
}

// Obter os Convênios com base nos parâmetros atuais
fetchConvenios(tipoClinica, tipoProfissional, estado, especialidade, cidade)
.then(convenios => {
  console.log("Convênios obtidos: ", convenios);
  const convenioSelect = document.getElementById("convenios_select");

  const initialOption = document.createElement("option");
initialOption.value = "";
initialOption.text = "Convênios";
convenioSelect.appendChild(initialOption);

// Adicionando as opções ao select com base nos convênios obtidos
convenios.forEach(convenio => {
  const option = document.createElement("option");
  option.value = convenio;
  option.text = convenio;
  convenioSelect.appendChild(option);
});


 // Atualizando o DOM com base nos parâmetros da URL
 document.getElementById("especialidadeSpan").innerHTML = ` ${especialidade || ''}`;
 document.getElementById("estadoSpan").innerHTML = ` ${estado || ''}`;
 document.getElementById("cidadeSpan").innerHTML = `${cidade || ''}`;

 // Lógica baseada no tipo_clinica
 let imageSrc;
 if (tipoClinica === 'Emergência') {
   document.getElementById("tipoProfissionalSpan").innerHTML = "Urgências e Emergências 24h";
   imageSrc = document.getElementById("emergenciaImg").innerText;
 } else if (tipoClinica === 'Laboratório') {
   document.getElementById("tipoProfissionalSpan").innerHTML = "Exames e Laboratórios";
   imageSrc = document.getElementById("laboratorioImg").innerText;


 } else {
   // Outros casos
   document.getElementById("tipoProfissionalSpan").innerHTML = "Outro";
   imageSrc = `http://alguma.url/imagem/Outro_${estado || ''}_${especialidade || ''}_${cidade || ''}.jpg`;
 }
 document.getElementById("suaImagem").src = imageSrc;

 // O restante do seu código...




  // Evento para adicionar o novo filtro à URL
  convenioSelect.addEventListener("change", function() {
    const selectedConvenio = convenioSelect.value;
    console.log("Convênio selecionado: ", selectedConvenio);

    // Adicionando novo parâmetro à URL
    urlObj.searchParams.set("convenios", selectedConvenio);
    window.location.href = urlObj.toString();
  });
});
