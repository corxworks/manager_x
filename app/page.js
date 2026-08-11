"use client";

import { useEffect, useState } from "react";


export default function Home() {

  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);


  // =====================================================
  // CHECK LOGIN
  // =====================================================

  useEffect(() => {

    async function checkUser() {

      try {

        const response = await fetch(
          "http://localhost:5000/api/me",
          {
            credentials: "include"
          }
        );

        if (response.ok) {

          const data = await response.json();

          if (data.authenticated) {

            setUser(data.user);

          }

        }

      } catch (error) {

        console.log(
          "Backend connection error:",
          error
        );

      } finally {

        setLoading(false);

      }

    }

    checkUser();

  }, []);


  // =====================================================
  // GOOGLE LOGIN
  // =====================================================

  function loginWithGoogle() {

    window.location.href =
      "http://localhost:5000/auth/google";

  }


  // =====================================================
  // OPEN DASHBOARD
  // =====================================================

  function openDashboard() {

    window.location.href =
      "/dashboard";

  }


  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {

    return (
      <main className="min-h-screen flex items-center justify-center bg-white">

        <p className="text-sm text-neutral-500">
          Loading...
        </p>

      </main>
    );

  }


  // =====================================================
  // PAGE
  // =====================================================

  return (

    <main className="min-h-screen bg-white text-neutral-950">


      {/* =================================================
          NAVBAR
      ================================================= */}

      <nav className="max-w-7xl mx-auto px-6 lg:px-8 h-20 flex items-center justify-between">

        <div className="flex items-center gap-3">

          <div className="w-9 h-9 rounded-xl bg-black text-white flex items-center justify-center font-semibold">
            C
          </div>

          <div>
            <p className="font-semibold text-lg leading-none">
              CORX
            </p>

            <p className="text-xs text-neutral-500 mt-1">
              Manager X
            </p>
          </div>

        </div>


        {user ? (

          <button
            onClick={openDashboard}
            className="px-5 py-2.5 rounded-xl bg-black text-white text-sm font-medium hover:bg-neutral-800 transition"
          >
            Open Manager
          </button>

        ) : (

          <button
            onClick={loginWithGoogle}
            className="px-5 py-2.5 rounded-xl border border-neutral-200 text-sm font-medium hover:bg-neutral-50 transition"
          >
            Sign in
          </button>

        )}

      </nav>


      {/* =================================================
          HERO
      ================================================= */}

      <section className="max-w-5xl mx-auto px-6 pt-24 md:pt-32 pb-20 text-center">


        <div className="inline-flex items-center px-4 py-2 rounded-full border border-neutral-200 bg-neutral-50 text-sm text-neutral-600 mb-8">

          Built for creators who do everything themselves.

        </div>


        <h1 className="text-5xl md:text-7xl lg:text-8xl font-semibold tracking-tight leading-[0.95]">

          You create.

          <br />

          <span className="text-neutral-400">
            We manage.
          </span>

        </h1>


        <p className="max-w-2xl mx-auto mt-8 text-lg md:text-xl text-neutral-500 leading-relaxed">

          Manager X handles your inbox, brand deals,
          meetings, files, payments and follow-ups —
          so you can spend your time creating.

        </p>


        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-3">


          {user ? (

            <button
              onClick={openDashboard}
              className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-black text-white font-medium hover:bg-neutral-800 transition"
            >
              Open Manager X
            </button>

          ) : (

            <button
              onClick={loginWithGoogle}
              className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-black text-white font-medium hover:bg-neutral-800 transition"
            >
              Continue with Google
            </button>

          )}


          <a
            href="#how-it-works"
            className="w-full sm:w-auto px-7 py-3.5 rounded-xl border border-neutral-200 font-medium hover:bg-neutral-50 transition"
          >
            See how it works
          </a>

        </div>


        <p className="mt-4 text-xs text-neutral-400">

          Connect Gmail, Calendar, Drive and Sheets.

        </p>

      </section>


      {/* =================================================
          MANAGER PREVIEW
      ================================================= */}

      <section className="max-w-6xl mx-auto px-6 pb-28">

        <div className="border border-neutral-200 rounded-3xl shadow-sm bg-neutral-50 p-3">

          <div className="bg-white border border-neutral-200 rounded-2xl overflow-hidden">


            {/* TOP BAR */}

            <div className="h-14 px-5 border-b border-neutral-100 flex items-center justify-between">

              <div className="flex items-center gap-2">

                <div className="w-2.5 h-2.5 rounded-full bg-neutral-200" />
                <div className="w-2.5 h-2.5 rounded-full bg-neutral-200" />
                <div className="w-2.5 h-2.5 rounded-full bg-neutral-200" />

              </div>

              <p className="text-xs text-neutral-400">
                Manager X
              </p>

              <div className="w-12" />

            </div>


            {/* DASHBOARD PREVIEW */}

            <div className="p-6 md:p-10">

              <p className="text-sm text-neutral-500">
                Good morning
              </p>

              <h2 className="text-3xl font-semibold mt-1">
                Here&apos;s what needs your attention.
              </h2>


              <div className="grid md:grid-cols-3 gap-4 mt-8">


                {/* PRIORITY */}

                <div className="md:col-span-2 border border-neutral-200 rounded-2xl p-6">

                  <p className="text-xs font-medium uppercase tracking-wider text-neutral-400">
                    Today&apos;s priority
                  </p>

                  <div className="mt-6 space-y-5">


                    <div className="flex items-center justify-between gap-4">

                      <div>

                        <p className="font-medium">
                          Reply to Samsung
                        </p>

                        <p className="text-sm text-neutral-500 mt-1">
                          Brand deal · $5,000
                        </p>

                      </div>

                      <span className="text-xs px-3 py-1.5 rounded-full bg-neutral-100">
                        Urgent
                      </span>

                    </div>


                    <div className="border-t border-neutral-100" />


                    <div className="flex items-center justify-between gap-4">

                      <div>

                        <p className="font-medium">
                          Send Nike invoice
                        </p>

                        <p className="text-sm text-neutral-500 mt-1">
                          Payment due today
                        </p>

                      </div>

                      <span className="text-xs px-3 py-1.5 rounded-full bg-neutral-100">
                        Finance
                      </span>

                    </div>


                    <div className="border-t border-neutral-100" />


                    <div className="flex items-center justify-between gap-4">

                      <div>

                        <p className="font-medium">
                          Adidas campaign call
                        </p>

                        <p className="text-sm text-neutral-500 mt-1">
                          Today at 4:00 PM
                        </p>

                      </div>

                      <span className="text-xs px-3 py-1.5 rounded-full bg-neutral-100">
                        Meeting
                      </span>

                    </div>

                  </div>

                </div>


                {/* SUMMARY */}

                <div className="border border-neutral-200 rounded-2xl p-6">

                  <p className="text-xs font-medium uppercase tracking-wider text-neutral-400">
                    Manager summary
                  </p>


                  <div className="mt-6 space-y-6">

                    <div>

                      <p className="text-3xl font-semibold">
                        2
                      </p>

                      <p className="text-sm text-neutral-500 mt-1">
                        Brand deals need attention
                      </p>

                    </div>


                    <div>

                      <p className="text-3xl font-semibold">
                        3
                      </p>

                      <p className="text-sm text-neutral-500 mt-1">
                        Follow-ups due
                      </p>

                    </div>


                    <div>

                      <p className="text-3xl font-semibold">
                        $4,000
                      </p>

                      <p className="text-sm text-neutral-500 mt-1">
                        Payment pending
                      </p>

                    </div>

                  </div>

                </div>

              </div>


              <div className="mt-5 border border-neutral-200 rounded-2xl px-6 py-5">

                <p className="font-medium">
                  Everything else can wait.
                </p>

                <p className="text-sm text-neutral-500 mt-1">
                  Manager X is handling the rest in the background.
                </p>

              </div>

            </div>

          </div>

        </div>

      </section>


      {/* =================================================
          HOW IT WORKS
      ================================================= */}

      <section
        id="how-it-works"
        className="border-t border-neutral-100"
      >

        <div className="max-w-6xl mx-auto px-6 py-24">

          <div className="max-w-2xl">

            <p className="text-sm font-medium text-neutral-500">
              How it works
            </p>

            <h2 className="text-4xl md:text-5xl font-semibold tracking-tight mt-3">
              One manager.
              <br />
              All the boring work.
            </h2>

          </div>


          <div className="grid md:grid-cols-3 gap-10 mt-16">


            <div>

              <p className="text-sm text-neutral-400">
                01
              </p>

              <h3 className="text-xl font-semibold mt-4">
                Connect
              </h3>

              <p className="text-neutral-500 mt-3 leading-relaxed">
                Connect the Google tools you already use.
                No complicated setup.
              </p>

            </div>


            <div>

              <p className="text-sm text-neutral-400">
                02
              </p>

              <h3 className="text-xl font-semibold mt-4">
                Manager X works
              </h3>

              <p className="text-neutral-500 mt-3 leading-relaxed">
                Important emails, deals, meetings,
                payments and follow-ups are organized automatically.
              </p>

            </div>


            <div>

              <p className="text-sm text-neutral-400">
                03
              </p>

              <h3 className="text-xl font-semibold mt-4">
                You create
              </h3>

              <p className="text-neutral-500 mt-3 leading-relaxed">
                Open one dashboard, see what matters,
                and spend the rest of your time creating.
              </p>

            </div>

          </div>

        </div>

      </section>


      {/* =================================================
          FINAL CTA
      ================================================= */}

      <section className="border-t border-neutral-100">

        <div className="max-w-4xl mx-auto px-6 py-28 text-center">

          <h2 className="text-4xl md:text-6xl font-semibold tracking-tight">

            Stop managing.

            <br />

            <span className="text-neutral-400">
              Start creating.
            </span>

          </h2>


          <button
            onClick={
              user
                ? openDashboard
                : loginWithGoogle
            }
            className="mt-10 px-7 py-3.5 rounded-xl bg-black text-white font-medium hover:bg-neutral-800 transition"
          >
            {user
              ? "Open Manager X"
              : "Continue with Google"
            }
          </button>

        </div>

      </section>


      {/* =================================================
          FOOTER
      ================================================= */}

      <footer className="border-t border-neutral-100">

        <div className="max-w-7xl mx-auto px-6 py-8 flex items-center justify-between">

          <p className="text-sm font-medium">
            CORX
          </p>

          <p className="text-xs text-neutral-400">
            Creators create. We manage.
          </p>

        </div>

      </footer>

    </main>
  );
}