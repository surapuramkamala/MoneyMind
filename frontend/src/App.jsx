
import { useEffect, useState } from "react";
import {
  Wallet, TrendingUp, TrendingDown, LayoutDashboard,
  FileText, BriefcaseBusiness, Settings, LogOut, Bell,
  Plus, CalendarDays, ArrowUpRight, ArrowDownRight,
  Receipt, PiggyBank, LoaderCircle, Bot
} from "lucide-react";

import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  Tooltip, CartesianGrid, PieChart, Pie, Cell, Legend
} from "recharts";

import api from "./services/api";
import TransactionForms from "./components/TransactionForms";
import "./App.css";

const COLORS = ["#12b8a6", "#f5b82e", "#8b5cf6", "#ef4899", "#4385f5", "#f97316"];

const money = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(Number(value || 0));

function AuthScreen({ onLogin }) {
  const [register, setRegister] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (register) {
        await api.post("/api/auth/register", {
          full_name: name,
          email,
          password
        });
      }

      const result = await api.post("/api/auth/login", { email, password });
      localStorage.setItem("moneymind_token", result.data.access_token);
      onLogin();
    } catch (err) {
      setError(err.response?.data?.detail || "Authentication failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <div className="logo-mark">M</div>
        <h1>MoneyMind AI</h1>
        <p>Understand your money. Make smarter decisions.</p>

        {register && (
          <label>Full name
            <input value={name} onChange={e => setName(e.target.value)} required />
          </label>
        )}

        <label>Email
          <input type="email" value={email}
            onChange={e => setEmail(e.target.value)} required />
        </label>

        <label>Password
          <input type="password" value={password}
            onChange={e => setPassword(e.target.value)} required />
        </label>

        {error && <div className="error-message">{error}</div>}

        <button className="purple-button" disabled={loading}>
          {loading ? "Please wait..." : register ? "Create account" : "Login"}
        </button>

        <p className="auth-switch">
          {register ? "Already have an account?" : "New to MoneyMind AI?"}
          <button type="button" onClick={() => setRegister(!register)}>
            {register ? " Login" : " Create account"}
          </button>
        </p>
      </form>
    </div>
  );
}

function SummaryCard({ title, amount, icon: Icon, tone, note }) {
  return (
    <div className="summary-card">
      <div className={`summary-icon ${tone}`}><Icon size={21} /></div>
      <div className="summary-info">
        <span>{title}</span>
        <strong>{money(amount)}</strong>
        <small>{note}</small>
      </div>
    </div>
  );
}

