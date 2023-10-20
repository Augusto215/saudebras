// Obtendo a URL atual
console.log("Obtendo a URL atual...");
const currentURL = window.location.href;
console.log("URL atual: ", currentURL);

// Parsing dos parâmetros
console.log("Parsing dos parâmetros...");
const urlObj = new URL(currentURL);
const tipoProfissional = urlObj.searchParams.get("tipo_profissional");
const estado = urlObj.searchParams.get("estado");
const especialidade = urlObj.searchParams.get("especialidade");
const cidade = urlObj.searchParams.get("cidade");
console.log(`Tipo profissional: ${tipoProfissional}, Estado: ${estado}, Especialidade: ${especialidade}, Cidade: ${cidade}`);

// Fetch dos Convênios (exemplo)
function fetchConvenios(tipoProfissional, estado, especialidade, cidade) {
  console.log("Iniciando fetch para obter convênios...");
  return fetch(`/buscar_convenios_por_tipo_profissional/?tipo_profissional=${tipoProfissional}&estado=${estado}&especialidade=${especialidade}&cidade=${cidade}`)
    .then(response => response.json())
    .then(data => {
      console.log("Dados recebidos para convênios: ", data);
      return data.convenios;
    });
}

// Obter os Convênios com base nos parâmetros atuais
fetchConvenios(tipoProfissional, estado, especialidade, cidade)
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

 // Lógica baseada no tipo_profissional
 let imageSrc;
 if (tipoProfissional === 'Médico') {
   document.getElementById("tipoProfissionalSpan").innerHTML = "Consultas Médicas";
   imageSrc = document.getElementById("medicoImg").innerText;
 } else if (tipoProfissional === 'Dentista') {
   document.getElementById("tipoProfissionalSpan").innerHTML = "Consultas Odontológicas";
   imageSrc = document.getElementById("dentistaImg").innerText;


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
    window.location.href = urlObj.toString();
  });
});
