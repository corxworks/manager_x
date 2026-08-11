"use client";

import { useEffect, useState } from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:5000";

export default function Sheets() {
  const [spreadsheetId, setSpreadsheetId] = useState("");
  const [range, setRange] = useState("Sheet1!A1:G20");

  const [rows, setRows] = useState([]);

  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

  const [title, setTitle] = useState(
    "Manager X Sheet"
  );

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");


  // =====================================================
  // LOAD SHEET
  // =====================================================

  async function loadSheet() {
    if (!spreadsheetId) {
      setError(
        "Enter a Google Spreadsheet ID first."
      );
      return;
    }

    try {
      setLoading(true);
      setError("");
      setMessage("");

      const response = await fetch(
        `${API_URL}/api/sheets/read?spreadsheet_id=${encodeURIComponent(
          spreadsheetId
        )}&range=${encodeURIComponent(range)}`,
        {
          method: "GET",
          credentials: "include",
        }
      );

      if (response.status === 401) {
        window.location.href = "/";
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error ||
            "Could not load spreadsheet."
        );
      }

      setRows(data.rows || []);

      setMessage(
        `${(data.rows || []).length} rows loaded.`
      );
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Could not load spreadsheet."
      );
    } finally {
      setLoading(false);
    }
  }


  // =====================================================
  // CREATE SPREADSHEET
  // =====================================================

  async function createSpreadsheet() {
    if (!title.trim()) {
      setError(
        "Enter a spreadsheet title."
      );
      return;
    }

    try {
      setCreating(true);
      setError("");
      setMessage("");

      const response = await fetch(
        `${API_URL}/api/sheets/create`,
        {
          method: "POST",
          credentials: "include",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            title: title.trim(),
          }),
        }
      );

      if (response.status === 401) {
        window.location.href = "/";
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error ||
            "Could not create spreadsheet."
        );
      }

      setSpreadsheetId(
        data.spreadsheet_id || ""
      );

      setMessage(
        "Spreadsheet created successfully."
      );
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Could not create spreadsheet."
      );
    } finally {
      setCreating(false);
    }
  }


  // =====================================================
  // APPEND ROW
  // =====================================================

  async function appendRow() {
    if (!spreadsheetId) {
      setError(
        "Enter or create a spreadsheet first."
      );
      return;
    }

    try {
      setLoading(true);
      setError("");
      setMessage("");

      const response = await fetch(
        `${API_URL}/api/sheets/append`,
        {
          method: "POST",
          credentials: "include",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            spreadsheet_id:
              spreadsheetId,

            range: range,

            values: [
              new Date().toLocaleString(),
              "Manager X",
              "Test row",
              "Working",
            ],
          }),
        }
      );

      if (response.status === 401) {
        window.location.href = "/";
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error ||
            "Could not append row."
        );
      }

      setMessage(
        "New row added successfully."
      );

      await loadSheet();
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Could not append row."
      );
    } finally {
      setLoading(false);
    }
  }


  // =====================================================
  // PAGE
  // =====================================================

  return (
    <main className="manager-app">

      <div className="manager-container py-8 md:py-10">

        {/* HEADER */}

        <header className="flex flex-col md:flex-row md:items-end md:justify-between gap-5">

          <div>

            <a
              href="/dashboard"
              className="text-sm manager-muted hover:text-neutral-950"
            >
              ← Dashboard
            </a>

            <h1 className="text-4xl font-semibold tracking-tight mt-4">
              Sheets
            </h1>

            <p className="manager-muted mt-2">
              Manage your Google Sheets from Manager X.
            </p>

          </div>

        </header>


        {/* CREATE */}

        <section className="manager-card p-6 mt-10">

          <p className="manager-label">
            Create spreadsheet
          </p>

          <h2 className="text-2xl font-semibold tracking-tight mt-2">
            Create a new Google Sheet
          </h2>

          <div className="flex flex-col md:flex-row gap-3 mt-5">

            <input
              value={title}
              onChange={(e) =>
                setTitle(e.target.value)
              }
              placeholder="Spreadsheet title"
              className="manager-input flex-1"
            />

            <button
              onClick={createSpreadsheet}
              disabled={creating}
              className="manager-button"
            >
              {creating
                ? "Creating..."
                : "Create sheet"}
            </button>

          </div>

        </section>


        {/* OPEN SHEET */}

        <section className="manager-card p-6 mt-5">

          <p className="manager-label">
            Spreadsheet
          </p>

          <h2 className="text-2xl font-semibold tracking-tight mt-2">
            Open a Google Sheet
          </h2>

          <div className="grid md:grid-cols-2 gap-3 mt-5">

            <input
              value={spreadsheetId}
              onChange={(e) =>
                setSpreadsheetId(
                  e.target.value
                )
              }
              placeholder="Google Spreadsheet ID"
              className="manager-input"
            />

            <input
              value={range}
              onChange={(e) =>
                setRange(e.target.value)
              }
              placeholder="Sheet1!A1:G20"
              className="manager-input"
            />

          </div>

          <div className="flex gap-3 mt-4">

            <button
              onClick={loadSheet}
              disabled={loading}
              className="manager-button"
            >
              {loading
                ? "Loading..."
                : "Load sheet"}
            </button>

            <button
              onClick={appendRow}
              disabled={loading}
              className="manager-button-secondary"
            >
              Add test row
            </button>

          </div>

        </section>


        {/* MESSAGE */}

        {message && (

          <div className="manager-card p-4 mt-5">

            <p className="text-sm">
              {message}
            </p>

          </div>

        )}


        {/* ERROR */}

        {error && (

          <div className="manager-card p-4 mt-5">

            <p className="text-sm text-red-600">
              {error}
            </p>

          </div>

        )}


        {/* DATA */}

        <section className="manager-card mt-5 overflow-hidden">

          <div className="p-6">

            <p className="manager-label">
              Sheet data
            </p>

            <h2 className="text-2xl font-semibold tracking-tight mt-2">
              Your spreadsheet
            </h2>

          </div>


          {rows.length === 0 ? (

            <div className="manager-empty">

              <p className="font-medium text-neutral-950">
                No sheet data loaded.
              </p>

              <p className="text-sm manager-muted mt-2">
                Create a sheet or enter an existing
                spreadsheet ID above.
              </p>

            </div>

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full text-sm">

                <tbody>

                  {rows.map(
                    (row, rowIndex) => (

                      <tr
                        key={rowIndex}
                        className="border-t border-neutral-200"
                      >

                        {row.map(
                          (cell, cellIndex) => (

                            <td
                              key={cellIndex}
                              className="px-5 py-4 whitespace-nowrap"
                            >
                              {cell}
                            </td>

                          )
                        )}

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            </div>

          )}

        </section>


        {/* INFO */}

        <section className="manager-card p-6 mt-5">

          <div className="flex items-start gap-4">

            <div className="manager-status-dot mt-1.5" />

            <div>

              <p className="font-medium">
                Sheets connected
              </p>

              <p className="text-sm manager-muted mt-2 leading-relaxed">
                Manager X can read spreadsheets,
                create spreadsheets and add rows
                using your Google account.
              </p>

            </div>

          </div>

        </section>

      </div>

    </main>
  );
}