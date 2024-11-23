/**
 * Fonction pour afficher ou masquer un formulaire avec une animation.
 * @param {string} formId - ID du formulaire à afficher/masquer.
 * @param {HTMLInputElement} switchElement - Switch qui déclenche l'action.
 */
function toggleForm(formId, switchElement) {
    const form = document.getElementById(formId);
    if (switchElement.checked) {
      form.style.display = "block"; // Affiche le formulaire
      form.style.opacity = 0;
      setTimeout(() => {
        form.style.opacity = 1;
        form.style.transition = "opacity 0.5s ease-in-out";
      }, 10);
    } else {
      form.style.opacity = 0;
      setTimeout(() => {
        form.style.display = "none"; // Masque le formulaire après l'animation
      }, 500);
    }
  }



  
  let debounceTimeout;
      
const addressInput = document.getElementById("addressInput");
const addressSuggestions = document.getElementById("addressSuggestions");
const submitBtn = document.getElementById("submitBtn");

// Mise à jour des suggestions dans le datalist
function updateSuggestions(options) {
  addressSuggestions.innerHTML = ""; // Efface les suggestions précédentes

  options.forEach((feature) => {
    const option = document.createElement("option");
    option.value = feature.properties.label; // Valeur affichée et envoyée au backend
    addressSuggestions.appendChild(option);
  });
}


      // Activer les tooltips
      document.addEventListener("DOMContentLoaded", function () {
        const tooltipTriggerList = [].slice.call(
          document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        tooltipTriggerList.map(function (tooltipTriggerEl) {
          return new bootstrap.Tooltip(tooltipTriggerEl);
        });
      });

      // Gestion de l'affichage des sections
      function toggleForm(formId, checkbox) {
        const form = document.getElementById(formId);
        form.style.display = checkbox.checked ? "block" : "none";
      }

  // Initialisation des tooltips Bootstrap
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });


// Script pour Potly, Créer les données pour le graphique
   var data = [{
    x: [1, 2, 3, 4, 5],
    y: [10, 15, 13, 17, 21],
    type: 'scatter'
}];

// Ajouter le graphique à l'élément avec l'ID 'myPlot'
Plotly.newPlot('myPlot', data, {
    title: 'Exemple de graphique',
    xaxis: { title: 'X-Axis' },
    yaxis: { title: 'Y-Axis' }
});


var data1 = [{ x: [1, 2, 3], y: [10, 20, 30], type: 'bar' }];
var data2 = [{ labels: ['A', 'B', 'C'], values: [30, 50, 20], type: 'pie' }];

Plotly.newPlot('plot1', data1, { title: 'Graphique en Barres' });
Plotly.newPlot('plot2', data2, { title: 'Graphique en Secteurs' });

var layout = {
    title: 'Graphique Réactif',
    autosize: true
};

Plotly.newPlot('myPlot', data, layout, { responsive: true });