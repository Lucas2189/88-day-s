"use client";

export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <html lang="en">
      <body style={{ background: "#000", color: "#f5f5f7", fontFamily: "system-ui", display: "grid", placeItems: "center", minHeight: "100dvh", margin: 0 }}>
        <div style={{ textAlign: "center", padding: 32 }}>
          <h1 style={{ fontSize: 22, marginBottom: 8 }}>SCROLL hit a fatal error</h1>
          <p style={{ opacity: 0.7, fontSize: 14 }}>{error.message}</p>
          <button onClick={reset} style={{ marginTop: 16, background: "#fff", color: "#000", border: 0, borderRadius: 999, padding: "10px 20px", fontWeight: 600 }}>
            Reload
          </button>
        </div>
      </body>
    </html>
  );
}
