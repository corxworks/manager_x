"use client";

import { useState } from "react";


const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:5000";


export default function TaskCard({
  task,
  onCompleted
}) {

  const [completing, setCompleting] =
    useState(false);

  const [error, setError] =
    useState("");


  // =====================================================
  // SAFE TASK
  // =====================================================

  if (!task) {
    return null;
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
  // FORMAT PRIORITY
  // =====================================================

  function formatPriority(value) {

    if (!value) {
      return "Low";
    }


    return (
      value.charAt(0).toUpperCase() +
      value.slice(1)
    );

  }


  // =====================================================
  // COMPLETE TASK
  // =====================================================

  async function completeTask() {

    if (
      completing ||
      task.status === "completed"
    ) {
      return;
    }


    try {

      setCompleting(true);
      setError("");


      const response =
        await fetch(
          `${API_URL}/api/tasks/${task.id}/complete`,
          {
            method: "PATCH",
            credentials: "include"
          }
        );


      if (
        response.status === 401
      ) {

        window.location.href =
          "/";

        return;

      }


      if (!response.ok) {

        throw new Error(
          "Could not complete task"
        );

      }


      let updatedTask = {
        ...task,
        status: "completed"
      };


      try {

        const data =
          await response.json();

        if (data?.task) {

          updatedTask =
            data.task;

        } else if (
          data?.id
        ) {

          updatedTask =
            data;

        }

      } catch {

        // Backend may return no JSON.
        // Local completed state is enough.

      }


      if (onCompleted) {

        onCompleted(
          updatedTask
        );

      }


    } catch (err) {

      console.error(
        "Task completion error:",
        err
      );


      setError(
        "Could not update task."
      );


    } finally {

      setCompleting(false);

    }

  }


  // =====================================================
  // STATUS
  // =====================================================

  const completed =
    task.status === "completed";


  const urgent =
    task.priority === "urgent";


  // =====================================================
  // CARD
  // =====================================================

  return (

    <div className="manager-card p-5">


      {/* =================================================
          TOP
      ================================================= */}

      <div className="flex items-start justify-between gap-5">


        {/* TASK INFO */}

        <div className="flex items-start gap-3 min-w-0">


          {/* STATUS DOT */}

          <div
            className={`
              w-2 h-2
              rounded-full
              mt-2
              flex-shrink-0
              ${
                completed
                  ? "bg-neutral-300"
                  : urgent
                  ? "bg-neutral-950"
                  : "bg-neutral-400"
              }
            `}
          />


          <div className="min-w-0">


            {/* TITLE */}

            <p
              className={`
                font-medium
                ${
                  completed
                    ? "line-through text-neutral-400"
                    : "text-neutral-950"
                }
              `}
            >

              {task.title ||
                "Untitled task"}

            </p>


            {/* DESCRIPTION */}

            {task.description && (

              <p className="text-sm manager-muted mt-2 leading-relaxed">

                {task.description}

              </p>

            )}


          </div>

        </div>


        {/* AI BADGE */}

        {task.created_by_ai && (

          <span className="hidden sm:inline-flex flex-shrink-0 px-2.5 py-1 rounded-full bg-neutral-100 text-neutral-500 text-xs font-medium">

            Manager created

          </span>

        )}

      </div>


      {/* =================================================
          META
      ================================================= */}

      <div className="flex flex-wrap items-center gap-x-4 gap-y-2 mt-5 text-xs manager-muted">


        <span>

          {formatPriority(
            task.priority
          )}{" "}
          priority

        </span>


        <span>
          •
        </span>


        <span>

          {formatDate(
            task.deadline
          )}

        </span>


        {task.source && (

          <>

            <span>
              •
            </span>

            <span className="capitalize">

              From{" "}
              {task.source.replaceAll(
                "_",
                " "
              )}

            </span>

          </>

        )}

      </div>


      {/* =================================================
          ERROR
      ================================================= */}

      {error && (

        <p className="text-xs mt-4">
          {error}
        </p>

      )}


      {/* =================================================
          ACTION
      ================================================= */}

      <div className="manager-divider my-5" />


      <div className="flex items-center justify-between gap-4">


        <p className="text-xs manager-muted">

          {completed
            ? "Completed"
            : urgent
            ? "Needs your attention"
            : "Manager prepared this task"
          }

        </p>


        {completed ? (

          <span className="text-sm manager-muted">
            Done ✓
          </span>

        ) : (

          <button
            onClick={completeTask}
            disabled={completing}
            className="manager-button-secondary"
          >

            {completing
              ? "Completing..."
              : "Mark done"
            }

          </button>

        )}

      </div>

    </div>

  );

}