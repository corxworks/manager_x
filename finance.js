"use client";

import { useEffect, useState } from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:5000";

export default function Finance() {
  const [payments, setPayments] = useState([]);

  const [summary, setSummary] = useState({
    total_revenue: 0,
    pending_amount: 0,
  });

  const [filter, setFilter] = useState("all");

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  // =====================================================
  // LOAD FINANCE
  // =====================================================

  async function loadFinance() {
    try {
      setLoading(true);
      setError("");

      const url =
        filter === "all"
          ? `${API_URL}/api/finance`
          : `${API_URL}/api/finance?status=${filter}`;

      const response = await fetch(url, {
        method: "GET",
        credentials: "include",
      });

      if (response.status === 401) {
        window.location.href = "/";
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || "Could not load finance"
        );
      }

      setPayments(data.payments || []);

      setSummary({
        total_revenue:
          data.summary?.total_revenue || 0,

        pending_amount:
          data.summary?.pending_amount || 0,
      });
    } catch (err) {
      console.error("Finance error:", err);

      setError(
        err.message ||
          "Manager X could not load your payments."
      );
    } finally {
      setLoading(false);
    }
  }

  // =====================================================
  // LOAD ON START / FILTER CHANGE
  // =====================================================

  useEffect(() => {
    loadFinance();
  }, [filter]);

  // =====================================================
  // FORMAT MONEY
  // =====================================================

  function formatMoney(amount, currency = "USD") {
    const value = Number(amount || 0);

    try {
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: currency || "USD",
        maximumFractionDigits: 0,
      }).format(value);
    } catch {
      return `${currency || ""} ${value}`;
    }
  }

  // =====================================================
  // FORMAT DATE
  // =====================================================

  function formatDate(value) {
    if (!value) {
      return "Not set";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return "Not set";
    }

    return date.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  }

  // =====================================================
  // COUNTS
  // =====================================================

  const pendingCount = payments.filter(
    (payment) => payment.status === "pending"
  ).length;

  const overdueCount = payments.filter(
    (payment) => payment.status === "overdue"
  ).length;

  const paidCount = payments.filter(
    (payment) => payment.status === "paid"
  ).length;

  // =====================================================
  // PAGE
  // =====================================================

  return (
    <main className="manager-app">
      <div className="manager-container py-8 md:py-10">

        {/* HEADER */}

        <header
          className="
            flex
            flex-col
            md:flex-row
            md:items-end
            md:justify-between
            gap-5
          "
        >
          <div>
            <a
              href="/dashboard"
              className="
                text-sm
                manager-muted
                hover:text-neutral-950
              "
            >
              ← Dashboard
            </a>

            <h1
              className="
                text-4xl
                font-semibold
                tracking-tight
                mt-4
              "
            >
              Finance
            </h1>

            <p
              className="
                manager-muted
                mt-2
              "
            >
              Know what&apos;s paid,
              what&apos;s pending and
              what needs a follow-up.
            </p>
          </div>

          <button
            onClick={loadFinance}
            className="manager-button-secondary"
          >
            Refresh payments
          </button>
        </header>

        {/* SUMMARY */}

        <section
          className="
            grid
            md:grid-cols-2
            gap-4
            mt-8
          "
        >
          <div className="manager-card p-6 md:p-7">
            <p className="manager-label">
              Revenue received
            </p>

            <p
              className="
                text-4xl
                md:text-5xl
                font-semibold
                tracking-tight
                mt-4
              "
            >
              {formatMoney(
                summary.total_revenue
              )}
            </p>

            <p
              className="
                text-sm
                manager-muted
                mt-3
              "
            >
              Payments marked as paid.
            </p>
          </div>

          <div className="manager-card p-6 md:p-7">
            <p className="manager-label">
              Waiting to be paid
            </p>

            <p
              className="
                text-4xl
                md:text-5xl
                font-semibold
                tracking-tight
                mt-4
              "
            >
              {formatMoney(
                summary.pending_amount
              )}
            </p>

            <p
              className="
                text-sm
                manager-muted
                mt-3
              "
            >
              {overdueCount > 0
                ? `${overdueCount} overdue payment${
                    overdueCount === 1
                      ? ""
                      : "s"
                  } need attention.`
                : "No overdue payments."}
            </p>
          </div>
        </section>

        {/* COUNTS */}

        <section
          className="
            grid
            sm:grid-cols-3
            gap-4
            mt-4
          "
        >
          <SmallSummary
            value={pendingCount}
            label="Pending"
          />

          <SmallSummary
            value={overdueCount}
            label="Overdue"
          />

          <SmallSummary
            value={paidCount}
            label="Paid"
          />
        </section>

        {/* FILTERS */}

        <section
          className="
            mt-6
            flex
            flex-wrap
            gap-2
          "
        >
          <FilterButton
            active={filter === "all"}
            onClick={() => setFilter("all")}
          >
            All
          </FilterButton>

          <FilterButton
            active={filter === "pending"}
            onClick={() => setFilter("pending")}
          >
            Pending
          </FilterButton>

          <FilterButton
            active={filter === "overdue"}
            onClick={() => setFilter("overdue")}
          >
            Overdue
          </FilterButton>

          <FilterButton
            active={filter === "paid"}
            onClick={() => setFilter("paid")}
          >
            Paid
          </FilterButton>
        </section>

        {/* ERROR */}

        {error && (
          <div className="manager-card p-5 mt-5">
            <p className="text-sm text-red-600">
              {error}
            </p>
          </div>
        )}

        {/* PAYMENTS */}

        <section
          className="
            manager-card
            mt-5
            overflow-hidden
          "
        >
          <div
            className="
              px-6
              py-5
              border-b
              border-neutral-100
              flex
              items-center
              justify-between
              gap-4
            "
          >
            <div>
              <p className="manager-label">
                Payments
              </p>

              <p
                className="
                  text-sm
                  manager-muted
                  mt-1
                  capitalize
                "
              >
                {filter === "all"
                  ? "All payments"
                  : `${filter} payments`}
              </p>
            </div>

            <span className="text-sm manager-muted">
              {payments.length}
            </span>
          </div>

          {loading ? (
            <div className="manager-empty">
              <div className="manager-loading" />

              <p className="text-sm mt-4">
                Checking payments...
              </p>
            </div>
          ) : payments.length === 0 ? (
            <div className="manager-empty">
              <p
                className="
                  font-medium
                  text-neutral-950
                "
              >
                {filter === "all"
                  ? "No payments detected yet."
                  : `No ${filter} payments.`}
              </p>

              <p
                className="
                  text-sm
                  mt-2
                  max-w-md
                "
              >
                Manager X will track
                payment information
                connected to your
                creator deals.
              </p>
            </div>
          ) : (
            <div>
              {payments.map(
                (payment, index) => (
                  <div key={payment.id}>
                    <PaymentRow
                      payment={payment}
                      formatMoney={formatMoney}
                      formatDate={formatDate}
                    />

                    {index <
                      payments.length - 1 && (
                      <div className="manager-divider" />
                    )}
                  </div>
                )
              )}
            </div>
          )}
        </section>

        {/* FOOTER MESSAGE */}

        <section className="manager-card p-6 mt-5">
          <div className="flex items-start gap-4">
            <div className="manager-status-dot mt-1.5" />

            <div>
              <p className="font-medium">
                Don&apos;t lose track of
                creator revenue.
              </p>

              <p
                className="
                  text-sm
                  manager-muted
                  mt-2
                  leading-relaxed
                  max-w-2xl
                "
              >
                Manager X keeps pending
                and overdue payments
                visible so a finished
                brand deal doesn&apos;t
                turn into forgotten money.
              </p>
            </div>
          </div>
        </section>

      </div>
    </main>
  );
}


