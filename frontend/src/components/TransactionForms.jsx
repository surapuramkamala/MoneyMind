import { useState } from "react";
import { PlusCircle, Wallet, Receipt, LoaderCircle } from "lucide-react";
import api from "../services/api";

function todayLocal() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export default function TransactionForms({ onSaved }) {
  const [activeTab, setActiveTab] = useState("income");
  const [incomeSource, setIncomeSource] = useState("");
  const [incomeAmount, setIncomeAmount] = useState("");
  const [incomeDate, setIncomeDate] = useState(todayLocal());
  const [incomeDescription, setIncomeDescription] = useState("");

  const [expenseCategory, setExpenseCategory] = useState("Food");
  const [expenseAmount, setExpenseAmount] = useState("");
  const [expenseDate, setExpenseDate] = useState(todayLocal());
  const [expenseDescription, setExpenseDescription] = useState("");

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function submitIncome(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");

    try {
      await api.post("/api/income/", {
        source: incomeSource.trim(),
        amount: Number(incomeAmount),
        income_date: incomeDate,
        description: incomeDescription.trim() || null,
      });

      setMessage("Income saved successfully!");
      setIncomeSource("");
      setIncomeAmount("");
      setIncomeDescription("");

      await onSaved();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Could not save income. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  async function submitExpense(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");

    try {
      await api.post("/api/expenses/", {
        category: expenseCategory,
        amount: Number(expenseAmount),
        expense_date: expenseDate,
        description: expenseDescription.trim() || null,
      });

      setMessage("Expense saved successfully!");
      setExpenseAmount("");
      setExpenseDescription("");

      await onSaved();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Could not save expense. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel transaction-panel">
      <div className="transaction-heading">
        <div>
          <h2>Add a Transaction</h2>
          <p>Record money you receive or spend.</p>
        </div>
        <PlusCircle size={24} />
      </div>

      <div className="transaction-tabs">
        <button
          type="button"
          className={activeTab === "income" ? "active" : ""}
          onClick={() => {
            setActiveTab("income");
            setMessage("");
            setError("");
          }}
        >
          <Wallet size={17} />
          Add Income
        </button>

        <button
          type="button"
          className={activeTab === "expense" ? "active" : ""}
          onClick={() => {
            setActiveTab("expense");
            setMessage("");
            setError("");
          }}
        >
          <Receipt size={17} />
          Add Expense
        </button>
      </div>

      {message && <div className="success-message">{message}</div>}
      {error && <div className="error-banner">{error}</div>}

      {activeTab === "income" ? (
        <form className="transaction-form" onSubmit={submitIncome}>
          <label>
            Income source
            <input
              value={incomeSource}
              onChange={(e) => setIncomeSource(e.target.value)}
              placeholder="Example: Monthly Salary"
              maxLength={100}
              required
            />
          </label>

          <label>
            Amount (₹)
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={incomeAmount}
              onChange={(e) => setIncomeAmount(e.target.value)}
              placeholder="Example: 50000"
              required
            />
          </label>

          <label>
            Date
            <input
              type="date"
              value={incomeDate}
              onChange={(e) => setIncomeDate(e.target.value)}
              required
            />
          </label>

          <label>
            Description (optional)
            <input
              value={incomeDescription}
              onChange={(e) => setIncomeDescription(e.target.value)}
              placeholder="Example: November salary"
              maxLength={500}
            />
          </label>

          <button className="primary-button" disabled={loading}>
            {loading ? (
              <LoaderCircle className="spin" size={18} />
            ) : (
              <PlusCircle size={18} />
            )}
            Save Income
          </button>
        </form>
      ) : (
        <form className="transaction-form" onSubmit={submitExpense}>
          <label>
            Expense category
            <select
              value={expenseCategory}
              onChange={(e) => setExpenseCategory(e.target.value)}
            >
              <option>Food</option>
              <option>Rent</option>
              <option>Shopping</option>
              <option>Travel</option>
              <option>Entertainment</option>
              <option>Healthcare</option>
              <option>Education</option>
              <option>Bills</option>
              <option>Groceries</option>
              <option>Other</option>
            </select>
          </label>

          <label>
            Amount (₹)
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={expenseAmount}
              onChange={(e) => setExpenseAmount(e.target.value)}
              placeholder="Example: 1500"
              required
            />
          </label>

          <label>
            Date
            <input
              type="date"
              value={expenseDate}
              onChange={(e) => setExpenseDate(e.target.value)}
              required
            />
          </label>

          <label>
            Description (optional)
            <input
              value={expenseDescription}
              onChange={(e) => setExpenseDescription(e.target.value)}
              placeholder="Example: Weekly groceries"
              maxLength={500}
            />
          </label>

          <button className="primary-button" disabled={loading}>
            {loading ? (
              <LoaderCircle className="spin" size={18} />
            ) : (
              <PlusCircle size={18} />
            )}
            Save Expense
          </button>
        </form>
      )}
    </section>
  );
}