"use client";

import { useEffect, useState } from "react";


const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:5000";


export default function Header({
  title = "Today",
  subtitle = ""
}) {

  const [user, setUser] =
    useState(null);

  const [loadingUser, setLoadingUser] =
    useState(true);

  const [syncing, setSyncing] =
    useState(false);

  const [message, setMessage] =
    useState("");


  // =====================================================
  // LOAD USER
  // =====================================================

  useEffect(() => {

    async function loadUser() {

      try {

        const response =
          await fetch(
            `${API_URL}/api/me`,
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
            "Could not load user"
          );

        }


        const data =
          await response.json();


        if (data.user) {

          setUser(data.user);

        } else {

          setUser(data);

        }


      } catch (error) {

        console.error(
          "Header user error:",
          error
        );

      } finally {

        setLoadingUser(false);

      }

    }


    loadUser();

  }, []);


  // =====================================================
  // RUN MANAGER
  // =====================================================

  async function runManager() {

    if (syncing) {
      return;
    }


    try {

      setSyncing(true);
      setMessage("");


      const response =
        await fetch(
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


      setMessage(
        "Manager is working"
      );


      setTimeout(
        () => {
          setMessage("");
        },
        3000
      );


    } catch (error) {

      console.error(
        "Manager sync error:",
        error
      );


      setMessage(
        "Could not sync"
      );


      setTimeout(
        () => {
          setMessage("");
        },
        3000
      );


    } finally {

      setSyncing(false);

    }

  }


  // =====================================================
  // USER INITIAL
  // =====================================================

  function getInitial() {

    const value =
      user?.name ||
      user?.email ||
      "C";


    return value
      .charAt(0)
      .toUpperCase();

  }


  // =====================================================
  // HEADER
  // =====================================================

  return (

    <header className="w-full bg-white border-b border-neutral-200">


      <div className="px-6 md:px-8 h-20 flex items-center justify-between gap-5">


        {/* =================================================
            LEFT
        ================================================= */}

        <div className="min-w-0">

          <h1 className="font-semibold text-lg truncate">

            {title}

          </h1>


          {subtitle && (

            <p className="text-sm manager-muted mt-0.5 truncate">

              {subtitle}

            </p>

          )}

        </div>


        {/* =================================================
            RIGHT
        ================================================= */}

        <div className="flex items-center gap-3">


          {/* STATUS */}

          <div className="hidden md:flex items-center gap-2 mr-2">

            <div className="manager-status-dot" />

            <span className="text-xs manager-muted">

              {message ||
                "Manager active"}

            </span>

          </div>


          {/* RUN MANAGER */}

          <button
            onClick={runManager}
            disabled={syncing}
            className="manager-button-secondary whitespace-nowrap"
          >

            {syncing
              ? "Working..."
              : "Run manager"
            }

          </button>


          {/* USER */}

          <div className="flex items-center gap-3 ml-1">


            <div className="hidden lg:block text-right max-w-[170px]">

              <p className="text-sm font-medium truncate">

                {loadingUser
                  ? "Loading..."
                  : user?.name ||
                    "Creator"
                }

              </p>


              <p className="text-xs manager-muted truncate mt-0.5">

                {loadingUser
                  ? ""
                  : user?.email ||
                    "Google connected"
                }

              </p>

            </div>


            <div className="w-9 h-9 rounded-full bg-neutral-950 text-white flex items-center justify-center text-sm font-semibold flex-shrink-0">

              {loadingUser
                ? "..."
                : getInitial()
              }

            </div>

          </div>

        </div>

      </div>

    </header>

  );

}