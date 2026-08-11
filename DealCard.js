"use client";


export default function DealCard({
  deal,
  onClick
}) {

  if (!deal) {
    return null;
  }


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
  // FORMAT DATE
  // =====================================================

  function formatDate(value) {

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
  // FOLLOW UP
  // =====================================================

  const followUpDate =
    formatDate(
      deal.next_follow_up
    );


  // =====================================================
  // CARD
  // =====================================================

  return (

    <button
      type="button"
      onClick={
        () => {

          if (onClick) {
            onClick(deal);
          }

        }
      }
      className="
        manager-card
        w-full
        text-left
        p-5
        hover:bg-neutral-50
        transition
      "
    >


      {/* =================================================
          TOP
      ================================================= */}

      <div className="flex items-start justify-between gap-5">


        {/* BRAND */}

        <div className="min-w-0">

          <p className="manager-label">
            Brand deal
          </p>


          <h3 className="text-lg font-semibold mt-2 truncate">

            {deal.company ||
              "Unknown brand"}

          </h3>


          <p className="text-sm manager-muted mt-1 truncate">

            {deal.contact_name ||
              deal.contact_email ||
              "Contact unavailable"}

          </p>

        </div>


        {/* VALUE */}

        <div className="text-right flex-shrink-0">

          <p className="manager-label">
            Value
          </p>

          <p className="font-semibold mt-2">

            {formatMoney(
              deal.deal_value,
              deal.currency
            )}

          </p>

        </div>

      </div>


      {/* =================================================
          DIVIDER
      ================================================= */}

      <div className="manager-divider my-5" />


      {/* =================================================
          STATUS
      ================================================= */}

      <div className="flex flex-wrap items-center justify-between gap-4">


        <div>

          <p className="text-xs manager-muted">
            Status
          </p>

          <div className="mt-2">

            <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-neutral-100 text-neutral-600 text-xs font-medium">

              {formatStatus(
                deal.status
              )}

            </span>

          </div>

        </div>


        {/* FOLLOW UP */}

        <div className="text-right">

          <p className="text-xs manager-muted">
            Next follow-up
          </p>

          <p className="text-sm font-medium mt-2">

            {followUpDate ||
              "Not scheduled"}

          </p>

        </div>

      </div>


      {/* =================================================
          NEXT ACTION
      ================================================= */}

      {deal.next_action && (

        <div className="mt-5 bg-neutral-50 border border-neutral-100 rounded-xl px-4 py-3">

          <p className="text-xs manager-muted">
            Next action
          </p>

          <p className="text-sm font-medium mt-1.5">

            {deal.next_action}

          </p>

        </div>

      )}


      {/* =================================================
          BOTTOM
      ================================================= */}

      <div className="mt-5 flex items-center justify-between">

        <p className="text-xs manager-muted">

          {followUpDate
            ? "Manager is tracking this deal"
            : "No follow-up scheduled"
          }

        </p>


        <span className="text-sm">
          →
        </span>

      </div>

    </button>

  );

}