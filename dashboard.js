"use client";

import { useEffect, useState } from "react";


const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:5000";


export default function Dashboard() {

  const [dashboard, setDashboard] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [syncing, setSyncing] =
    useState(false);

  const [error, setError] =
    useState("");


  // =====================================================
  // LOAD DASHBOARD
  // =====================================================

  async function loadDashboard() {

    try {

      setError("");

      const response = await fetch(
        `${API_URL}/api/dashboard`,
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
          "Could not load dashboard"
        );

      }

      const data =
        await response.json();

      setDashboard(data);

    } catch (err) {

      console.error(err);

      setError(
        "Manager X could not load your work."
      );

    } finally {

      setLoading(false);

    }

  }


  // =====================================================
  // FIRST LOAD
  // =====================================================

  useEffect(() => {

    loadDashboard();

  }, []);


  // =====================================================
  // RUN MANAGER SYNC
  // =====================================================

  async function runManager() {

    if (syncing) {
      return;
    }

    try {

      setSyncing(true);
      setError("");

      const response = await fetch(
        `${API_URL}/api/sync`,
        {
          method: "POST",
          credentials: "include"
        }
      );

      if (response.status === 401) {

        window.location.href = "/";
        return;

      }

      if (!response.ok) {

        throw new Error(
          "Manager sync failed"
        );

      }

      /*
        The backend starts a Celery job.

        We wait a little before refreshing
        the dashboard so the background
        manager has time to process data.
      */

      await new Promise(
        (resolve) =>
          setTimeout(resolve, 2500)
      );

      await loadDashboard();

    } catch (err) {

      console.error(err);

      setError(
        "Manager X could not sync right now."
      );

    } finally {

      setSyncing(false);

    }

  }


  // =====================================================
  // FORMAT MONEY
  // =====================================================

  function formatMoney(amount) {

    const value =
      Number(amount || 0);

    return new Intl.NumberFormat(
      "en-US",
      {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 0
      }
    ).format(value);

  }


  // =====================================================
  // FORMAT MEETING TIME
  // =====================================================

  function formatMeetingTime(value) {

    if (!value) {
      return "Time unavailable";
    }

    const date =
      new Date(value);

    if (
      Number.isNaN(
        date.getTime()
      )
    ) {
      return "Time unavailable";
    }

    return date.toLocaleString(
      undefined,
      {
        weekday: "short",
        hour: "numeric",
        minute: "2-digit"
      }
    );

  }


  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {

    return (

      <main className="manager-app">

        <div className="min-h-screen flex items-center justify-center">

          <div className="flex items-center gap-3">

            <div className="manager-loading" />

            <p className="text-sm manager-muted">
              Preparing your day...
            </p>

          </div>

        </div>

      </main>

    );

  }


  // =====================================================
  // DATA
  // =====================================================

  const today =
    dashboard?.today || {};

  const meetings =
    dashboard?.upcoming_meetings || [];

  const urgentEmails =
    today.urgent_emails || 0;

  const activeDeals =
    today.active_deals || 0;

  const pendingTasks =
    today.pending_tasks || 0;

  const followUps =
    today.follow_ups || 0;

  const pendingPayment =
    today.pending_payment_amount || 0;


  // =====================================================
  // PAGE
  // =====================================================

  return (

    <main className="manager-app">

      <div className="manager-container py-8 md:py-10">


        {/* =================================================
            TOP BAR
        ================================================= */}

        <header className="flex items-center justify-between gap-4">

          <div className="flex items-center gap-3">

            <div className="w-10 h-10 bg-neutral-950 text-white rounded-xl flex items-center justify-center font-semibold">

              C

            </div>

            <div>

              <p className="font-semibold leading-none">
                CORX
              </p>

              <p className="text-xs manager-muted mt-1">
                Manager X
              </p>

            </div>

          </div>


          <button
            onClick={runManager}
            disabled={syncing}
            className="manager-button-secondary"
          >

            {syncing
              ? "Manager working..."
              : "Refresh manager"
            }

          </button>

        </header>


        {/* =================================================
            ERROR
        ================================================= */}

        {error && (

          <div className="mt-6 manager-card px-5 py-4">

            <p className="text-sm">
              {error}
            </p>

          </div>

        )}


        {/* =================================================
            GREETING
        ================================================= */}

        <section className="mt-12 md:mt-16">

          <p className="text-sm manager-muted">
            Good morning
          </p>

          <h1 className="mt-2 text-4xl md:text-5xl font-semibold tracking-tight max-w-3xl">

            Here&apos;s what needs
            your attention today.

          </h1>

          <p className="mt-4 text-base manager-muted max-w-xl leading-relaxed">

            Your manager has organized
            the important work. Everything
            else can wait.

          </p>

        </section>


        {/* =================================================
            MAIN GRID
        ================================================= */}

        <section className="grid lg:grid-cols-[1fr_340px] gap-5 mt-10">


          {/* ===============================================
              TODAY'S PRIORITY
          =============================================== */}

          <div className="manager-card p-6 md:p-8">

            <div className="flex items-center justify-between">

              <p className="manager-label">
                Today&apos;s priority
              </p>

              <span className="text-xs manager-muted">
                Manager prepared
              </span>

            </div>


            <div className="mt-7">


              {/* URGENT EMAILS */}

              <PriorityRow
                title={
                  urgentEmails === 1
                    ? "1 urgent email needs a reply"
                    : `${urgentEmails} urgent emails need replies`
                }
                description="Important conversations waiting for you."
                value={urgentEmails}
                href="/inbox"
              />


              <div className="manager-divider" />


              {/* TASKS */}

              <PriorityRow
                title={
                  pendingTasks === 1
                    ? "1 task needs to be completed"
                    : `${pendingTasks} tasks need to be completed`
                }
                description="Work your manager has prepared."
                value={pendingTasks}
                href="/tasks"
              />


              <div className="manager-divider" />


              {/* FOLLOW UPS */}

              <PriorityRow
                title={
                  followUps === 1
                    ? "1 follow-up is due"
                    : `${followUps} follow-ups are due`
                }
                description="Keep brand conversations moving."
                value={followUps}
                href="/deals"
              />


              <div className="manager-divider" />


              {/* PAYMENT */}

              <PriorityRow
                title={
                  pendingPayment > 0
                    ? `${formatMoney(
                        pendingPayment
                      )} waiting to be paid`
                    : "No payments need attention"
                }
                description={
                  pendingPayment > 0
                    ? "Pending creator revenue."
                    : "Your payments are up to date."
                }
                value={pendingPayment}
                href="/finance"
              />

            </div>

          </div>


          {/* ===============================================
              MANAGER SUMMARY
          =============================================== */}

          <aside className="manager-card p-6">

            <p className="manager-label">
              Manager summary
            </p>


            <div className="mt-7 space-y-7">

              <SummaryItem
                number={activeDeals}
                label="Active brand deals"
              />

              <div className="manager-divider" />

              <SummaryItem
                number={urgentEmails}
                label="Urgent emails"
              />

              <div className="manager-divider" />

              <SummaryItem
                number={followUps}
                label="Follow-ups due"
              />

              <div className="manager-divider" />

              <SummaryItem
                number={
                  formatMoney(
                    pendingPayment
                  )
                }
                label="Pending payments"
              />

            </div>

          </aside>

        </section>


        {/* =================================================
            UPCOMING MEETINGS
        ================================================= */}

        <section className="manager-card mt-5 p-6 md:p-8">

          <div className="flex items-center justify-between">

            <div>

              <p className="manager-label">
                Upcoming
              </p>

              <h2 className="text-xl font-semibold mt-2">
                Meetings
              </h2>

            </div>

            <a
              href="/calendar"
              className="text-sm manager-muted hover:text-neutral-950 transition"
            >
              View calendar →
            </a>

          </div>


          {meetings.length === 0 ? (

            <div className="manager-empty">

              <p className="font-medium text-neutral-950">
                Your calendar is clear.
              </p>

              <p className="text-sm mt-2">
                No upcoming meetings need
                your attention.
              </p>

            </div>

          ) : (

            <div className="mt-6">

              {meetings.map(
                (meeting, index) => (

                  <div
                    key={meeting.id}
                  >

                    <div className="py-5 flex flex-col md:flex-row md:items-center justify-between gap-4">

                      <div>

                        <p className="font-medium">
                          {meeting.title}
                        </p>

                        <p className="text-sm manager-muted mt-1">
                          {formatMeetingTime(
                            meeting.start_time
                          )}
                        </p>

                      </div>


                      {meeting.meeting_link && (

                        <a
                          href={
                            meeting.meeting_link
                          }
                          target="_blank"
                          rel="noreferrer"
                          className="manager-button-secondary"
                        >
                          Join meeting
                        </a>

                      )}

                    </div>


                    {index <
                      meetings.length - 1 && (

                      <div className="manager-divider" />

                    )}

                  </div>

                )
              )}

            </div>

          )}

        </section>


        {/* =================================================
            EVERYTHING ELSE
        ================================================= */}

        <section className="mt-5 manager-card p-6 md:p-8">

          <div className="flex items-start gap-4">

            <div className="mt-1 manager-status-dot" />

            <div>

              <h2 className="font-semibold text-lg">
                Everything else can wait.
              </h2>

              <p className="text-sm manager-muted mt-2 leading-relaxed max-w-2xl">

                Manager X is checking your
                inbox, calendar, files,
                payments and follow-ups in
                the background.

              </p>

            </div>

          </div>

        </section>


        {/* =================================================
            NAVIGATION
        ================================================= */}

        <nav className="mt-10 flex flex-wrap gap-x-6 gap-y-3 text-sm manager-muted">

          <a
            href="/inbox"
            className="hover:text-neutral-950"
          >
            Inbox
          </a>

          <a
            href="/deals"
            className="hover:text-neutral-950"
          >
            Brand CRM
          </a>

          <a
            href="/tasks"
            className="hover:text-neutral-950"
          >
            Tasks
          </a>

          <a
            href="/calendar"
            className="hover:text-neutral-950"
          >
            Calendar
          </a>

          <a
            href="/drive"
            className="hover:text-neutral-950"
          >
            Drive
          </a>

          <a
            href="/finance"
            className="hover:text-neutral-950"
          >
            Finance
          </a>

        </nav>

      </div>

    </main>

  );

}


// =========================================================
// PRIORITY ROW
// =========================================================

function PriorityRow({
  title,
  description,
  value,
  href
}) {

  const active =
    Number(value) > 0;

  return (

    <a
      href={href}
      className="group py-6 flex items-center justify-between gap-6"
    >

      <div>

        <div className="flex items-center gap-2">

          {active && (
            <span className="manager-status-dot" />
          )}

          <p className="font-medium">
            {title}
          </p>

        </div>

        <p className="text-sm manager-muted mt-1.5">
          {description}
        </p>

      </div>


      <span className="text-neutral-300 group-hover:text-neutral-950 transition text-lg">

        →

      </span>

    </a>

  );

}


// =========================================================
// SUMMARY ITEM
// =========================================================

function SummaryItem({
  number,
  label
}) {

  return (

    <div>

      <p className="text-3xl font-semibold tracking-tight">
        {number}
      </p>

      <p className="text-sm manager-muted mt-1">
        {label}
      </p>

    </div>

  );

}