"use client";

import { useEffect, useState } from "react";


const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:5000";


export default function Drive() {

  const [files, setFiles] =
    useState([]);

  const [category, setCategory] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  // =====================================================
  // LOAD FILES
  // =====================================================

  async function loadFiles() {

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

      const query =
        params.toString();

      const url =
        query
          ? `${API_URL}/api/drive?${query}`
          : `${API_URL}/api/drive`;


      const response = await fetch(
        url,
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
          "Could not load files"
        );

      }


      const data =
        await response.json();


      setFiles(
        data.files || []
      );


    } catch (err) {

      console.error(err);

      setError(
        "Manager X could not load your files."
      );

    } finally {

      setLoading(false);

    }

  }


  // =====================================================
  // LOAD WHEN CATEGORY CHANGES
  // =====================================================

  useEffect(() => {

    loadFiles();

  }, [category]);


  // =====================================================
  // FORMAT CATEGORY
  // =====================================================

  function formatCategory(value) {

    const categories = {

      contract:
        "Contract",

      invoice:
        "Invoice",

      media_kit:
        "Media Kit",

      sponsor_asset:
        "Sponsor Asset",

      other:
        "Other"

    };


    return (
      categories[value] ||
      "Other"
    );

  }


  // =====================================================
  // FORMAT FILE TYPE
  // =====================================================

  function formatFileType(
    mimeType
  ) {

    if (!mimeType) {
      return "File";
    }


    if (
      mimeType.includes(
        "pdf"
      )
    ) {
      return "PDF";
    }


    if (
      mimeType.includes(
        "spreadsheet"
      )
    ) {
      return "Spreadsheet";
    }


    if (
      mimeType.includes(
        "document"
      )
    ) {
      return "Document";
    }


    if (
      mimeType.includes(
        "presentation"
      )
    ) {
      return "Presentation";
    }


    if (
      mimeType.includes(
        "image"
      )
    ) {
      return "Image";
    }


    if (
      mimeType.includes(
        "folder"
      )
    ) {
      return "Folder";
    }


    return "File";

  }


  // =====================================================
  // FORMAT DATE
  // =====================================================

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
        day: "numeric",
        year: "numeric"
      }
    );

  }


  // =====================================================
  // SUMMARY
  // =====================================================

  const contracts =
    files.filter(
      (file) =>
        file.category ===
        "contract"
    ).length;


  const invoices =
    files.filter(
      (file) =>
        file.category ===
        "invoice"
    ).length;


  const sponsorAssets =
    files.filter(
      (file) =>
        file.category ===
        "sponsor_asset"
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

              Drive

            </h1>


            <p className="manager-muted mt-2">

              Important creator files,
              already organized.

            </p>

          </div>


          <button
            onClick={loadFiles}
            className="manager-button-secondary"
          >

            Refresh files

          </button>

        </header>


        {/* =================================================
            SUMMARY
        ================================================= */}

        <section className="grid sm:grid-cols-4 gap-4 mt-8">


          <SummaryCard
            value={files.length}
            label="Files"
          />


          <SummaryCard
            value={contracts}
            label="Contracts"
          />


          <SummaryCard
            value={invoices}
            label="Invoices"
          />


          <SummaryCard
            value={sponsorAssets}
            label="Sponsor assets"
          />


        </section>


        {/* =================================================
            CATEGORY FILTER
        ================================================= */}

        <section className="mt-6 flex flex-wrap gap-2">


          <FilterButton
            active={
              category === ""
            }
            onClick={
              () =>
                setCategory("")
            }
          >
            All
          </FilterButton>


          <FilterButton
            active={
              category ===
              "contract"
            }
            onClick={
              () =>
                setCategory(
                  "contract"
                )
            }
          >
            Contracts
          </FilterButton>


          <FilterButton
            active={
              category ===
              "invoice"
            }
            onClick={
              () =>
                setCategory(
                  "invoice"
                )
            }
          >
            Invoices
          </FilterButton>


          <FilterButton
            active={
              category ===
              "media_kit"
            }
            onClick={
              () =>
                setCategory(
                  "media_kit"
                )
            }
          >
            Media Kit
          </FilterButton>


          <FilterButton
            active={
              category ===
              "sponsor_asset"
            }
            onClick={
              () =>
                setCategory(
                  "sponsor_asset"
                )
            }
          >
            Sponsor Assets
          </FilterButton>


          <FilterButton
            active={
              category ===
              "other"
            }
            onClick={
              () =>
                setCategory(
                  "other"
                )
            }
          >
            Other
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
            FILES
        ================================================= */}

        <section className="manager-card mt-5 overflow-hidden">


          <div className="px-6 py-5 border-b border-neutral-100 flex items-center justify-between">

            <div>

              <p className="manager-label">
                Files
              </p>

              <p className="text-sm manager-muted mt-1">

                {category
                  ? formatCategory(
                      category
                    )
                  : "All organized files"
                }

              </p>

            </div>


            <span className="text-sm manager-muted">

              {files.length}

            </span>

          </div>


          {loading ? (

            <div className="manager-empty">

              <div className="manager-loading" />

              <p className="text-sm mt-4">

                Organizing your files...

              </p>

            </div>

          ) : files.length === 0 ? (

            <div className="manager-empty">

              <p className="font-medium text-neutral-950">

                No files here yet.

              </p>

              <p className="text-sm mt-2 max-w-md">

                Manager X will surface
                contracts, invoices,
                media kits and sponsor
                assets when they appear
                in your connected Drive.

              </p>

            </div>

          ) : (

            <div>

              {files.map(
                (file, index) => (

                  <div
                    key={file.id}
                  >

                    <FileRow
                      file={file}
                      formatCategory={
                        formatCategory
                      }
                      formatFileType={
                        formatFileType
                      }
                      formatDate={
                        formatDate
                      }
                    />


                    {index <
                      files.length -
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

                Stop searching through Drive.

              </p>

              <p className="text-sm manager-muted mt-2 leading-relaxed max-w-2xl">

                Manager X identifies the
                creator files that matter
                and keeps contracts,
                invoices, media kits and
                sponsor assets easy to find.

              </p>

            </div>

          </div>

        </section>

      </div>

    </main>

  );

}


// =========================================================
// FILE ROW
// =========================================================

function FileRow({
  file,
  formatCategory,
  formatFileType,
  formatDate
}) {

  return (

    <div className="px-5 md:px-6 py-5 flex flex-col md:flex-row md:items-center justify-between gap-5">


      {/* LEFT */}

      <div className="flex items-start gap-4 min-w-0">


        {/* FILE ICON */}

        <div className="w-11 h-11 rounded-xl bg-neutral-100 flex items-center justify-center flex-shrink-0">

          <FileIcon />

        </div>


        <div className="min-w-0">

          <p className="font-medium truncate">

            {file.name ||
              "Untitled file"}

          </p>


          <div className="flex flex-wrap gap-x-3 gap-y-1 mt-2 text-xs manager-muted">

            <span>

              {formatCategory(
                file.category
              )}

            </span>

            <span>
              •
            </span>

            <span>

              {formatFileType(
                file.file_type
              )}

            </span>


            {file.created_at && (

              <>

                <span>
                  •
                </span>

                <span>

                  {formatDate(
                    file.created_at
                  )}

                </span>

              </>

            )}

          </div>


          {file.deal_id && (

            <p className="text-xs manager-muted mt-2">

              Attached to deal #
              {file.deal_id}

            </p>

          )}

        </div>

      </div>


      {/* RIGHT */}

      {file.drive_url ? (

        <a
          href={
            file.drive_url
          }
          target="_blank"
          rel="noreferrer"
          className="manager-button-secondary whitespace-nowrap"
        >

          Open file

        </a>

      ) : (

        <span className="text-sm manager-subtle">

          Link unavailable

        </span>

      )}

    </div>

  );

}


// =========================================================
// FILE ICON
// =========================================================

function FileIcon() {

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

      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />

      <polyline points="14 2 14 8 20 8" />

    </svg>

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