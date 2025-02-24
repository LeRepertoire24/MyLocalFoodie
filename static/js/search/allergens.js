// Function to search allergens based on input filters
async function searchAllergens() {
  const searchQuery = document.getElementById("searchInput").value.toLowerCase();
  const severityFilter = document.getElementById("severityFilter").value;
  const symptomFilter = document.getElementById("symptomFilter").value.toLowerCase();

  // Construct query parameters
  let queryParams = new URLSearchParams();
  if (searchQuery) queryParams.append('search_query', searchQuery);
  if (severityFilter) queryParams.append('severity', severityFilter);
  if (symptomFilter) queryParams.append('symptom', symptomFilter);

  try {
    // Fetch allergens data from the backend API
    const response = await fetch(`/api/allergens?${queryParams.toString()}`);
    if (!response.ok) {
      throw new Error("Failed to fetch allergens");
    }

    const allergensData = await response.json();

    if (allergensData.length === 0) {
      document.getElementById("errorMessage").classList.remove('hidden');
    } else {
      document.getElementById("errorMessage").classList.add('hidden');
      displayResults(allergensData);
    }
  } catch (error) {
    console.error("Error fetching allergens data:", error);
    document.getElementById("errorMessage").classList.remove('hidden');
  }
}

// Function to display allergen results as tiles
function displayResults(allergens) {
  const resultsContainer = document.getElementById("resultsArea");
  resultsContainer.innerHTML = ''; // Clear previous results

  allergens.forEach(allergen => {
    const resultTile = document.createElement("div");
    resultTile.classList.add(
      "p-6",
      "border",
      "rounded-lg",
      "shadow-lg",
      "bg-white",
      "hover:bg-gray-50",
      "cursor-pointer",
      "transition-all",
      "w-full"
    );

    // Severity color coding based on severity level
    const severityColor = getSeverityColor(allergen.severity);

    resultTile.innerHTML = `
      <img
        alt="Image of ${allergen.ingredient}"
        class="rounded-full mx-auto mb-4"
        height="100"
        src="${allergen.img_url || 'https://via.placeholder.com/100'}"
        width="100"
      />
      <h2 class="text-lg font-semibold text-center">${allergen.ingredient}</h2>
      <p class="text-center text-gray-500">Reaction Type: ${allergen.reactionType}</p>
      <p class="text-center">
        <span class="text-black font-semibold">Severity:</span>
        <span class="text-${severityColor}-500 font-semibold">${allergen.severity}</span>
      </p>
      <div class="mt-4 text-center">
        ${
          allergen.symptoms
            ? `<p class="text-black text-sm truncate">${allergen.symptoms.slice(0, 60)}${allergen.symptoms.length > 60 ? '...' : ''}</p>`
            : `<p class="text-black text-sm">No symptoms listed</p>`
        }
      </div>
    `;
    resultTile.onclick = () => showAllergenDetails(allergen);

    resultsContainer.appendChild(resultTile);
  });
}

// Function to determine color based on severity level
function getSeverityColor(severity) {
  // Normalize input to lowercase to handle case insensitivity
  const normalizedSeverity = severity.toLowerCase();

  switch (normalizedSeverity) {
    case 'critical':
      return 'red';
    case 'severe':
      return 'orange';
    case 'high':
      return 'yellow';
    case 'medium':
      return 'green';
    case 'low':
      return 'blue';
    default:
      return 'gray';
  }
}

// Function to display allergen details in a modal
function showAllergenDetails(allergen) {
  const modal = document.getElementById("allergenModal");
  modal.classList.remove("hidden");
  modal.classList.add("flex"); // Ensure flex centering

  document.getElementById("modalIngredient").textContent = allergen.ingredient || 'Unknown Ingredient';

  const severityColor = getSeverityColor(allergen.severity);
  document.getElementById("modalSeverity").innerHTML = `
    <span class="text-${severityColor}-500 font-semibold">${allergen.severity}</span>
  `;

  document.getElementById("modalSymptoms").textContent = allergen.symptoms
    ? allergen.symptoms.join(", ")
    : "No symptoms available";
  document.getElementById("modalDescribedSymptoms").textContent = allergen.describedSymptoms
    ? allergen.describedSymptoms.join(", ")
    : "No described symptoms available";

  const actions = getEmergencyActions(allergen);
  document.getElementById("modalActions").innerHTML = actions;

  const additionalInfo = getAdditionalInformation(allergen);
  document.getElementById("modalAdditionalInfo").innerHTML = additionalInfo;

  // Add emergency message if applicable
  const emergencyMessageContainer = document.getElementById("modalEmergencyMessage");
  if (allergen.severity.toLowerCase() === 'critical') {
    emergencyMessageContainer.innerHTML = `
      <p>
        <span class="text-red-500 font-semibold">CALL EMERGENCY SERVICES IMMEDIATELY:</span>
        <span class="text-blue-600 font-semibold">AUSTRALIA - 000; NEW ZEALAND - 111.</span>
      </p>
    `;
    emergencyMessageContainer.classList.remove("hidden");
  } else {
    emergencyMessageContainer.classList.add("hidden");
  }
}

// Helper function to extract emergency actions from severity matrix
function getEmergencyActions(allergen) {
  const actions = [];

  if (allergen.severityMatrix && allergen.severityMatrix.emergencyActions) {
    const emergencyActions = allergen.severityMatrix.emergencyActions;
    for (let key in emergencyActions) {
      if (emergencyActions[key] && emergencyActions[key].action) {
        actions.push(...emergencyActions[key].action);
      }
    }
  }

  return actions.length > 0
    ? actions.map(action => `<li>${action}</li>`).join("")
    : "<li>No emergency actions available</li>";
}

// Helper function to extract additional information
function getAdditionalInformation(allergen) {
  const additionalInfo = [];

  if (allergen.additionalInformation) {
    for (let key in allergen.additionalInformation) {
      if (allergen.additionalInformation[key]) {
        additionalInfo.push(
          `<li><strong>${key.charAt(0).toUpperCase() + key.slice(1)}:</strong> ${allergen.additionalInformation[key]}</li>`
        );
      }
    }
  }

  return additionalInfo.length > 0
    ? additionalInfo.join("")
    : "<li>No additional information available</li>";
}

// Function to close the modal
function closeModal() {
  const modal = document.getElementById("allergenModal");
  modal.classList.add("hidden");
}

// Function to reset all search filters
function resetSearch() {
  document.getElementById("searchInput").value = '';
  document.getElementById("severityFilter").value = '';
  document.getElementById("symptomFilter").value = '';
  searchAllergens(); // Trigger search with empty filters
}
