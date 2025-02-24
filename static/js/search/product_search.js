// product_search.js
document.addEventListener('DOMContentLoaded', function () {
    // Initialize all components
    initializeSupplierSearch();
    initializeProductSearch();
    initializeTableFunctionality();
});

function initializeSupplierSearch() {
    const supplierInput = document.getElementById('supplier-search');
    const supplierList = document.getElementById('supplier-list');

    supplierInput.addEventListener('input', async function() {
        const query = this.value.trim();
        
        if (query.length > 0) {
            try {
                const response = await fetch(`/api/suppliers/search?query=${encodeURIComponent(query)}`);
                if (!response.ok) throw new Error('Network response was not ok');
                const suppliers = await response.json();
                
                supplierList.innerHTML = suppliers.map(supplier => 
                    `<li class="p-2 hover:bg-gray-200 cursor-pointer">${supplier}</li>`
                ).join('');
                
                supplierList.classList.remove('hidden');
                supplierInput.classList.add('text-black');
            } catch (error) {
                console.error('Error fetching suppliers:', error);
            }
        } else {
            supplierList.classList.add('hidden');
            supplierInput.classList.remove('text-black');
        }
    });

    supplierList.addEventListener('click', function(event) {
        if (event.target.tagName === 'LI') {
            supplierInput.value = event.target.textContent;
            supplierInput.classList.add('text-black');
            supplierList.classList.add('hidden');
            filterTableBySupplier(event.target.textContent);
        }
    });
}

function initializeProductSearch() {
    const productInput = document.getElementById('product-search-part2');
    let searchTimeout;

    productInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        searchTimeout = setTimeout(async () => {
            if (query.length >= 2) {
                try {
                    const response = await fetch(`/api/products/search?query=${encodeURIComponent(query)}`);
                    if (!response.ok) throw new Error('Network response was not ok');
                    const products = await response.json();
                    displaySearchResults(products);
                } catch (error) {
                    console.error('Error searching products:', error);
                }
            }
        }, 300);
    });
}

function displaySearchResults(products) {
    const tableBody = document.getElementById('costings-table-body');
    tableBody.innerHTML = ''; // Clear existing rows

    products.forEach(product => {
        const row = createTableRow(product);
        tableBody.appendChild(row);
    });

    // Add a few empty rows at the end
    for (let i = 0; i < 3; i++) {
        tableBody.appendChild(createEmptyRow());
    }
}

function createTableRow(product) {
    const row = document.createElement('tr');
    row.className = 'supplier-row border-b border-gray-200';
    row.innerHTML = `
        <td class="px-4 py-2 supplier-name">
            <input type="text" value="${product.SUPPLIER || ''}" class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 form-control">
        </td>
        <td class="px-6 py-2 ingredient-name">
            <input type="text" value="${product.INGREDIENT || ''}" class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 form-control">
        </td>
        <td class="px-2 py-2 unit">
            <input type="text" value="${product.UNIT || ''}" class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 form-control">
        </td>
        <td class="px-2 py-2 unit-cost">
            <input type="number" value="${product.UNIT_COST || ''}" step="0.01" min="0" class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 unit-cost-input form-control small-width">
        </td>
        <td class="hidden">
            <input type="number" value="${product.RUC || ''}" class="ruc-input">
        </td>
        <td class="px-2 py-2 qty">
            <input type="number" min="0" class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 qty-input form-control small-width">
        </td>
        <td class="px-6 py-2 subtotal font-medium subtotal-cell">0.00</td>
        <td class="px-5 py-2 comments">
            <input type="text" class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 comment-input form-control">
        </td>
        <td class="px-4 py-2 actions">
            <button type="button" class="px-3 py-1 text-red-600 hover:text-red-800 transition-colors delete-ingredient">
                <i class="fas fa-trash-alt"></i>
            </button>
        </td>
    `;
    return row;
}

function createEmptyRow() {
    const row = document.createElement('tr');
    row.className = 'supplier-row border-b border-gray-200';
    row.innerHTML = `
        <td class="px-4 py-2 supplier-name">
            <input type="text" class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 form-control">
        </td>
        <td class="px-6 py-2 ingredient-name">
            <input type="text" class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 form-control">
        </td>
        <td class="px-2 py-2 unit">
            <input type="text" class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 form-control">
        </td>
        <td class="px-2 py-2 unit-cost">
            <input type="number" step="0.01" min="0" class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 unit-cost-input form-control small-width">
        </td>
        <td class="hidden">
            <input type="number" class="ruc-input">
        </td>
        <td class="px-2 py-2 qty">
            <input type="number" min="0" class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 qty-input form-control small-width">
        </td>
        <td class="px-6 py-2 subtotal font-medium subtotal-cell">0.00</td>
        <td class="px-5 py-2 comments">
            <input type="text" class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 comment-input form-control">
        </td>
        <td class="px-4 py-2 actions">
            <button type="button" class="px-3 py-1 text-red-600 hover:text-red-800 transition-colors delete-ingredient">
                <i class="fas fa-trash-alt"></i>
            </button>
        </td>
    `;
    return row;
}

function initializeTableFunctionality() {
    const tableBody = document.getElementById('costings-table-body');

    // Subtotal calculation
    tableBody.addEventListener('input', function(e) {
        if (e.target.classList.contains('unit-cost-input') || 
            e.target.classList.contains('qty-input')) {
            updateRowSubtotal(e.target.closest('tr'));
        }
    });

    // Delete functionality
    tableBody.addEventListener('click', function(e) {
        if (e.target.classList.contains('delete-ingredient') || 
            e.target.closest('.delete-ingredient')) {
            const row = e.target.closest('tr');
            clearRow(row);
        }
    });
}

function updateRowSubtotal(row) {
    const unitCost = parseFloat(row.querySelector('.unit-cost-input').value) || 0;
    const qty = parseFloat(row.querySelector('.qty-input').value) || 0;
    const subtotal = unitCost * qty;
    row.querySelector('.subtotal-cell').textContent = subtotal.toFixed(2);
}

function clearRow(row) {
    row.querySelectorAll('input').forEach(input => input.value = '');
    row.querySelector('.subtotal-cell').textContent = '0.00';
}

function filterTableBySupplier(supplier) {
    const tableBody = document.getElementById('costings-table-body');
    const rows = tableBody.querySelectorAll('tr');
    
    rows.forEach(row => {
        const supplierInput = row.querySelector('.supplier-name input');
        if (supplierInput.value && supplierInput.value !== supplier) {
            row.classList.add('hidden');
        } else {
            row.classList.remove('hidden');
        }
    });
}