function Dashboard({ onLogout }) {
  const currentDate = new Date();
  const [year, setYear] = useState(currentDate.getFullYear());
  const [month, setMonth] = useState(currentDate.getMonth() + 1);

  const [monthly, setMonthly] = useState(null);
  const [yearly, setYearly] = useState(null);
  const [breakdown, setBreakdown] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [asking, setAsking] = useState(false);

  async function loadDashboard() {
    setLoading(true);
    setError("");

    try {
      const [m, y, b, income, expenses] = await Promise.all([
        api.get("/api/reports/monthly", { params: { year, month } }),
        api.get("/api/reports/yearly", { params: { year } }),
        api.get("/api/reports/expense-breakdown", { params: { year, month } }),
        api.get("/api/income/"),
        api.get("/api/expenses/")
      ]);

      setMonthly(m.data);
      setYearly(y.data);
      setBreakdown(b.data);

      const incomeRows = Array.isArray(income.data) ? income.data : [];
      const expenseRows = Array.isArray(expenses.data) ? expenses.data : [];

      const combined = [
        ...incomeRows.map(item => ({
          id: `income-${item.id}`,
          title: item.source,
          amount: Number(item.amount),
          date: item.income_date,
          type: "income"
        })),
        ...expenseRows.map(item => ({
          id: `expense-${item.id}`,
          title: item.category,
          amount: Number(item.amount),
          date: item.expense_date,
          type: "expense"
        }))
      ];

      combined.sort((a, b) => new Date(b.date) - new Date(a.date));
      setTransactions(combined.slice(0, 6));
    } catch (err) {
      if (err.response?.status === 401) {
        onLogout();
        return;
      }
      setError(err.response?.data?.detail || "Unable to load dashboard data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, [year, month]);

  async function askAI(e) {
    e.preventDefault();
    if (!question.trim()) return;

    setAsking(true);
    setAnswer("");

    try {
      const result = await api.post("/api/advisor/ask", {
        question,
        year,
        month
      });
      setAnswer(result.data.answer);
      setQuestion("");
    } catch (err) {
      setAnswer(err.response?.data?.detail || "AI advisor request failed.");
    } finally {
      setAsking(false);
    }
  }

  const chartData = (yearly?.monthly_summary || []).map(item => ({
    month: new Date(year, item.month - 1).toLocaleString("en-IN", {
      month: "short"
    }),
    Income: Number(item.total_income),
    Expense: Number(item.total_expenses)
  }));

  const pieData = (breakdown?.categories || []).map(item => ({
    name: item.category,
    value: Number(item.total_amount)
  }));

  const selectedMonth = new Date(year, month - 1).toLocaleString("en-IN", {
    month: "long"
  });

  function scrollToTransactions() {
    document.getElementById("transactions")?.scrollIntoView({
      behavior: "smooth",
      block: "start"
    });
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-logo">M</div>
          <div>
            <strong>MoneyMind AI</strong>
            <span>Personal Finance</span>
          </div>
        </div>

        <div className="sidebar-label">WORKSPACE</div>
        <nav className="side-nav">
          <a className="nav-link active" href="#dashboard">
            <LayoutDashboard size={17} /> Dashboard
          </a>
          <a className="nav-link" href="#reports">
            <FileText size={17} /> Reports
          </a>
          <a className="nav-link" href="#investments">
            <BriefcaseBusiness size={17} /> Investments
          </a>
          <a className="nav-link" href="#settings">
            <Settings size={17} /> Settings
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="profile-avatar">M</div>
          <div className="profile-text">
            <strong>My Account</strong>
            <span>MoneyMind user</span>
          </div>
          <button className="sidebar-logout" onClick={onLogout} title="Logout">
            <LogOut size={17} />
          </button>
        </div>
      </aside>

      <main className="main-area" id="dashboard">
        <header className="topbar">
          <div className="mobile-brand">
            <div className="sidebar-logo">M</div>
            <strong>MoneyMind AI</strong>
          </div>

          <div className="topbar-actions">
            <button className="header-icon" title="Notifications">
              <Bell size={18} />
            </button>

            <select value={month} onChange={e => setMonth(Number(e.target.value))}>
              {Array.from({ length: 12 }, (_, i) => (
                <option value={i + 1} key={i + 1}>
                  {new Date(year, i).toLocaleString("en-IN", { month: "long" })}
                </option>
              ))}
            </select>

            <select value={year} onChange={e => setYear(Number(e.target.value))}>
              {Array.from({ length: 7 }, (_, i) => {
                const value = currentDate.getFullYear() - i;
                return <option value={value} key={value}>{value}</option>;
              })}
            </select>

            <button className="purple-button add-expense-top" onClick={scrollToTransactions}>
              <Plus size={16} /> Add transaction
            </button>
          </div>
        </header>

        <div className="page-content">
          <div className="page-heading">
            <div>
              <span className="eyebrow">OVERVIEW</span>
              <h1>Dashboard</h1>
              <p>Welcome back! Here's your financial summary.</p>
            </div>
            <div className="date-label">
              <CalendarDays size={16} />
              {selectedMonth} {year}
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          {loading ? (
            <div className="dashboard-loading">
              <LoaderCircle className="spin" /> Loading your finances...
            </div>
          ) : (
            <>
              <section className="summary-grid">
                <SummaryCard
                  title="Current Balance"
                  amount={monthly?.cash_remaining}
                  icon={Wallet}
                  tone="purple"
                  note="Estimated monthly cash flow"
                />
                <SummaryCard
                  title="Total Income"
                  amount={monthly?.total_income}
                  icon={TrendingUp}
                  tone="green"
                  note="Income recorded this month"
                />
                <SummaryCard
                  title="Total Expense"
                  amount={monthly?.total_expenses}
                  icon={TrendingDown}
                  tone="blue"
                  note="Spending recorded this month"
                />
              </section>

              <section className="panel chart-panel" id="reports">
                <div className="panel-title-row">
                  <div>
                    <h2>Total Income & Expense Flow</h2>
                    <p>Monthly financial activity for {year}</p>
                  </div>
                  <span className="chart-legend">
                    <i className="dot income-dot" /> Income
                    <i className="dot expense-dot" /> Expense
                  </span>
                </div>

                <div className="main-chart">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} barGap={5}>
                      <CartesianGrid stroke="#edf0f5" vertical={false} />
                      <XAxis dataKey="month" axisLine={false} tickLine={false} />
                      <YAxis
                        axisLine={false}
                        tickLine={false}
                        tickFormatter={value => value >= 1000 ? `${value / 1000}k` : value}
                      />
                      <Tooltip formatter={value => money(value)} />
                      <Bar dataKey="Income" fill="#12b981" radius={[3, 3, 0, 0]} />
                      <Bar dataKey="Expense" fill="#4385f5" radius={[3, 3, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </section>

              <section className="bottom-grid">
                <div className="panel recent-panel">
                  <div className="panel-title-row">
                    <div>
                      <h2>Recent Income & Expense</h2>
                      <p>Your latest recorded transactions</p>
                    </div>
                    <button className="small-link" onClick={scrollToTransactions}>
                      Add new
                    </button>
                  </div>

                  {transactions.length === 0 ? (
                    <div className="empty-state">
                      No transactions yet. Add your first income or expense below.
                    </div>
                  ) : (
                    <div className="transaction-list">
                      {transactions.map(item => (
                        <div className="transaction-row" key={item.id}>
                          <div className={`transaction-symbol ${item.type}`}>
                            {item.type === "income"
                              ? <ArrowDownRight size={17} />
                              : <ArrowUpRight size={17} />}
                          </div>
                          <div className="transaction-description">
                            <strong>{item.title}</strong>
                            <span>{new Date(item.date).toLocaleDateString("en-IN")}</span>
                          </div>
                          <strong className={item.type === "income" ? "income-value" : "expense-value"}>
                            {item.type === "income" ? "+" : "-"}{money(item.amount)}
                          </strong>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="panel breakdown-panel">
                  <div className="panel-title-row">
                    <div>
                      <h2>Breakdown of Expenses</h2>
                      <p>{selectedMonth} spending by category</p>
                    </div>
                  </div>

                  {pieData.length === 0 ? (
                    <div className="empty-state">
                      No expenses recorded for this period.
                    </div>
                  ) : (
                    <div className="donut-layout">
                      <div className="donut-chart">
                        <ResponsiveContainer width="100%" height="100%">
                          <PieChart>
                            <Pie
                              data={pieData}
                              dataKey="value"
                              nameKey="name"
                              innerRadius={57}
                              outerRadius={83}
                              paddingAngle={2}
                              stroke="none"
                            >
                              {pieData.map((item, index) => (
                                <Cell key={item.name} fill={COLORS[index % COLORS.length]} />
                              ))}
                            </Pie>
                            <Tooltip formatter={value => money(value)} />
                          </PieChart>
                        </ResponsiveContainer>
                        <div className="donut-center">
                          <span>Total</span>
                          <strong>{money(breakdown?.total_expenses)}</strong>
                        </div>
                      </div>

                      <div className="category-legend">
                        {pieData.map((item, index) => (
                          <div className="category-row" key={item.name}>
                            <i style={{ background: COLORS[index % COLORS.length] }} />
                            <span>{item.name}</span>
                            <strong>{money(item.value)}</strong>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </section>

              <section className="panel transaction-entry" id="transactions">
                <div className="panel-title-row">
                  <div>
                    <h2>Add Income or Expense</h2>
                    <p>Save a transaction to update your dashboard.</p>
                  </div>
                  <Receipt size={21} />
                </div>
                <TransactionForms onSaved={loadDashboard} />
              </section>

              <section className="panel advisor-panel">
                <div className="advisor-title">
                  <div className="advisor-icon"><Bot size={21} /></div>
                  <div>
                    <h2>MoneyMind AI Advisor</h2>
                    <p>Ask questions about your financial activity.</p>
                  </div>
                </div>
                <form className="advisor-form" onSubmit={askAI}>
                  <input
                    value={question}
                    onChange={e => setQuestion(e.target.value)}
                    placeholder="How can I save ₹5,000 next month?"
                  />
                  <button className="purple-button" disabled={asking || !question.trim()}>
                    {asking ? "Thinking..." : "Ask AI"}
                  </button>
                </form>
                {answer && <div className="ai-answer">{answer}</div>}
              </section>

              <footer className="dashboard-footer">
                MoneyMind AI · Your personal finance companion.
                Cash flow is an estimate, not a verified bank balance.
              </footer>
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default function App() {
  const [authenticated, setAuthenticated] = useState(
    Boolean(localStorage.getItem("moneymind_token"))
  );

  function logout() {
    localStorage.removeItem("moneymind_token");
    setAuthenticated(false);
  }

  return authenticated
    ? <Dashboard onLogout={logout} />
    : <AuthScreen onLogin={() => setAuthenticated(true)} />;
}
