document.addEventListener('DOMContentLoaded', function() {
    // Inicialize o intl-tel-input
    const phoneInput = document.querySelector("#phone");
    const iti = window.intlTelInput(phoneInput, {
      initialCountry: "BR",
      utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.13/js/utils.js"
    });
    phoneInput.value = '+55 ';
    // Ouça para mudanças no país
    phoneInput.addEventListener('countrychange', function() {
      // Obtém o código do país atual
      const countryCode = iti.getSelectedCountryData().dialCode;
      // Atualiza o valor do campo de input com o código do país
      phoneInput.value = '+' + countryCode + ' ';
    });
  
    // Adicione um listener ao formulário
    document.querySelector('#regForm').addEventListener('submit', function(e) {
      // Evite a ação padrão do formulário por enquanto
      e.preventDefault();
  
      // Obtém o input escondido ou cria um novo
      let hiddenInput = document.querySelector('input[name=telefone]');
      if (!hiddenInput) {
        hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'telefone';
        this.appendChild(hiddenInput);
      }
  
      // Preenche o valor completo do telefone
      hiddenInput.value = iti.getNumber();
  
      // Agora você pode prosseguir com a ação de envio do formulário
      this.submit();
    });
  });
  


  document.addEventListener('DOMContentLoaded', function() {
    // CEP Validation for both forms
    validateCep('registerCEP');
    validateEmail('emailId');
    // validateCPF('cpfId'); // REMOVIDO - validação agora é feita apenas no botão "Próximo"


   
});

function validateCep(cepElementId) {
    document.getElementById(cepElementId).addEventListener('blur', function() {
        const cep = this.value.replace(/\D/g, '');
        if (cep !== "") {
            const validacep = /^[0-9]{8}$/;
            if (validacep.test(cep)) {
                fetch(`https://viacep.com.br/ws/${cep}/json/`)
                    .then(response => response.json())
                    .then(data => {
                        if (!data.erro) {
                            const infoCep = `
                                <p><strong>Estado:</strong> ${data.uf}</p>
                                <p><strong>Cidade:</strong> ${data.localidade}</p>
                                <p><strong>Bairro:</strong> ${data.bairro}</p>
                                <p><strong>Logradouro:</strong> ${data.logradouro}</p>
                            `;
                            document.querySelector(`#${cepElementId} ~ .registerCEP`).innerHTML = infoCep;
                        } else {
                            alert("CEP não encontrado.");
                        }
                    });
            } else {
                alert("Formato de CEP inválido.");
            }
        } else {
            alert("Por favor, preencha o CEP.");
        }
    });
}


// Email Validation
function validateEmail(emailId) {
    document.getElementById(emailId).addEventListener('blur', function() {
        const email = this.value;
        const validEmail = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (validEmail.test(email)) {
            // Fazer algo, por exemplo:
            // alert("Email válido.");
        } else {
            alert("Formato de e-mail inválido.");
        }
    });
}

// CPF Validation - DESABILITADA
// A validação do CPF agora é feita apenas no botão "Próximo" com modais personalizadas
// let cpfAlertShown = false; // Variável de controle

// function validateCPF(cpfId) {
//     document.getElementById(cpfId).addEventListener('blur', function() {
//         if (cpfAlertShown) {
//             cpfAlertShown = false; // Resetar a variável
//             return;
//         }

//         const cpf = this.value.replace(/\D/g, '');
//         if (cpf.length === 11) {
//             // Fazer algo, por exemplo:
//             // alert("CPF válido.");
//         } else {
//             alert("CPF inválido.");
//             cpfAlertShown = true; // Marcar que o alerta foi mostrado
//             this.focus(); // Focar o elemento novamente
//         }
//     });
// }

