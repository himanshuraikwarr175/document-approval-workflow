import { useEffect, useState } from "react";
import { createSubmission, listSubmissions } from "../api";
import SubmissionList from "./SubmissionList";

const EMPTY_FORM = { title: "", body: "" };

export default function SubmitterView({ userId }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setSubmissions(await listSubmissions(userId));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [userId]);

  async function onSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      await createSubmission(userId, {
        title: form.title.trim(),
        body: form.body.trim(),
      });
      setForm(EMPTY_FORM);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="layout">
      <form className="card" onSubmit={onSubmit}>
        <h2>New submission</h2>
        <label>
          Title
          <input
            value={form.title}
            onChange={(event) => setForm({ ...form, title: event.target.value })}
            required
          />
        </label>
        <label>
          Document
          <textarea
            value={form.body}
            onChange={(event) => setForm({ ...form, body: event.target.value })}
            rows={6}
            required
          />
        </label>
        {error ? <p className="error">{error}</p> : null}
        <button type="submit" disabled={saving}>
          {saving ? "Submitting..." : "Submit for review"}
        </button>
      </form>
      <SubmissionList
        title="Your submissions"
        submissions={submissions}
        loading={loading}
        empty="You have not submitted a document yet."
      />
    </section>
  );
}
