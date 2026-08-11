"use client";

import { useEffect, useState } from "react";


const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:5000";


export default function CRM() {

  const [deals, setDeals] = useState([]);
  const [selectedDeal, setSelectedDeal] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  // =====================================================
  // LOAD DEALS
  // =====================================================

  async function loadDeals() {

    try {

      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_URL}/api/deals`,
        {
          method: "GET",
          credentials: "include"
        }
      );

      if (response.status === 401) {

        window.location.href = "/";
        return;

      }

      if (!response.ok) {

        throw new Error(
          "Could not load deals"
        );

      }

      const data =
        await response.json();

      const list =
        data.deals || [];

      setDeals(list);

      setSelectedDeal(
        (current) => {

          if (list.length === 0) {
            return null;
          }

          if (!current) {
            return list[0];
          }

          const updated =
            list.find(
              (deal) =>
                deal.id === current.id
            );

          return updated || list[0];

        }
      );

    } catch (err) {

      console.error(err);

      setError(
        "Manager X could not load your brand deals."
      );

    } finally {

      setLoading(false);

    }

  }


  // =====================================================
  // FIRST LOAD
  // =====================================================

  useEffect(() => {

    loadDeals();

  }, []);


  // =====================================================
  // FORMAT MONEY
  // =====================================================

  function formatMoney(
    amount,
    currency = "USD"
  ) {

    if (
      amount === null ||
      amount === undefined
    ) {
      return "Value not set";
    }

    try {

      return new Intl.NumberFormat(
        "en-US",
        {
          style: "currency",
          currency:
            currency || "USD",
          maximumFractionDigits: 0
        }
      ).format(
        Number(amount)
      );

    } catch {

      return `${currency || ""} ${amount}`;

    }

  }


  // =====================================================
  // FORMAT DATE
  // =====================================================

  function formatDate(value) {

    if (!value) {
      return "Not scheduled";
    }

    const date =
      new Date(value);

    if (
      Number.isNaN(
        date.getTime()
      )
    ) {
      return "Not scheduled";
    }

    return date.toLocaleDateString(
      undefined,
      {
        month: "short",
        day: "numeric",
        year: "numeric"
      }
    );

  }


  // =====================================================
  // FORMAT STATUS
  // =====================================================

  function formatStatus(value) {

    if (!value) {
      return "New";
    }

    return value
      .replaceAll("_", " ")
      .replace(
        /\b\w/g,
        (letter) =>
          letter.toUpperCase()
      );

  }


  // =====================================================
  // SUMMARY
  // =====================================================

  const activeDeals =
    deals.filter(
      (deal) =>
        ![
          "paid",
          "lost",
          "completed"
        ].includes(
          deal.status
        )
    );

  const pipelineValue =
    activeDeals.reduce(
      (total, deal) =>
        total +
        Number(
          deal.deal_value || 0
        ),
      0
    );

  const followUps =
    deals.filter(
      (deal) =>
        deal.next_follow_up
    ).length;


  // =====================================================
  // PAGE
  // =====================================================

  return (

    <main className="manager-app">

      <div className="manager-container py-8 md:py-10">


        {/* =================================================
            HEADER
        ================================================= */}

        <header className="flex flex-col md:flex-row md:items-end justify-between gap-5">

          <div>

            <a
              href="/dashboard"
              className="text-sm manager-muted hover:text-neutral-950"
            >
              ← Dashboard
            </a>

            <h1 className="text-4xl font-semibold tracking-tight mt-4">
              Brand CRM
            </h1>

            <p className="manager-muted mt-2">
              Every brand conversation,
              deal and follow-up in one place.
            </p>

          </div>


          <button
            onClick={loadDeals}
            className="manager-button-secondary"
          >
            Refresh deals
          </button>

        </header>


        {/* =================================================
            SUMMARY
        ================================================= */}

        <section className="grid sm:grid-cols-3 gap-4 mt-8">

          <SummaryCard
            value={activeDeals.length}
            label="Active deals"
          />

          <SummaryCard
            value={
              formatMoney(
                pipelineValue
              )
            }
            label="Active deal value"
          />

          <SummaryCard
            value={followUps}
            label="Follow-ups scheduled"
          />

        </section>


        {/* =================================================
            ERROR
        ================================================= */}

        {error && (

          <div className="manager-card p-5 mt-5">

            <p className="text-sm">
              {error}
            </p>

          </div>

        )}


        {/* =================================================
            CRM
        ================================================= */}

        <section className="manager-card mt-5 overflow-hidden">

          {loading ? (

            <div className="manager-empty">

              <div className="manager-loading" />

              <p className="text-sm mt-4">
                Organizing brand deals...
              </p>

            </div>

          ) : deals.length === 0 ? (

            <div className="manager-empty">

              <p className="font-medium text-neutral-950">
                No brand deals yet.
              </p>

              <p className="text-sm mt-2 max-w-md">
                When Manager X detects a
                brand opportunity, it will
                appear here automatically.
              </p>

            </div>

          ) : (

            <div className="grid lg:grid-cols-[390px_1fr] min-h-[620px]">


              {/* ===========================================
                  DEAL LIST
              =========================================== */}

              <div className="border-b lg:border-b-0 lg:border-r border-neutral-200">

                <div className="px-5 py-4 border-b border-neutral-100">

                  <p className="manager-label">
                    {deals.length} deals
                  </p>

                </div>


                <div className="max-h-[620px] overflow-y-auto">

                  {deals.map(
                    (deal) => {

                      const selected =
                        selectedDeal?.id ===
                        deal.id;

                      return (

                        <button
                          key={deal.id}
                          onClick={
                            () =>
                              setSelectedDeal(
                                deal
                              )
                          }
                          className={`
                            w-full text-left
                            px-5 py-5
                            border-b border-neutral-100
                            transition
                            ${
                              selected
                                ? "bg-neutral-50"
                                : "bg-white hover:bg-neutral-50"
                            }
                          `}
                        >

                          <div className="flex items-start justify-between gap-4">

                            <div className="min-w-0">

                              <p className="font-semibold truncate">

                                {deal.company ||
                                  "Unknown brand"}

                              </p>

                              <p className="text-sm manager-muted mt-1">

                                {deal.contact_name ||
                                  deal.contact_email ||
                                  "Contact unavailable"}

                              </p>

                            </div>


                            <p className="text-sm font-medium whitespace-nowrap">

                              {formatMoney(
                                deal.deal_value,
                                deal.currency
                              )}

                            </p>

                          </div>


                          <div className="flex flex-wrap items-center gap-2 mt-4">

                            <StatusBadge>
                              {formatStatus(
                                deal.status
                              )}
                            </StatusBadge>


                            {deal.next_follow_up && (

                              <span className="text-xs manager-muted">

                                Follow up{" "}
                                {formatDate(
                                  deal.next_follow_up
                                )}

                              </span>

                            )}

                          </div>

                        </button>

                      );

                    }
                  )}

                </div>

              </div>


              {/* ===========================================
                  DEAL DETAILS
              =========================================== */}

              <div className="bg-white">

                {selectedDeal ? (

                  <div className="p-6 md:p-8">


                    {/* TOP */}

                    <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">

                      <div>

                        <StatusBadge>
                          {formatStatus(
                            selectedDeal.status
                          )}
                        </StatusBadge>

                        <h2 className="text-3xl font-semibold tracking-tight mt-4">

                          {selectedDeal.company ||
                            "Unknown brand"}

                        </h2>

                        <p className="manager-muted mt-2">

                          {selectedDeal.contact_name ||
                            "No contact name"}

                        </p>

                      </div>


                      <div className="md:text-right">

                        <p className="manager-label">
                          Deal value
                        </p>

                        <p className="text-3xl font-semibold mt-2">

                          {formatMoney(
                            selectedDeal.deal_value,
                            selectedDeal.currency
                          )}

                        </p>

                      </div>

                    </div>


                    <div className="manager-divider my-8" />


                    {/* DETAILS */}

                    <div className="grid md:grid-cols-2 gap-x-12 gap-y-8">

                      <Detail
                        label="Contact"
                        value={
                          selectedDeal.contact_name ||
                          "Not available"
                        }
                      />

                      <Detail
                        label="Email"
                        value={
                          selectedDeal.contact_email ||
                          "Not available"
                        }
                      />

                      <Detail
                        label="Status"
                        value={
                          formatStatus(
                            selectedDeal.status
                          )
                        }
                      />

                      <Detail
                        label="Next follow-up"
                        value={
                          formatDate(
                            selectedDeal.next_follow_up
                          )
                        }
                      />

                    </div>


                    {/* NOTES */}

                    <div className="manager-divider my-8" />

                    <div>

                      <p className="manager-label">
                        Notes
                      </p>

                      <p className="mt-3 text-[15px] leading-7 whitespace-pre-wrap">

                        {selectedDeal.notes ||
                          "No notes yet."}

                      </p>

                    </div>


                    {/* MANAGER */}

                    <div className="mt-8 bg-neutral-50 border border-neutral-200 rounded-2xl p-5">

                      <p className="manager-label">
                        Manager X
                      </p>

                      {selectedDeal.next_follow_up ? (

                        <>

                          <p className="font-medium mt-3">
                            Next action is already scheduled.
                          </p>

                          <p className="text-sm manager-muted mt-2">
                            Follow up on{" "}
                            {formatDate(
                              selectedDeal.next_follow_up
                            )}
                            .
                          </p>

                        </>

                      ) : (

                        <>

                          <p className="font-medium mt-3">
                            No follow-up is currently scheduled.
                          </p>

                          <p className="text-sm manager-muted mt-2">
                            Manager X will surface
                            the next action when one
                            is detected.
                          </p>

                        </>

                      )}

                    </div>

                  </div>

                ) : (

                  <div className="manager-empty h-full">
                    Select a deal.
                  </div>

                )}

              </div>

            </div>

          )}

        </section>

      </div>

    </main>

  );

}


// =========================================================
// SUMMARY CARD
// =========================================================

function SummaryCard({
  value,
  label
}) {

  return (

    <div className="manager-card p-5">

      <p className="text-2xl font-semibold tracking-tight">
        {value}
      </p>

      <p className="text-sm manager-muted mt-1">
        {label}
      </p>

    </div>

  );

}


// =========================================================
// DETAIL
// =========================================================

function Detail({
  label,
  value
}) {

  return (

    <div>

      <p className="manager-label">
        {label}
      </p>

      <p className="mt-2 font-medium break-words">
        {value}
      </p>

    </div>

  );

}


// =========================================================
// STATUS BADGE
// =========================================================

function StatusBadge({
  children
}) {

  return (

    <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-neutral-100 text-neutral-600 text-xs font-medium">

      {children}

    </span>

  );

}