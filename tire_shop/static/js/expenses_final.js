// Expense Management - Complete CRUD Implementation
class ExpenseManager {
  constructor() {
    this.chart = null;
    this.currentExpenseId = null;
    this.init();
  }

  async init() {
    this.setupEventListeners();
    await this.loadExpenses();
    await this.initChart();
  }

  setupEventListeners() {
    document.getElementById('expense-form').addEventListener('submit', (e) => this.handleSubmit(e));
    document.getElementById('confirm-delete').addEventListener('click', () => this.confirmDelete());
  }

  async loadExpenses() {
    try {
      const response = await fetch('/api/expenses');
      const expenses = await response.json();
      this.renderExpenseTable(expenses);
    } catch (error) {
      console.error('Error loading expenses:', error);
      this.showAlert('Failed to load expenses', 'error');
    }
  }

  renderExpenseTable(expenses) {
    const tableBody = document.getElementById('expense-table-body');
    tableBody.innerHTML = '';

    expenses.forEach(expense => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td class="px-6 py-4 whitespace-nowrap">${new Date(expense.date).toLocaleDateString()}</td>
        <td class="px-6 py-4 whitespace-nowrap">$${expense.amount.toFixed(2)}</td>
        <td class="px-6 py-4 whitespace-nowrap">${this.formatLabel(expense.category)}</td>
        <td class="px-6 py-4 whitespace-nowrap">${this.formatLabel(expense.payment_method)}</td>
        <td class="px-6 py-4">${expense.description || '-'}</td>
        <td class="px-6 py-4 whitespace-nowrap">
          <button onclick="editExpense(${expense.id})" class="text-blue-500 hover:text-blue-700 mr-3">
            <i class="fas fa-edit"></i>
          </button>
          <button onclick="showDeleteConfirm(${expense.id})" class="text-red-500 hover:text-red-700">
            <i class="fas fa-trash"></i>
          </button>
        </td>
      `;
      tableBody.appendChild(row);
    });
  }

  async initChart() {
    try {
      const expenses = await this.fetchExpenses();
      const categories = this.processExpenseData(expenses);
      this.renderChart(categories);
    } catch (error) {
      console.error('Chart Error:', error);
    }
  }

  async fetchExpenses() {
    const response = await fetch('/api/expenses');
    return await response.json();
  }

  processExpenseData(expenses) {
    return expenses.reduce((acc, expense) => {
      acc[expense.category] = (acc[expense.category] || 0) + expense.amount;
      return acc;
    }, {});
  }

  renderChart(categories) {
    const ctx = document.getElementById('expenseChart').getContext('2d');
    
    if (this.chart) this.chart.destroy();
    
    this.chart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: Object.keys(categories).map(this.formatLabel),
        datasets: [{
          data: Object.values(categories),
          backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { 
          legend: { position: 'right' },
          tooltip: {
            callbacks: {
              label: (context) => {
                const label = context.label || '';
                const value = context.raw || 0;
                return `${label}: $${value.toFixed(2)}`;
              }
            }
          }
        }
      }
    });
  }

  formatLabel(label) {
    return label.charAt(0).toUpperCase() + label.slice(1).replace('-', ' ');
  }

  async handleSubmit(e) {
    e.preventDefault();
    
    const formData = {
      id: document.getElementById('expense-id').value || null,
      amount: parseFloat(document.getElementById('amount').value),
      category: document.getElementById('category').value,
      payment_method: document.getElementById('payment_method').value,
      description: document.getElementById('description').value,
      date: document.getElementById('date').value,
      receipt_number: document.getElementById('receipt_number').value
    };

    if (!formData.amount || isNaN(formData.amount)) {
      this.showAlert('Please enter a valid amount', 'error');
      return;
    }

    try {
      const method = formData.id ? 'PUT' : 'POST';
      const url = formData.id ? `/api/expenses/${formData.id}` : '/api/expenses';
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        this.closeExpenseModal();
        this.showAlert(`Expense ${formData.id ? 'updated' : 'added'} successfully`, 'success');
        await this.loadExpenses();
        await this.initChart();
      } else {
        const error = await response.json();
        throw new Error(error.error || 'Failed to save expense');
      }
    } catch (error) {
      console.error('Submission Error:', error);
      this.showAlert(error.message, 'error');
    }
  }

  async editExpense(id) {
    try {
      const response = await fetch(`/api/expenses/${id}`);
      const expense = await response.json();
      
      document.getElementById('expense-id').value = expense.id;
      document.getElementById('amount').value = expense.amount;
      document.getElementById('category').value = expense.category;
      document.getElementById('payment_method').value = expense.payment_method;
      document.getElementById('description').value = expense.description;
      document.getElementById('date').value = expense.date.split('T')[0];
      document.getElementById('receipt_number').value = expense.receipt_number;
      
      document.getElementById('modal-title').textContent = 'Edit Expense';
      this.openExpenseModal();
    } catch (error) {
      console.error('Error editing expense:', error);
      this.showAlert('Failed to load expense details', 'error');
    }
  }

  showDeleteConfirm(id) {
    this.currentExpenseId = id;
    document.getElementById('confirm-modal').classList.remove('hidden');
  }

  async confirmDelete() {
    if (!this.currentExpenseId) return;

    try {
      const response = await fetch(`/api/expenses/${this.currentExpenseId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        this.showAlert('Expense deleted successfully', 'success');
        await this.loadExpenses();
        await this.initChart();
      } else {
        const error = await response.json();
        throw new Error(error.error || 'Failed to delete expense');
      }
    } catch (error) {
      console.error('Deletion Error:', error);
      this.showAlert(error.message, 'error');
    } finally {
      this.closeConfirmModal();
      this.currentExpenseId = null;
    }
  }

  openExpenseModal() {
    document.getElementById('expense-modal').classList.remove('hidden');
  }

  closeExpenseModal() {
    document.getElementById('expense-form').reset();
    document.getElementById('expense-id').value = '';
    document.getElementById('modal-title').textContent = 'Add New Expense';
    document.getElementById('expense-modal').classList.add('hidden');
  }

  closeConfirmModal() {
    document.getElementById('confirm-modal').classList.add('hidden');
  }

  showAlert(message, type) {
    const alert = document.createElement('div');
    alert.className = `fixed top-4 right-4 px-4 py-2 rounded-md text-white ${
      type === 'error' ? 'bg-red-500' : 'bg-green-500'
    }`;
    alert.textContent = message;
    document.body.appendChild(alert);
    
    setTimeout(() => {
      alert.remove();
    }, 3000);
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.expenseManager = new ExpenseManager();
});

// Global functions for HTML onclick handlers
window.openExpenseModal = () => window.expenseManager.openExpenseModal();
window.closeExpenseModal = () => window.expenseManager.closeExpenseModal();
window.editExpense = (id) => window.expenseManager.editExpense(id);
window.showDeleteConfirm = (id) => window.expenseManager.showDeleteConfirm(id);
window.closeConfirmModal = () => window.expenseManager.closeConfirmModal();
