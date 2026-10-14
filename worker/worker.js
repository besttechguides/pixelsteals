// PixelSteals signup worker (Cloudflare Workers, free tier).
// Secrets: RESEND_API_KEY (full access), SIGNING_SECRET. Vars: SITE_URL, FROM.
const enc = new TextEncoder();
async function sign(secret, msg) {
  const k = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const s = await crypto.subtle.sign("HMAC", k, enc.encode(msg));
  return [...new Uint8Array(s)].map(b => b.toString(16).padStart(2, "0")).join("").slice(0, 32);
}
const resend = (env, path, method, body) => fetch("https://api.resend.com" + path, {
  method, headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
  body: body ? JSON.stringify(body) : undefined });
const page = (env, title, msg) => new Response(
  `<!doctype html><meta name=viewport content="width=device-width,initial-scale=1"><title>${title}</title><body style="font:18px system-ui;background:#0b0d17;color:#e8ecff;text-align:center;padding:60px"><h1>${title}</h1><p>${msg}</p><p><a style="color:#7cf" href="${env.SITE_URL}">Back to PixelSteals</a></p>`,
  { headers: { "content-type": "text/html; charset=utf-8" } });
let ORIGIN = "";
const cors = env => ({ "Access-Control-Allow-Origin": (env.SITE_ORIGIN || "").split(",").map(x => x.trim()).includes(ORIGIN) ? ORIGIN : (env.SITE_ORIGIN || "").split(",")[0], "Vary": "Origin", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "content-type" });

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    ORIGIN = req.headers.get("Origin") || "";
    if (req.method === "OPTIONS") return new Response(null, { headers: cors(env) });

    if (url.pathname === "/subscribe" && req.method === "POST") {
      let email = "";
      try { email = String((await req.json()).email || "").trim().toLowerCase(); } catch {}
      const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { ...cors(env), "content-type": "application/json" } });
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || email.length > 254) return json({ ok: false, error: "Invalid email" }, 400);
      // Existing confirmed contact: say nothing different (avoid list enumeration).
      const existing = await resend(env, `/contacts/${encodeURIComponent(email)}`, "GET");
      if (existing.ok && (await existing.json()).unsubscribed === false) return json({ ok: true });
      if (!existing.ok) await resend(env, "/contacts", "POST", { email, unsubscribed: true }); // pending until confirmed
      const t = await sign(env.SIGNING_SECRET, "confirm:" + email);
      const link = `${url.origin}/confirm?e=${encodeURIComponent(email)}&t=${t}`;
      await resend(env, "/emails", "POST", {
        from: env.FROM, to: [email], subject: "Confirm your PixelSteals subscription",
        html: `<p>Hi! Tap below to confirm you want the daily PixelSteals email of free games and PC deals.</p><p><a href="${link}">Yes, subscribe me</a></p><p>If you didn't ask for this, ignore this email and you won't hear from us again.</p>`,
        text: `Confirm your PixelSteals subscription: ${link}\nIf you didn't ask for this, ignore this email.` });
      return json({ ok: true });
    }

    if (url.pathname === "/confirm" || url.pathname === "/unsubscribe") {
      const email = (url.searchParams.get("e") || "").toLowerCase(), t = url.searchParams.get("t") || "";
      const action = url.pathname.slice(1);
      if (!email || t !== await sign(env.SIGNING_SECRET, (action === "confirm" ? "confirm:" : "unsub:") + email))
        return page(env, "Link not valid", "This link is invalid or has expired.");
      // One-click unsubscribe (RFC 8058) POSTs here; GET shows a page.
      const r = await resend(env, `/contacts/${encodeURIComponent(email)}`, "PATCH", { unsubscribed: action !== "confirm" });
      if (!r.ok) return page(env, "Something went wrong", "Please try again later.");
      if (req.method === "POST") return new Response("ok");
      return action === "confirm"
        ? page(env, "You're in! 🎮", "Your first PixelSteals email arrives with the next daily drop.")
        : page(env, "Unsubscribed", "You won't get any more PixelSteals emails.");
    }
    return new Response("Not found", { status: 404 });
  }
};
