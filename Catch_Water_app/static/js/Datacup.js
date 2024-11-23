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

// Envoi des données au backend
submitBtn.addEventListener("click", () => {
  const selectedAddress = addressInput.value; // Adresse à envoyer
  const personnes = document.getElementById("personnes").value; // Récupère la valeur du champ "personnes"

  if (!selectedAddress || !personnes) return; // Vérifie si les deux champs sont remplis

  // Masquer les éléments du formulaire

  submitBtn.style.display = "none";

  // Afficher le message de confirmation
  const confirmationMessage = document.getElementById("confirmationMessage");
//   const confirmationAddress = document.getElementById("confirmationAddress");
//   const confirmationPersonnes = document.getElementById("confirmationPersonnes");

//   // Mettre à jour le contenu de la div de confirmation
//   confirmationAddress.textContent = `Adresse : ${selectedAddress}`;
//   confirmationPersonnes.textContent = `Nombre de personnes : ${personnes}`;

  // Afficher la div de confirmation
  confirmationMessage.style.display = "block";

});

// Écouteur sur l'input pour la recherche
addressInput.addEventListener("input", function (e) {
  const query = e.target.value;

  // Débouncer pour limiter les requêtes
  clearTimeout(debounceTimeout);
  debounceTimeout = setTimeout(() => {
    if (query.trim() === "") {
      updateSuggestions([]);
      return;
    }

    // Requête au backend pour rechercher des adresses
    fetch("http://127.0.0.1:5000/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: query }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.features && data.features.length > 0) {
          updateSuggestions(data.features);
        } else {
          updateSuggestions([]);
        }
      })
      .catch((error) => {
        console.error("Erreur:", error);
        updateSuggestions([]);
      });
  }, 300); // Délai pour débouncer
});

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

