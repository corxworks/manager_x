"use client";

import { useEffect, useState } from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:5000";


// =========================================================
// CLEAN + SHORT EMAIL PREVIEW
// =========================================================

function getPreview(value) {
  if (!value) {
    return "No message preview";
  }

  let text = String(value);

  // Remove invisible / zero-width / control characters
  text = text.replace(
    /[\u0000-\u001F\u007F-\u009F\u00AD\u034F\u061C\u180E\u200B-\u200F\u202A-\u202E\u2060-\u206F\uFEFF]/g,
    " "
  );

  // Remove HTML comments
  text = text.replace(
    /<!--[\s\S]*?-->/g,
    " "
  );

  // Remove HTML tags
  text = text.replace(
    /<[^>]*>/g,
    " "
  );

  // Markdown links -> visible text
  text = text.replace(
    /\[([^\]]+)\]\([^)]+\)/g,
    "$1"
  );

  // Remove URLs
  text = text.replace(
    /https?:\/\/\S+/gi,
    " "
  );

  // HTML entities
  text = text.replace(
    /&nbsp;/gi,
    " "
  );

  text = text.replace(
    /&amp;/gi,
    "&"
  );

  text = text.replace(
    /&lt;/gi,
    "<"
  );

  text = text.replace(
    /&gt;/gi,
    ">"
  );

  text = text.replace(
    /&quot;/gi,
    '"'
  );

  text = text.replace(
    /&#39;/gi,
    "'"
  );

  // Normalize whitespace
  text = text
    .replace(/\s+/g, " ")
    .trim();

  if (!text) {
    return "No message preview";
  }

  // Keep inbox preview short
  if (text.length > 100) {
    return (
      text.substring(0, 100).trim() +
      "..."
    );
  }

  return text;
}


// =========================================================
// INBOX
// =========================================================

