"use client";


export default function PriorityCard({
  title,
  description,
  type = "default",
  count,
  href,
  actionText = "View"
}) {


  // =====================================================
  // TYPE LABEL
  // =====================================================

  function getTypeLabel() {

    const labels = {

      email:
        "Inbox",

      deal:
        "Brand Deal",

      task:
        "Task",

      payment:
        "Payment",

      meeting:
        "Meeting",

      followup:
        "Follow Up",

      default:
        "Priority"

    };


    return (
      labels[type] ||
      "Priority"
    );

  }


  // =====================================================
  // HANDLE OPEN
  // =====================================================

  function handleOpen() {

    if (!href) {
      return;
    }


    window.location.href =
      href;

  }


  // =====================================================
  // CARD
  // =====================================================

  return (

    <div className="manager-card p-5 md:p-6 flex flex-col justify-between min-h-[190px]">


      {/* =================================================
          TOP
      ================================================= */}

      <div>


        <div className="flex items-start justify-between gap-4">


          {/* TYPE */}

          <div className="flex items-center gap-2">

            <span className="manager-status-dot" />

            <p className="manager-label">

              {getTypeLabel()}

            </p>

          </div>


          {/* COUNT */}

          {count !== undefined &&
            count !== null && (

            <span className="text-sm manager-muted">

              {count}

            </span>

          )}

        </div>


        {/* TITLE */}

        <h3 className="text-lg font-semibold tracking-tight mt-5">

          {title ||
            "Needs attention"}

        </h3>


        {/* DESCRIPTION */}

        {description && (

          <p className="text-sm manager-muted mt-2 leading-relaxed">

            {description}

          </p>

        )}

      </div>


      {/* =================================================
          ACTION
      ================================================= */}

      {href && (

        <div className="mt-6">

          <button
            onClick={handleOpen}
            className="text-sm font-medium inline-flex items-center gap-2 hover:opacity-60 transition"
          >

            {actionText}

            <span>
              →
            </span>

          </button>

        </div>

      )}

    </div>

  );

}