const API_URL = "http://127.0.0.1:8000";

async function request(path, { method = "GET", body, userId } = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      "X-User-Id": String(userId),
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const data = await response.json();
      if (typeof data.detail === "string") {
        detail = data.detail;
      }
    } catch {
      // The response was not JSON; keep the status message.
    }
    throw new Error(detail);
  }

  return response.json();
}

export function createSubmission(userId, payload) {
  return request("/api/submissions", { method: "POST", body: payload, userId });
}

export function listSubmissions(userId, status) {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return request(`/api/submissions${query}`, { userId });
}

export function decideSubmission(userId, submissionId, status, note) {
  return request(`/api/submissions/${submissionId}`, {
    method: "PATCH",
    body: { status, note: note || null },
    userId,
  });
}
