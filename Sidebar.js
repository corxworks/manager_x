"use client";

import { usePathname } from "next/navigation";


const navigation = [

  {
    name: "Today",
    href: "/dashboard",
    icon: HomeIcon
  },

  {
    name: "Inbox",
    href: "/inbox",
    icon: InboxIcon
  },

  {
    name: "Brand CRM",
    href: "/deals",
    icon: BriefcaseIcon
  },

  {
    name: "Tasks",
    href: "/tasks",
    icon: CheckIcon
  },

  {
    name: "Calendar",
    href: "/calendar",
    icon: CalendarIcon
  },

  {
    name: "Drive",
    href: "/drive",
    icon: FileIcon
  },

  {
    name: "Finance",
    href: "/finance",
    icon: MoneyIcon
  }

];


export default function Sidebar() {

  const pathname =
    usePathname();


  // =====================================================
  // ACTIVE PAGE
  // =====================================================

  function isActive(href) {

    if (
      href === "/dashboard"
    ) {

      return (
        pathname === "/dashboard"
      );

    }

    return (
      pathname === href ||
      pathname.startsWith(
        `${href}/`
      )
    );

  }


  // =====================================================
  // SIDEBAR
  // =====================================================

  return (

    <aside className="w-[250px] min-h-screen bg-white border-r border-neutral-200 flex flex-col">


      {/* =================================================
          BRAND
      ================================================= */}

      <div className="h-20 px-5 flex items-center">

        <a
          href="/dashboard"
          className="flex items-center gap-3"
        >

          <div className="w-9 h-9 rounded-xl bg-neutral-950 text-white flex items-center justify-center font-semibold">

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

        </a>

      </div>


      {/* =================================================
          MANAGER STATUS
      ================================================= */}

      <div className="px-4">

        <div className="bg-neutral-50 border border-neutral-200 rounded-xl px-4 py-3 flex items-center gap-3">

          <div className="manager-status-dot" />

          <div>

            <p className="text-sm font-medium">
              Manager active
            </p>

            <p className="text-xs manager-muted mt-0.5">
              Working in background
            </p>

          </div>

        </div>

      </div>


      {/* =================================================
          NAVIGATION
      ================================================= */}

      <nav className="px-3 mt-6 flex-1">

        <p className="manager-label px-3 mb-2">
          Workspace
        </p>


        <div className="space-y-1">

          {navigation.map(
            (item) => {

              const active =
                isActive(
                  item.href
                );

              const Icon =
                item.icon;


              return (

                <a
                  key={item.href}
                  href={item.href}
                  className={`
                    flex items-center gap-3
                    px-3 py-2.5
                    rounded-xl
                    text-sm
                    transition
                    ${
                      active
                        ? "bg-neutral-100 text-neutral-950 font-medium"
                        : "text-neutral-500 hover:bg-neutral-50 hover:text-neutral-950"
                    }
                  `}
                >

                  <Icon />

                  <span>
                    {item.name}
                  </span>

                </a>

              );

            }
          )}

        </div>

      </nav>


      {/* =================================================
          BOTTOM
      ================================================= */}

      <div className="p-4">

        <div className="manager-divider mb-4" />


        <div className="px-3 py-2">

          <p className="text-xs manager-muted leading-relaxed">

            Creators create.
            <br />
            Manager X manages.

          </p>

        </div>

      </div>

    </aside>

  );

}


// =========================================================
// HOME ICON
// =========================================================

function HomeIcon() {

  return (

    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >

      <path d="M3 10.5L12 3l9 7.5" />

      <path d="M5 9.5V21h14V9.5" />

      <path d="M9 21v-6h6v6" />

    </svg>

  );

}


// =========================================================
// INBOX ICON
// =========================================================

function InboxIcon() {

  return (

    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >

      <path d="M4 4h16v16H4z" />

      <path d="M4 14h4l2 3h4l2-3h4" />

    </svg>

  );

}


// =========================================================
// BRIEFCASE ICON
// =========================================================

function BriefcaseIcon() {

  return (

    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >

      <rect
        x="3"
        y="7"
        width="18"
        height="13"
        rx="2"
      />

      <path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />

      <path d="M3 12h18" />

    </svg>

  );

}


// =========================================================
// CHECK ICON
// =========================================================

function CheckIcon() {

  return (

    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >

      <rect
        x="3"
        y="3"
        width="18"
        height="18"
        rx="3"
      />

      <path d="M8 12l3 3 5-6" />

    </svg>

  );

}


// =========================================================
// CALENDAR ICON
// =========================================================

function CalendarIcon() {

  return (

    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >

      <rect
        x="3"
        y="5"
        width="18"
        height="16"
        rx="2"
      />

      <path d="M8 3v4" />

      <path d="M16 3v4" />

      <path d="M3 10h18" />

    </svg>

  );

}


// =========================================================
// FILE ICON
// =========================================================

function FileIcon() {

  return (

    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >

      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />

      <path d="M14 2v6h6" />

    </svg>

  );

}


// =========================================================
// MONEY ICON
// =========================================================

function MoneyIcon() {

  return (

    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >

      <rect
        x="3"
        y="5"
        width="18"
        height="14"
        rx="2"
      />

      <path d="M7 9h.01" />

      <path d="M17 15h.01" />

      <circle
        cx="12"
        cy="12"
        r="2.5"
      />

    </svg>

  );

}