//document.addEventListener('DOMContentLoaded', function() {


    // CEP Validation for both forms
  //  validateCep('registerCEP');
    //validateCep('clientCEP');


// });



//function validateCep(cepElementId) {
    // document.getElementById(cepElementId).addEventListener('blur', function() {
//      const cep = this.value.replace(/\D/g, '');
  //      if (cep !== "") {
       //     const validacep = /^[0-9]{8}$/;
         //   if (validacep.test(cep)) {
           //     fetch(`https://viacep.com.br/ws/${cep}/json/`)
             //       .then(response => response.json())
               //     .then(data => {
                 //       if (!data.erro) {
                   //         const infoCep = `
                     //           <p><strong>Estado:</strong> ${data.uf}</p>
                       //         <p><strong>Cidade:</strong> ${data.localidade}</p>
                         //       <p><strong>Bairro:</strong> ${data.bairro}</p>
                           //     <p><strong>Logradouro:</strong> ${data.logradouro}</p>
                            // `;
                            //document.querySelector(`#${cepElementId} ~ .registerCEP`).innerHTML = infoCep;
                        //} else {
                          //  alert("CEP não encontrado.");
                        //}
                    //});
            //} else {
              //  alert("Formato de CEP inválido.");
            //}
        //} else {
          //  alert("Por favor, preencha o CEP.");
        //}
    //});
//}

