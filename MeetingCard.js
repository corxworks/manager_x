"use client";


export default function MeetingCard({
  meeting
}) {

  if (!meeting) {
    return null;
  }


  // =====================================================
  // GET DATE
  // =====================================================

  function getDate(value) {

    if (!value) {
      return null;
    }


    const date =
      new Date(value);


    if (
      Number.isNaN(
        date.getTime()
      )
    ) {
      return null;
    }


    return date;

  }


  // =====================================================
  // FORMAT TIME
  // =====================================================

  function formatTime(value) {

    const date =
      getDate(value);


    if (!date) {
      return "Time unavailable";
    }


    return date.toLocaleTimeString(
      undefined,
      {
        hour: "numeric",
        minute: "2-digit"
      }
    );

  }


  // =====================================================
  // FORMAT DATE
  // =====================================================

  function formatDate(value) {

    const date =
      getDate(value);


    if (!date) {
      return "Date unavailable";
    }


    return date.toLocaleDateString(
      undefined,
      {
        weekday: "short",
        month: "short",
        day: "numeric"
      }
    );

  }


  // =====================================================
  // CHECK TODAY
  // =====================================================

  function isToday(value) {

    const date =
      getDate(value);


    if (!date) {
      return false;
    }


    const today =
      new Date();


    return (
      date.toDateString() ===
      today.toDateString()
    );

  }


  // =====================================================
  // CHECK PAST
  // =====================================================

  function isPast(value) {

    const date =
      getDate(value);


    if (!date) {
      return false;
    }


    return (
      date.getTime() <
      Date.now()
    );

  }


  // =====================================================
  // VALUES
  // =====================================================

  const today =
    isToday(
      meeting.start_time
    );


  const past =
    isPast(
      meeting.end_time ||
      meeting.start_time
    );


  // =====================================================
  // CARD
  // =====================================================

  return (

    <div className="manager-card p-5">


      {/* =================================================
          TOP
      ================================================= */}

      <div className="flex items-start justify-between gap-5">


        {/* DATE + TITLE */}

        <div className="flex items-start gap-4 min-w-0">


          {/* DATE BOX */}

          <div className="w-14 h-14 rounded-xl bg-neutral-100 flex flex-col items-center justify-center flex-shrink-0">

            <span className="text-[10px] uppercase manager-muted">

              {today
                ? "Today"
                : formatDate(
                    meeting.start_time
                  ).split(" ")[0]
              }

            </span>


            <span className="text-sm font-semibold mt-0.5">

              {formatTime(
                meeting.start_time
              )}

            </span>

          </div>


          {/* MEETING INFO */}

          <div className="min-w-0">

            <p className="manager-label">

              {today
                ? "Today's meeting"
                : formatDate(
                    meeting.start_time
                  )
              }

            </p>


            <h3 className="font-semibold text-lg mt-2 truncate">

              {meeting.title ||
                "Untitled meeting"}

            </h3>


            {meeting.description && (

              <p className="text-sm manager-muted mt-2 leading-relaxed line-clamp-2">

                {meeting.description}

              </p>

            )}

          </div>

        </div>


        {/* STATUS */}

        <span
          className={`
            hidden sm:inline-flex
            px-2.5 py-1
            rounded-full
            text-xs font-medium
            flex-shrink-0
            ${
              past
                ? "bg-neutral-100 text-neutral-400"
                : "bg-neutral-950 text-white"
            }
          `}
        >

          {past
            ? "Finished"
            : today
            ? "Today"
            : "Upcoming"
          }

        </span>

      </div>


      {/* =================================================
          DETAILS
      ================================================= */}

      <div className="manager-divider my-5" />


      <div className="flex flex-wrap gap-x-6 gap-y-3 text-sm">


        {/* TIME */}

        <div>

          <p className="text-xs manager-muted">
            Time
          </p>

          <p className="font-medium mt-1">

            {formatTime(
              meeting.start_time
            )}

            {meeting.end_time && (
              <>
                {" — "}
                {formatTime(
                  meeting.end_time
                )}
              </>
            )}

          </p>

        </div>


        {/* DATE */}

        <div>

          <p className="text-xs manager-muted">
            Date
          </p>

          <p className="font-medium mt-1">

            {formatDate(
              meeting.start_time
            )}

          </p>

        </div>


        {/* LOCATION */}

        {meeting.location && (

          <div>

            <p className="text-xs manager-muted">
              Location
            </p>

            <p className="font-medium mt-1">

              {meeting.location}

            </p>

          </div>

        )}

      </div>


      {/* =================================================
          ACTION
      ================================================= */}

      <div className="mt-5 flex items-center justify-between gap-4">


        <p className="text-xs manager-muted">

          {past
            ? "Meeting finished"
            : "Manager is watching your schedule"
          }

        </p>


        {!past &&
          meeting.meeting_link && (

          <a
            href={
              meeting.meeting_link
            }
            target="_blank"
            rel="noreferrer"
            className="manager-button-primary whitespace-nowrap"
          >

            Join meeting

          </a>

        )}

      </div>

    </div>

  );

}