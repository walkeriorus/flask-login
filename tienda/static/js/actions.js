const toggleDisabled = function( el ){
    el.toggleAttribute('disabled')
}
const activarInputsAntesDeEnviar = function( event ){
    event.preventDefault()
    let inputs = document.querySelectorAll('input')
    for(input of inputs){
        toggleDisabled(input)
    }
    event.target.submit()
}


const formulario = document.getElementById('form');
formulario.addEventListener('submit', activarInputsAntesDeEnviar)