export default function Inbox() {
  const [emails, setEmails] =
    useState([]);

  const [selectedEmail, setSelectedEmail] =
    useState(null);

  const [category, setCategory] =
    useState("");

  const [priority, setPriority] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  // =======================================================
  // LOAD EMAILS
  // =======================================================

  async function loadEmails() {
    try {
      setLoading(true);
      setError("");

      const params =
        new URLSearchParams();

      if (category) {
        params.append(
          "category",
          category
        );
      }

      if (priority) {
        params.append(
          "priority",
          priority
        );
      }

      const query =
        params.toString();

      const url =
        query
          ? `${API_URL}/api/inbox?${query}`
          : `${API_URL}/api/inbox`;

      const response =
        await fetch(
          url,
          {
            credentials: "include"
          }
        );

      if (response.status === 401) {
        window.location.href = "/";
        return;
      }

      if (!response.ok) {
        throw new Error(
          "Could not load inbox"
        );
      }

      const data =
        await response.json();

      const list =
        Array.isArray(data.emails)
          ? data.emails
          : [];

      setEmails(list);

      if (list.length === 0) {
        setSelectedEmail(null);
      } else {
        setSelectedEmail(
          (current) => {
            if (!current) {
              return list[0];
            }

            const updated =
              list.find(
                (email) =>
                  email.id === current.id
              );

            return (
              updated ||
              list[0]
            );
          }
        );
      }

    } catch (err) {
      console.error(
        "Inbox loading error:",
        err
      );

      setError(
        "Manager X could not load your inbox."
      );

    } finally {
      setLoading(false);
    }
  }


  // =======================================================
  // LOAD ON START / FILTER CHANGE
  // =======================================================

  useEffect(() => {
    loadEmails();
  }, [
    category,
    priority
  ]);


  // =======================================================
  // OPEN EMAIL
  // =======================================================

  async function openEmail(email) {
    setSelectedEmail(email);

    if (email.is_read) {
      return;
    }

    try {
      const response =
        await fetch(
          `${API_URL}/api/inbox/${email.id}/read`,
          {
            method: "PATCH",
            credentials: "include"
          }
        );

      if (response.status === 401) {
        window.location.href = "/";
        return;
      }

      if (!response.ok) {
        return;
      }

      const updated =
        await response.json();

      setSelectedEmail(updated);

      setEmails(
        (current) =>
          current.map(
            (item) =>
              item.id === updated.id
                ? updated
                : item
          )
      );

    } catch (err) {
      console.error(
        "Could not mark email read:",
        err
      );
    }
  }


  // =======================================================
  // FORMAT DATE
  // =======================================================

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

    const today =
      new Date();

    if (
      date.toDateString() ===
      today.toDateString()
    ) {
      return date.toLocaleTimeString(
        undefined,
        {
          hour: "numeric",
          minute: "2-digit"
        }
      );
    }

    return date.toLocaleDateString(
      undefined,
      {
        month: "short",
        day: "numeric"
      }
    );
  }


  // =======================================================
  // FORMAT CATEGORY
  // =======================================================

  function formatCategory(value) {
    const categories = {
      brand_deal:
        "Brand deal",

      payment:
        "Payment",

      collaboration:
        "Collaboration",

      meeting:
        "Meeting",

      support:
        "Support",

      spam:
        "Spam",

      other:
        "Other"
    };

    return (
      categories[value] ||
      "Other"
    );
  }


  // =======================================================
  // PAGE
  // =======================================================

  return (
    <main className="manager-app">

      <div className="manager-container py-8 md:py-10">


        {/* =================================================
            HEADER
        ================================================= */}

        <header className="flex flex-col md:flex-row md:items-center justify-between gap-5">

          <div>

            <a
              href="/dashboard"
              className="text-sm manager-muted hover:text-neutral-950"
            >
              ← Dashboard
            </a>

            <h1 className="text-4xl font-semibold tracking-tight mt-4">
              Inbox
            </h1>

            <p className="manager-muted mt-2">
              Your manager already sorted
              what matters.
            </p>

          </div>

          <button
            onClick={loadEmails}
            disabled={loading}
            className="manager-button-secondary"
          >
            {loading
              ? "Checking..."
              : "Refresh inbox"}
          </button>

        </header>


        {/* =================================================
            FILTERS
        ================================================= */}

        <section className="mt-8 flex flex-wrap gap-3">

          <select
            value={category}
            onChange={(event) =>
              setCategory(
                event.target.value
              )
            }
            className="bg-white border border-neutral-200 rounded-xl px-4 py-2.5 text-sm"
          >

            <option value="">
              All categories
            </option>

            <option value="brand_deal">
              Brand deals
            </option>

            <option value="payment">
              Payments
            </option>

            <option value="collaboration">
              Collaborations
            </option>

            <option value="meeting">
              Meetings
            </option>

            <option value="support">
              Support
            </option>

            <option value="spam">
              Spam
            </option>

            <option value="other">
              Other
            </option>

          </select>


          <select
            value={priority}
            onChange={(event) =>
              setPriority(
                event.target.value
              )
            }
            className="bg-white border border-neutral-200 rounded-xl px-4 py-2.5 text-sm"
          >

            <option value="">
              All priorities
            </option>

            <option value="urgent">
              Urgent
            </option>

            <option value="medium">
              Medium
            </option>

            <option value="low">
              Low
            </option>

            <option value="ignore">
              Ignore
            </option>

          </select>

        </section>


        {/* =================================================
            ERROR
        ================================================= */}

        {error && (
          <div className="manager-card p-5 mt-5">

            <p className="text-sm">
              {error}
            </p>

            <button
              onClick={loadEmails}
              className="text-sm font-medium mt-3"
            >
              Try again →
            </button>

          </div>
        )}


        {/* =================================================
            INBOX
        ================================================= */}

        <section className="manager-card mt-5 overflow-hidden">

          {loading ? (

            <div className="manager-empty">

              <div className="manager-loading" />

              <p className="text-sm mt-4">
                Checking your inbox...
              </p>

            </div>

          ) : emails.length === 0 ? (

            <div className="manager-empty">

              <p className="font-medium text-neutral-950">
                Nothing needs your attention.
              </p>

              <p className="text-sm mt-2">
                Your manager has handled
                the rest.
              </p>

            </div>

          ) : (

            <div className="grid lg:grid-cols-[400px_1fr] min-h-[620px]">


              {/* ===========================================
                  EMAIL LIST
              =========================================== */}

              <div className="border-b lg:border-b-0 lg:border-r border-neutral-200">

                <div className="px-5 py-4 border-b border-neutral-100">

                  <p className="manager-label">

                    {emails.length}
                    {" "}
                    conversations

                  </p>

                </div>


                <div className="max-h-[620px] overflow-y-auto">

                  {emails.map(
                    (email) => {

                      const selected =
                        selectedEmail?.id ===
                        email.id;

                      return (

                        <button
                          key={email.id}
                          onClick={() =>
                            openEmail(email)
                          }
                          className={`
                            w-full
                            text-left
                            px-5
                            py-5
                            border-b
                            border-neutral-100
                            transition
                            ${
                              selected
                                ? "bg-neutral-50"
                                : "bg-white hover:bg-neutral-50"
                            }
                          `}
                        >

                          <div className="flex items-start justify-between gap-4">

                            <div className="min-w-0 flex-1">

                              <div className="flex items-center gap-2">

                                {!email.is_read && (
                                  <span className="manager-status-dot" />
                                )}

                                <p
                                  className={`
                                    truncate
                                    ${
                                      email.is_read
                                        ? "font-medium"
                                        : "font-semibold"
                                    }
                                  `}
                                >

                                  {email.sender_name ||
                                    email.sender_email ||
                                    "Unknown sender"}

                                </p>

                              </div>


                              {/* SUBJECT */}

                              <p className="text-sm font-medium mt-2 truncate">

                                {email.subject ||
                                  "No subject"}

                              </p>


                              {/* SHORT CLEAN PREVIEW */}

                              <p className="text-sm manager-muted mt-1 line-clamp-2">

                                {getPreview(
                                  email.body
                                )}

                              </p>

                            </div>


                            <span className="text-xs manager-subtle whitespace-nowrap">

                              {formatDate(
                                email.received_at
                              )}

                            </span>

                          </div>


                          <div className="flex items-center gap-2 mt-4">

                            <Badge>
                              {formatCategory(
                                email.category
                              )}
                            </Badge>


                            {email.priority ===
                              "urgent" && (
                              <Badge>
                                Urgent
                              </Badge>
                            )}


                            {email.priority ===
                              "high" && (
                              <Badge>
                                High
                              </Badge>
                            )}


                            {email.priority ===
                              "medium" && (
                              <Badge>
                                Medium
                              </Badge>
                            )}

                          </div>

                        </button>

                      );

                    }
                  )}

                </div>

              </div>


              {/* ===========================================
                  EMAIL DETAILS
              =========================================== */}

              <div className="bg-white">

                {selectedEmail ? (

                  <div className="p-6 md:p-8">

                    <div className="flex flex-col md:flex-row md:items-start justify-between gap-5">

                      <div>

                        <div className="flex flex-wrap gap-2">

                          <Badge>

                            {formatCategory(
                              selectedEmail.category
                            )}

                          </Badge>

                          <Badge>

                            {selectedEmail.priority ||
                              "low"}

                          </Badge>

                        </div>


                        <h2 className="text-2xl font-semibold tracking-tight mt-5">

                          {selectedEmail.subject ||
                            "No subject"}

                        </h2>


                        <p className="text-sm manager-muted mt-3">

                          From{" "}

                          <span className="text-neutral-950">

                            {selectedEmail.sender_name ||
                              selectedEmail.sender_email ||
                              "Unknown sender"}

                          </span>


                          {selectedEmail.sender_name &&
                            selectedEmail.sender_email && (
                              <>
                                {" "}
                                &lt;
                                {selectedEmail.sender_email}
                                &gt;
                              </>
                            )}

                        </p>

                      </div>


                      <p className="text-sm manager-muted whitespace-nowrap">

                        {selectedEmail.received_at
                          ? new Date(
                              selectedEmail.received_at
                            ).toLocaleString()
                          : ""}

                      </p>

                    </div>


                    <div className="manager-divider my-7" />


                    {/* FULL EMAIL BODY */}

                    <div className="max-w-3xl text-[15px] leading-7 whitespace-pre-wrap break-words">

                      {selectedEmail.body ||
                        "No email body available."}

                    </div>


                    {/* MANAGER ACTION */}

                    <div className="mt-10 bg-neutral-50 border border-neutral-200 rounded-2xl p-5 max-w-3xl">

                      <p className="manager-label">
                        Manager X
                      </p>


                      <p className="font-medium mt-3">

                        This email was classified
                        as{" "}

                        {formatCategory(
                          selectedEmail.category
                        )}

                        {" "}with{" "}

                        {selectedEmail.priority ||
                          "low"}

                        {" "}priority.

                      </p>


                      <p className="text-sm manager-muted mt-2 leading-relaxed">

                        Related tasks, deals,
                        payments or meetings can
                        be managed automatically
                        by Manager X.

                      </p>

                    </div>

                  </div>

                ) : (

                  <div className="manager-empty h-full">

                    Select an email.

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
// BADGE
// =========================================================

function Badge({
  children
}) {

  return (

    <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-neutral-100 text-neutral-600 text-xs font-medium capitalize">

      {children}

    </span>

  );
}