// =========================================================
// PAYMENT ROW
// =========================================================

function PaymentRow({
  payment,
  formatMoney,
  formatDate,
}) {
  return (
    <div
      className="
        px-5
        md:px-6
        py-5
        flex
        flex-col
        md:flex-row
        md:items-center
        md:justify-between
        gap-6
      "
    >
      <div>
        <div
          className="
            flex
            flex-wrap
            items-center
            gap-3
          "
        >
          <p
            className="
              font-medium
              text-lg
            "
          >
            {formatMoney(
              payment.amount,
              payment.currency
            )}
          </p>

          <StatusBadge
            status={payment.status}
          />
        </div>

        <div
          className="
            flex
            flex-wrap
            gap-x-4
            gap-y-2
            mt-3
            text-sm
            manager-muted
          "
        >
          {payment.invoice_number && (
            <span>
              Invoice {payment.invoice_number}
            </span>
          )}

          {payment.deal_id && (
            <span>
              Deal #{payment.deal_id}
            </span>
          )}
        </div>
      </div>

      <div className="md:text-right">
        {payment.status === "paid" ? (
          <>
            <p className="text-sm font-medium">
              Paid
            </p>

            <p
              className="
                text-sm
                manager-muted
                mt-1
              "
            >
              {formatDate(
                payment.paid_at
              )}
            </p>
          </>
        ) : (
          <>
            <p className="text-sm font-medium">
              {payment.status === "overdue"
                ? "Was due"
                : "Due"}
            </p>

            <p
              className="
                text-sm
                manager-muted
                mt-1
              "
            >
              {formatDate(
                payment.due_date
              )}
            </p>
          </>
        )}
      </div>
    </div>
  );
}


// =========================================================
// STATUS BADGE
// =========================================================

function StatusBadge({
  status,
}) {
  let classes =
    "bg-neutral-100 text-neutral-600";

  if (status === "overdue") {
    classes =
      "bg-neutral-950 text-white";
  }

  if (status === "paid") {
    classes =
      "bg-neutral-100 text-neutral-500";
  }

  return (
    <span
      className={`
        inline-flex
        items-center
        px-2.5
        py-1
        rounded-full
        text-xs
        font-medium
        capitalize
        ${classes}
      `}
    >
      {status || "pending"}
    </span>
  );
}


// =========================================================
// SMALL SUMMARY
// =========================================================

function SmallSummary({
  value,
  label,
}) {
  return (
    <div className="manager-card p-5">
      <p className="text-2xl font-semibold">
        {value}
      </p>

      <p
        className="
          text-sm
          manager-muted
          mt-1
        "
      >
        {label}
      </p>
    </div>
  );
}


// =========================================================
// FILTER BUTTON
// =========================================================

function FilterButton({
  active,
  onClick,
  children,
}) {
  return (
    <button
      onClick={onClick}
      className={`
        px-4
        py-2
        rounded-xl
        text-sm
        font-medium
        border
        transition
        ${
          active
            ? "bg-neutral-950 text-white border-neutral-950"
            : "bg-white text-neutral-600 border-neutral-200 hover:bg-neutral-50"
        }
      `}
    >
      {children}
    </button>
  );
}