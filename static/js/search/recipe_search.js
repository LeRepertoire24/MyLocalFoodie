// Tab Switching Logic
const myRecipesTab = document.getElementById('myRecipesTab');
const allRecipesTab = document.getElementById('allRecipesTab');
const myRecipesContent = document.getElementById('myRecipes');
const allRecipesContent = document.getElementById('allRecipes');

myRecipesTab.addEventListener('click', () => {
    myRecipesTab.classList.add('active');
    allRecipesTab.classList.remove('active');
    myRecipesContent.classList.remove('hidden');
    allRecipesContent.classList.add('hidden');
});

allRecipesTab.addEventListener('click', () => {
    allRecipesTab.classList.add('active');
    myRecipesTab.classList.remove('active');
    allRecipesContent.classList.remove('hidden');
    myRecipesContent.classList.add('hidden');
});

// Search Functionality
const searchInput = document.getElementById('searchInput');
const cuisineInput = document.getElementById('cuisineInput');
const dietaryInput = document.getElementById('dietaryInput');
const cookeryMethodInput = document.getElementById('cookeryMethodInput');
const ingredientInput = document.getElementById('ingredientInput');
const searchRecipesBtn = document.getElementById('searchRecipesBtn');
const clearFiltersBtn = document.getElementById('clearFilters');
const myRecipeGrid = document.getElementById('myRecipeGrid');
const allRecipeGrid = document.getElementById('allRecipeGrid');
const recipeModal = document.createElement('div');

// Modal setup
recipeModal.id = 'recipeModal';
recipeModal.classList.add('fixed', 'inset-0', 'z-50', 'hidden', 'bg-black', 'bg-opacity-50', 'flex', 'items-center', 'justify-center');
document.body.appendChild(recipeModal);
recipeModal.innerHTML = `
  <div class="bg-white p-6 rounded-lg shadow-lg max-w-full w-11/12 relative">
    <button id="closeModal" class="absolute top-2 right-2 text-gray-500 hover:text-gray-700">&times;</button>
    <iframe id="recipeFrame" class="w-full h-[90vh] rounded-lg" frameborder="0"></iframe>
  </div>
`;

const recipeFrame = document.getElementById('recipeFrame');
const closeModal = document.getElementById('closeModal');

// Close modal on button click
closeModal.addEventListener('click', () => {
    recipeModal.classList.add('hidden');
    recipeFrame.src = '';
});

// Close modal on outside click
recipeModal.addEventListener('click', (event) => {
    if (event.target === recipeModal) {
        recipeModal.classList.add('hidden');
        recipeFrame.src = '';
    }
});

async function fetchRecipes(tab) {
    const apiUrl = tab === 'myRecipes' ? '/api/user_recipes' : '/api/global_recipes';

    const queryParams = new URLSearchParams({
        search_query: searchInput.value.trim(),
        ingredient: ingredientInput.value.trim(),
        cuisine: cuisineInput.value.trim(),
        method: cookeryMethodInput.value.trim(),
        dietary: dietaryInput.value.trim(),
    });

    try {
        const response = await fetch(`${apiUrl}?${queryParams.toString()}`);
        if (!response.ok) throw new Error('Failed to fetch recipes.');

        const recipes = await response.json();
        renderRecipes(recipes, tab);
    } catch (error) {
        console.error('Error fetching recipes:', error);
    }
}

function renderRecipes(recipes, tab) {
    const grid = tab === 'myRecipes' ? myRecipeGrid : allRecipeGrid;
    grid.innerHTML = '';

    if (recipes.length === 0) {
        grid.innerHTML = '<p class="text-gray-500">No recipes found.</p>';
        return;
    }

    recipes.forEach(recipe => {
        // Create recipe card container
        const recipeCard = document.createElement('div');
        recipeCard.classList.add('relative', 'rounded', 'shadow-2xl', 'overflow-hidden', 'cursor-pointer');

        // Create image element
        const recipeImage = document.createElement('img');
        recipeImage.classList.add('w-full', 'h-full', 'object-cover');
        recipeImage.src = recipe.img_url || 'https://via.placeholder.com/596x296';
        recipeImage.alt = recipe.title;

        // Add click event to open modal
        recipeCard.addEventListener('click', () => {
            recipeModal.classList.remove('hidden');
            recipeFrame.src = recipe.display_url;
        });

        // Append elements
        recipeCard.appendChild(recipeImage);
        grid.appendChild(recipeCard);
    });
}

searchRecipesBtn.addEventListener('click', () => {
    const activeTab = myRecipesTab.classList.contains('active') ? 'myRecipes' : 'allRecipes';
    fetchRecipes(activeTab);
});

clearFiltersBtn.addEventListener('click', () => {
    searchInput.value = '';
    cuisineInput.value = '';
    dietaryInput.value = '';
    cookeryMethodInput.value = '';
    ingredientInput.value = '';
    const activeTab = myRecipesTab.classList.contains('active') ? 'myRecipes' : 'allRecipes';
    fetchRecipes(activeTab);
});

// Initial Fetch
fetchRecipes('allRecipes');
