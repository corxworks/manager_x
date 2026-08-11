"use client";

import { useEffect, useState } from "react";


const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:5000";


export default function Tasks() {

  const [tasks, setTasks] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [completing, setCompleting] =
    useState(null);

  const [filter, setFilter] =
    useState("pending");


  // =====================================================
  // LOAD TASKS
  // =====================================================

  async function loadTasks() {

    try {

      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_URL}/api/tasks`,
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
          "Could not load tasks"
        );

      }

      const data =
        await response.json();

      setTasks(
        data.tasks || []
      );

    } catch (err) {

      console.error(err);

      setError(
        "Manager X could not load your tasks."
      );

    } finally {

      setLoading(false);

    }

  }


  // =====================================================
  // FIRST LOAD
  // =====================================================

  useEffect(() => {

    loadTasks();

  }, []);


  // =====================================================
  // COMPLETE TASK
  // =====================================================

  async function completeTask(
    taskId
  ) {

    if (completing) {
      return;
    }

    try {

      setCompleting(taskId);
      setError("");

      const response = await fetch(
        `${API_URL}/api/tasks/${taskId}/complete`,
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

        throw new Error(
          "Could not complete task"
        );

      }


      // Update UI immediately

      setTasks(
        (currentTasks) =>
          currentTasks.map(
            (task) =>
              task.id === taskId
                ? {
                    ...task,
                    status: "completed"
                  }
                : task
          )
      );

    } catch (err) {

      console.error(err);

      setError(
        "Manager X could not update this task."
      );

    } finally {

      setCompleting(null);

    }

  }


  // =====================================================
  // FORMAT DATE
  // =====================================================

  function formatDate(value) {

    if (!value) {
      return "No deadline";
    }

    const date =
      new Date(value);

    if (
      Number.isNaN(
        date.getTime()
      )
    ) {

      return "No deadline";

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
  // FILTER TASKS
  // =====================================================

  const filteredTasks =
    tasks.filter(
      (task) => {

        if (filter === "all") {
          return true;
        }

        return (
          task.status === filter
        );

      }
    );


  // =====================================================
  // SUMMARY
  // =====================================================

  const pendingCount =
    tasks.filter(
      (task) =>
        task.status === "pending"
    ).length;

  const urgentCount =
    tasks.filter(
      (task) =>
        task.status === "pending" &&
        task.priority === "urgent"
    ).length;

  const completedCount =
    tasks.filter(
      (task) =>
        task.status === "completed"
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
              Tasks
            </h1>

            <p className="manager-muted mt-2">
              Work your manager prepared
              for you.
            </p>

          </div>


          <button
            onClick={loadTasks}
            className="manager-button-secondary"
          >
            Refresh tasks
          </button>

        </header>


        {/* =================================================
            SUMMARY
        ================================================= */}

        <section className="grid sm:grid-cols-3 gap-4 mt-8">

          <SummaryCard
            value={pendingCount}
            label="Pending"
          />

          <SummaryCard
            value={urgentCount}
            label="Urgent"
          />

          <SummaryCard
            value={completedCount}
            label="Completed"
          />

        </section>


        {/* =================================================
            FILTER
        ================================================= */}

        <section className="mt-6 flex flex-wrap gap-2">

          <FilterButton
            active={
              filter === "pending"
            }
            onClick={
              () =>
                setFilter("pending")
            }
          >
            Pending
          </FilterButton>


          <FilterButton
            active={
              filter === "completed"
            }
            onClick={
              () =>
                setFilter(
                  "completed"
                )
            }
          >
            Completed
          </FilterButton>


          <FilterButton
            active={
              filter === "all"
            }
            onClick={
              () =>
                setFilter("all")
            }
          >
            All
          </FilterButton>

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
            TASK LIST
        ================================================= */}

        <section className="manager-card mt-5 overflow-hidden">

          {loading ? (

            <div className="manager-empty">

              <div className="manager-loading" />

              <p className="text-sm mt-4">
                Preparing your work...
              </p>

            </div>

          ) : filteredTasks.length === 0 ? (

            <div className="manager-empty">

              <p className="font-medium text-neutral-950">

                {filter === "pending"
                  ? "Nothing needs your attention."
                  : filter === "completed"
                  ? "No completed tasks yet."
                  : "No tasks yet."
                }

              </p>

              <p className="text-sm mt-2">

                {filter === "pending"
                  ? "Everything else can wait."
                  : "Manager X will keep this organized."
                }

              </p>

            </div>

          ) : (

            <div>

              {filteredTasks.map(
                (task, index) => (

                  <div
                    key={task.id}
                  >

                    <TaskRow
                      task={task}
                      formatDate={
                        formatDate
                      }
                      completing={
                        completing ===
                        task.id
                      }
                      onComplete={
                        () =>
                          completeTask(
                            task.id
                          )
                      }
                    />


                    {index <
                      filteredTasks.length -
                        1 && (

                      <div className="manager-divider" />

                    )}

                  </div>

                )
              )}

            </div>

          )}

        </section>


        {/* =================================================
            MANAGER MESSAGE
        ================================================= */}

        <section className="manager-card p-6 mt-5">

          <div className="flex items-start gap-4">

            <div className="manager-status-dot mt-1.5" />

            <div>

              <p className="font-medium">
                You don&apos;t need to manage
                this list.
              </p>

              <p className="text-sm manager-muted mt-2 leading-relaxed">

                Manager X creates tasks from
                important emails, deals,
                payments and meetings so you
                only see the work that needs
                action.

              </p>

            </div>

          </div>

        </section>

      </div>

    </main>

  );

}


// =========================================================
// TASK ROW
// =========================================================

function TaskRow({
  task,
  formatDate,
  completing,
  onComplete
}) {

  const completed =
    task.status === "completed";


  return (

    <div className="p-5 md:p-6 flex flex-col md:flex-row md:items-center justify-between gap-5">


      {/* LEFT */}

      <div className="flex items-start gap-4">

        <div
          className={`
            mt-1.5
            w-2 h-2
            rounded-full
            flex-shrink-0
            ${
              completed
                ? "bg-neutral-300"
                : task.priority ===
                  "urgent"
                ? "bg-neutral-950"
                : "bg-neutral-400"
            }
          `}
        />


        <div>

          <div className="flex flex-wrap items-center gap-2">

            <p
              className={`
                font-medium
                ${
                  completed
                    ? "line-through text-neutral-400"
                    : ""
                }
              `}
            >
              {task.title}
            </p>


            {task.created_by_ai && (

              <span className="text-xs px-2.5 py-1 rounded-full bg-neutral-100 text-neutral-500">

                Manager created

              </span>

            )}

          </div>


          {task.description && (

            <p className="text-sm manager-muted mt-2 leading-relaxed max-w-2xl">

              {task.description}

            </p>

          )}


          <div className="flex flex-wrap gap-x-4 gap-y-2 mt-3 text-xs manager-muted">

            <span className="capitalize">

              {task.priority || "low"}
              {" "}priority

            </span>

            <span>
              {formatDate(
                task.deadline
              )}
            </span>

          </div>

        </div>

      </div>


      {/* RIGHT */}

      {!completed && (

        <button
          onClick={onComplete}
          disabled={completing}
          className="manager-button-secondary whitespace-nowrap"
        >

          {completing
            ? "Completing..."
            : "Mark done"
          }

        </button>

      )}


      {completed && (

        <span className="text-sm manager-muted whitespace-nowrap">
          Completed ✓
        </span>

      )}

    </div>

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
// FILTER BUTTON
// =========================================================

function FilterButton({
  active,
  onClick,
  children
}) {

  return (

    <button
      onClick={onClick}
      className={`
        px-4 py-2
        rounded-xl
        text-sm font-medium
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