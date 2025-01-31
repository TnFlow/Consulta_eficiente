document.addEventListener("DOMContentLoaded", function() {
    let inputField = document.getElementById("client_name");
    
    if (inputField) {
        inputField.addEventListener("input", function() {
            let query = this.value;
            if (query.length < 2) return;  // Espera al menos 2 caracteres para evitar consultas innecesarias

            fetch(`/autocomplete?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    let suggestionsBox = document.getElementById("suggestions");
                    suggestionsBox.innerHTML = "";  // Limpiar sugerencias previas
                    
                    data.forEach(client => {
                        let div = document.createElement("div");
                        div.textContent = client;
                        div.classList.add("suggestion-item");  // Agrega clase para estilos
                        div.onclick = function() {
                            inputField.value = client;
                            suggestionsBox.innerHTML = "";
                        };
                        suggestionsBox.appendChild(div);
                    });
                })
                .catch(error => console.error("Error en la búsqueda:", error));
        });
    } else {
        console.error("No se encontró el campo de entrada con id 'client_name'");
    }
});
