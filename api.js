const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:5000";


// =========================================================
// BASE REQUEST
// =========================================================

async function apiRequest(
  endpoint,
  options = {}
) {

  const url =
    `${API_URL}${endpoint}`;


  const config = {

    method:
      options.method || "GET",

    credentials:
      "include",

    headers: {
      ...(options.body
        ? {
            "Content-Type":
              "application/json"
          }
        : {}),
      ...(options.headers || {})
    }

  };


  // =====================================================
  // BODY
  // =====================================================

  if (
    options.body !== undefined
  ) {

    config.body =
      typeof options.body ===
      "string"
        ? options.body
        : JSON.stringify(
            options.body
          );

  }


  try {

    const response =
      await fetch(
        url,
        config
      );


    // ===================================================
    // NOT AUTHENTICATED
    // ===================================================

    if (
      response.status === 401
    ) {

      if (
        typeof window !==
        "undefined"
      ) {

        window.location.href =
          "/";

      }


      throw new Error(
        "Authentication required"
      );

    }


    // ===================================================
    // READ RESPONSE
    // ===================================================

    const contentType =
      response.headers.get(
        "content-type"
      );


    let data = null;


    if (
      contentType &&
      contentType.includes(
        "application/json"
      )
    ) {

      data =
        await response.json();

    } else {

      const text =
        await response.text();


      data =
        text
          ? {
              message: text
            }
          : {};

    }


    // ===================================================
    // API ERROR
    // ===================================================

    if (!response.ok) {

      const message =
        data?.error ||
        data?.message ||
        `Request failed (${response.status})`;


      throw new Error(
        message
      );

    }


    return data;


  } catch (error) {

    console.error(
      `API error: ${endpoint}`,
      error
    );


    throw error;

  }

}


// =========================================================
// AUTH
// =========================================================

export async function getCurrentUser() {

  return apiRequest(
    "/api/me"
  );

}


export function loginWithGoogle() {

  if (
    typeof window ===
    "undefined"
  ) {
    return;
  }


  window.location.href =
    `${API_URL}/auth/google`;

}


export async function logout() {

  const data =
    await apiRequest(
      "/api/logout",
      {
        method: "POST"
      }
    );


  if (
    typeof window !==
    "undefined"
  ) {

    window.location.href =
      "/";

  }


  return data;

}


// =========================================================
// MANAGER SYNC
// =========================================================

export async function runManager() {

  return apiRequest(
    "/api/sync",
    {
      method: "POST"
    }
  );

}


// =========================================================
// DASHBOARD
// =========================================================

export async function getDashboard() {

  return apiRequest(
    "/api/dashboard"
  );

}


// =========================================================
// INBOX
// =========================================================

export async function getInbox({
  category = "",
  priority = ""
} = {}) {

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


  return apiRequest(
    query
      ? `/api/inbox?${query}`
      : "/api/inbox"
  );

}


export async function markEmailRead(
  emailId
) {

  return apiRequest(
    `/api/inbox/${emailId}/read`,
    {
      method: "PATCH"
    }
  );

}


// =========================================================
// CRM / DEALS
// =========================================================

export async function getDeals() {

  return apiRequest(
    "/api/deals"
  );

}


export async function getDeal(
  dealId
) {

  return apiRequest(
    `/api/deals/${dealId}`
  );

}


// =========================================================
// TASKS
// =========================================================

export async function getTasks() {

  return apiRequest(
    "/api/tasks"
  );

}


export async function completeTask(
  taskId
) {

  return apiRequest(
    `/api/tasks/${taskId}/complete`,
    {
      method: "PATCH"
    }
  );

}


// =========================================================
// CALENDAR
// =========================================================

export async function getCalendar() {

  return apiRequest(
    "/api/calendar"
  );

}


// =========================================================
// DRIVE
// =========================================================

export async function getDriveFiles(
  category = ""
) {

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


  return apiRequest(
    query
      ? `/api/drive?${query}`
      : "/api/drive"
  );

}


// =========================================================
// FINANCE
// =========================================================

export async function getFinance() {

  return apiRequest(
    "/api/finance"
  );

}


// =========================================================
// HEALTH CHECK
// =========================================================

export async function checkBackend() {

  return apiRequest(
    "/api/health"
  );

}


// =========================================================
// EXPORT BASE URL
// =========================================================

export {
  API_URL
};