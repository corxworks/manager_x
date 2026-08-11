"use client";

import { useEffect, useState } from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:5000";

export default function Calendar() {
  const [meetings, setMeetings] = useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  // IMPORTANT:
  // Prevent server/client date mismatch.
  const [today, setToday] =
    useState(null);


  // =====================================================
  // SET CLIENT DATE
  // =====================================================

  useEffect(() => {

    setToday(new Date());

  }, []);


  // =====================================================
  // LOAD CALENDAR
  // =====================================================

  async function loadCalendar() {

    try {

      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_URL}/api/calendar`,
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
          "Could not load calendar"
        );

      }


      const data =
        await response.json();


      setMeetings(
        data.meetings || []
      );


    } catch (err) {

      console.error(err);

      setError(
        "Manager X could not load your calendar."
      );

    } finally {

      setLoading(false);

    }

  }


  // =====================================================
  // LOAD ON PAGE OPEN
  // =====================================================

  useEffect(() => {

    loadCalendar();

  }, []);


  // =====================================================
  // DATE HELPERS
  // =====================================================

  function formatTime(value) {

    if (!value) {
      return "";
    }


    const date =
      new Date(value);


    if (
      Number.isNaN(
        date.getTime()
      )
    ) {
      return "";
    }


    return date.toLocaleTimeString(
      undefined,
      {
        hour: "numeric",
        minute: "2-digit"
      }
    );

  }


  function formatFullDate(value) {

    if (!value) {
      return "";
    }


    const date =
      value instanceof Date
        ? value
        : new Date(value);


    if (
      Number.isNaN(
        date.getTime()
      )
    ) {
      return "";
    }


    return date.toLocaleDateString(
      undefined,
      {
        weekday: "long",
        month: "long",
        day: "numeric"
      }
    );

  }


  function formatDate(value) {

    if (!value) {
      return "";
    }


    const date =
      new Date(value);


    if (
      Number.isNaN(
        date.getTime()
      )
    ) {
      return "";
    }


    return date.toLocaleDateString(
      undefined,
      {
        month: "short",
        day: "numeric"
      }
    );

  }


  function isToday(value) {

    if (!value) {
      return false;
    }


    const date =
      new Date(value);


    const now =
      new Date();


    return (
      date.getFullYear()
      ===
      now.getFullYear()

      &&

      date.getMonth()
      ===
      now.getMonth()

      &&

      date.getDate()
      ===
      now.getDate()
    );

  }


  // =====================================================
  // SORT MEETINGS
  // =====================================================

  const sortedMeetings =
    [...meetings].sort(
      (a, b) => {

        const aTime =
          new Date(
            a.start_time
          ).getTime();

        const bTime =
          new Date(
            b.start_time
          ).getTime();

        return aTime - bTime;

      }
    );


  // =====================================================
  // TODAY'S MEETINGS
  // =====================================================

  const todayMeetings =
    sortedMeetings.filter(
      (meeting) =>
        isToday(
          meeting.start_time
        )
    );


  // =====================================================
  // UPCOMING MEETINGS
  // =====================================================

  const upcomingMeetings =
    sortedMeetings.filter(
      (meeting) =>
        !isToday(
          meeting.start_time
        )
    );


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
              Calendar
            </h1>


            <p className="manager-muted mt-2">
              Meetings your manager thinks matter.
            </p>

          </div>


          <button
            onClick={loadCalendar}
            className="manager-button-secondary"
          >
            Refresh calendar
          </button>

        </header>


        {/* =================================================
            TODAY
        ================================================= */}

        <section className="mt-10">

          <div className="flex items-end justify-between">

            <div>

              <p className="manager-label">
                Today
              </p>


              <h2 className="text-2xl font-semibold tracking-tight mt-2">

                {today
                  ? formatFullDate(today)
                  : "\u00A0"
                }

              </h2>

            </div>


            <span className="text-sm manager-muted">

              {todayMeetings.length}{" "}
              {todayMeetings.length === 1
                ? "meeting"
                : "meetings"
              }

            </span>

          </div>


          <div className="manager-card mt-5 overflow-hidden">

            {loading ? (

              <div className="manager-empty">

                <div className="manager-loading" />

                <p className="text-sm mt-4">
                  Loading your calendar...
                </p>

              </div>

            ) : error ? (

              <div className="manager-empty">

                <p className="font-medium text-neutral-950">
                  Calendar unavailable
                </p>

                <p className="text-sm manager-muted mt-2">
                  {error}
                </p>

              </div>

            ) : todayMeetings.length === 0 ? (

              <div className="manager-empty">

                <p className="font-medium text-neutral-950">
                  No meetings today.
                </p>

                <p className="text-sm manager-muted mt-2">
                  Your calendar is clear.
                </p>

              </div>

            ) : (

              <div>

                {todayMeetings.map(
                  (meeting, index) => (

                    <div
                      key={
                        meeting.id ||
                        meeting.google_event_id ||
                        index
                      }
                    >

                      <MeetingRow
                        meeting={meeting}
                        formatTime={formatTime}
                        formatDate={formatDate}
                      />


                      {index <
                        todayMeetings.length - 1
                        && (

                          <div className="manager-divider" />

                        )}

                    </div>

                  )
                )}

              </div>

            )}

          </div>

        </section>


        {/* =================================================
            UPCOMING
        ================================================= */}

        <section className="mt-10">

          <div className="flex items-end justify-between">

            <div>

              <p className="manager-label">
                Upcoming
              </p>


              <h2 className="text-2xl font-semibold tracking-tight mt-2">
                What's coming next.
              </h2>

            </div>


            <span className="text-sm manager-muted">

              {upcomingMeetings.length}{" "}
              {upcomingMeetings.length === 1
                ? "meeting"
                : "meetings"
              }

            </span>

          </div>


          <div className="manager-card mt-5 overflow-hidden">

            {loading ? (

              <div className="manager-empty">

                <div className="manager-loading" />

                <p className="text-sm mt-4">
                  Loading upcoming meetings...
                </p>

              </div>

            ) : upcomingMeetings.length === 0 ? (

              <div className="manager-empty">

                <p className="font-medium text-neutral-950">
                  Nothing coming up.
                </p>

                <p className="text-sm manager-muted mt-2">
                  No upcoming meetings need your attention.
                </p>

              </div>

            ) : (

              <div>

                {upcomingMeetings.map(
                  (meeting, index) => (

                    <div
                      key={
                        meeting.id ||
                        meeting.google_event_id ||
                        index
                      }
                    >

                      <MeetingRow
                        meeting={meeting}
                        formatTime={formatTime}
                        formatDate={formatDate}
                      />


                      {index <
                        upcomingMeetings.length - 1
                        && (

                          <div className="manager-divider" />

                        )}

                    </div>

                  )
                )}

              </div>

            )}

          </div>

        </section>


        {/* =================================================
            MANAGER MESSAGE
        ================================================= */}

        <section className="manager-card p-6 mt-5">

          <div className="flex items-start gap-4">

            <div className="manager-status-dot mt-1.5" />

            <div>

              <p className="font-medium">
                Your calendar is handled.
              </p>

              <p className="text-sm manager-muted mt-2 leading-relaxed max-w-2xl">
                Manager X keeps your important meetings
                visible so you don't have to constantly
                check your calendar.
              </p>

            </div>

          </div>

        </section>

      </div>

    </main>

  );

}


// =========================================================
// MEETING ROW
// =========================================================

function MeetingRow({
  meeting,
  formatTime,
  formatDate
}) {

  return (

    <div className="px-5 md:px-6 py-5 flex flex-col md:flex-row md:items-center justify-between gap-5">


      {/* LEFT */}

      <div className="flex items-start gap-4 min-w-0">

        <div className="w-11 h-11 rounded-xl bg-neutral-100 flex items-center justify-center flex-shrink-0">

          <CalendarIcon />

        </div>


        <div className="min-w-0">

          <p className="font-medium truncate">

            {meeting.title ||
              "Untitled meeting"}

          </p>


          <div className="flex flex-wrap gap-x-3 gap-y-1 mt-2 text-xs manager-muted">

            <span>

              {formatDate(
                meeting.start_time
              )}

            </span>


            <span>
              •
            </span>


            <span>

              {formatTime(
                meeting.start_time
              )}

              {meeting.end_time
                ? ` – ${formatTime(
                    meeting.end_time
                  )}`
                : ""
              }

            </span>

          </div>


          {meeting.description && (

            <p className="text-sm manager-muted mt-2 max-w-xl">

              {meeting.description}

            </p>

          )}

        </div>

      </div>


      {/* RIGHT */}

      {meeting.meeting_link ? (

        <a
          href={
            meeting.meeting_link
          }
          target="_blank"
          rel="noreferrer"
          className="manager-button-secondary whitespace-nowrap"
        >
          Join meeting
        </a>

      ) : (

        <span className="text-sm manager-subtle">
          No meeting link
        </span>

      )}

    </div>

  );

}


// =========================================================
// CALENDAR ICON
// =========================================================

function CalendarIcon() {

  return (

    <svg
      width="19"
      height="19"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >

      <rect
        x="3"
        y="4"
        width="18"
        height="17"
        rx="2"
      />

      <line
        x1="16"
        y1="2"
        x2="16"
        y2="6"
      />

      <line
        x1="8"
        y1="2"
        x2="8"
        y2="6"
      />

      <line
        x1="3"
        y1="10"
        x2="21"
        y2="10"
      />

    </svg>

  );

}