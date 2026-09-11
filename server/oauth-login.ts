import type { Express, Request, Response } from "express";
import { createHmac, randomBytes, timingSafeEqual, verify } from "node:crypto";

type Provider = "google" | "apple";
type Claims = { sub: string; email?: string; name?: string; nonce?: string; iss?: string; aud?: string | string[]; exp?: number };
type Jwk = JsonWebKey & { kid?: string };

const COOKIE_STATE = "buddy_oauth_state";
const COOKIE_SESSION = "buddy_auth_session";
const maxSessionSeconds = 8 * 60 * 60;
const providerConfig = {
  google: {
    clientId: () => process.env.GOOGLE_OAUTH_CLIENT_ID,
    clientSecret: () => process.env.GOOGLE_OAUTH_CLIENT_SECRET,
    authorize: "https://accounts.google.com/o/oauth2/v2/auth",
    token: "https://oauth2.googleapis.com/token",
    jwks: "https://www.googleapis.com/oauth2/v3/certs",
    issuer: "https://accounts.google.com",
    scope: "openid email profile",
  },
  apple: {
    clientId: () => process.env.APPLE_OAUTH_CLIENT_ID,
    clientSecret: () => process.env.APPLE_OAUTH_CLIENT_SECRET,
    authorize: "https://appleid.apple.com/auth/authorize",
    token: "https://appleid.apple.com/auth/token",
    jwks: "https://appleid.apple.com/auth/keys",
    issuer: "https://appleid.apple.com",
    scope: "name email",
  },
} as const;

const base64Url = (value: Buffer | string) => Buffer.from(value).toString("base64url");
const parseJson = <T>(value: string) => JSON.parse(Buffer.from(value, "base64url").toString("utf8")) as T;
const secret = () => process.env.AUTH_SESSION_SECRET || "";
const sign = (value: string) => createHmac("sha256", secret()).update(value).digest("base64url");
const equal = (left: string, right: string) => {
  const a = Buffer.from(left), b = Buffer.from(right);
  return a.length === b.length && timingSafeEqual(a, b);
};
const seal = (payload: object) => { const value = base64Url(JSON.stringify(payload)); return `${value}.${sign(value)}`; };
const unseal = <T>(value?: string): T | undefined => {
  if (!value || !secret()) return undefined;
  const [body, signature, extra] = value.split(".");
  if (!body || !signature || extra || !equal(signature, sign(body))) return undefined;
  try { return parseJson<T>(body); } catch { return undefined; }
};
const cookies = (request: Request) => Object.fromEntries((request.headers.cookie || "").split(";").map((part) => part.trim().split(/=(.*)/s)).filter(([name]) => name));
const secure = () => process.env.NODE_ENV === "production" ? "; Secure" : "";
const setCookie = (response: Response, name: string, value: string, seconds: number) => response.append("Set-Cookie", `${name}=${value}; HttpOnly; SameSite=Lax; Path=/; Max-Age=${seconds}${secure()}`);
const clearCookie = (response: Response, name: string) => setCookie(response, name, "", 0);
const redirectBase = () => (process.env.OAUTH_REDIRECT_BASE_URL || "").replace(/\/$/, "");
const callback = (provider: Provider) => `${redirectBase()}/api/auth/${provider}/callback`;
const configured = (provider: Provider) => Boolean(secret() && redirectBase() && providerConfig[provider].clientId() && providerConfig[provider].clientSecret());

async function verifyIdToken(provider: Provider, idToken: string, nonce: string): Promise<Claims> {
  const [encodedHeader, encodedPayload, encodedSignature, extra] = idToken.split(".");
  if (!encodedHeader || !encodedPayload || !encodedSignature || extra) throw new Error("Malformed identity token.");
  const header = parseJson<{ alg?: string; kid?: string }>(encodedHeader);
  if (header.alg !== "RS256" || !header.kid) throw new Error("Unsupported identity-token signing algorithm.");
  const jwks = await fetch(providerConfig[provider].jwks).then(async (response) => {
    if (!response.ok) throw new Error("Identity-key service unavailable.");
    return response.json() as Promise<{ keys?: Jwk[] }>;
  });
  const key = jwks.keys?.find((item) => item.kid === header.kid && item.kty === "RSA");
  if (!key || !verify("RSA-SHA256", Buffer.from(`${encodedHeader}.${encodedPayload}`), { key, format: "jwk" }, Buffer.from(encodedSignature, "base64url"))) throw new Error("Identity-token signature did not verify.");
  const claims = parseJson<Claims>(encodedPayload);
  const audience = Array.isArray(claims.aud) ? claims.aud : [claims.aud];
  if (claims.iss !== providerConfig[provider].issuer || !audience.includes(providerConfig[provider].clientId()) || claims.nonce !== nonce || !claims.sub || !claims.exp || claims.exp <= Math.floor(Date.now() / 1000)) throw new Error("Identity-token claims did not verify.");
  return claims;
}

export function registerOAuthLoginRoutes(app: Express) {
  app.get("/api/auth/providers", (_request, response) => response.json({ providers: (Object.keys(providerConfig) as Provider[]).map((provider) => ({ provider, configured: configured(provider), callback_url: redirectBase() ? callback(provider) : null })), truth: "A provider is available only after its server-side credentials and exact callback URL are configured." }));

  app.get("/api/auth/:provider/start", (request, response) => {
    const provider = request.params.provider as Provider;
    if (!(provider in providerConfig)) return response.status(404).json({ error: "Unknown identity provider." });
    if (!configured(provider)) return response.status(503).json({ error: "This sign-in provider is not configured on the Buddy backend." });
    const state = base64Url(randomBytes(32)), nonce = base64Url(randomBytes(32));
    setCookie(response, COOKIE_STATE, seal({ provider, state, nonce, exp: Date.now() + 10 * 60 * 1000 }), 10 * 60);
    const query = new URLSearchParams({ client_id: providerConfig[provider].clientId()!, redirect_uri: callback(provider), response_type: "code", response_mode: "query", scope: providerConfig[provider].scope, state, nonce });
    response.redirect(`${providerConfig[provider].authorize}?${query}`);
  });

  app.get("/api/auth/:provider/callback", async (request, response) => {
    const provider = request.params.provider as Provider;
    const state = unseal<{ provider: Provider; state: string; nonce: string; exp: number }>(cookies(request)[COOKIE_STATE]);
    clearCookie(response, COOKIE_STATE);
    if (!(provider in providerConfig) || !configured(provider) || !state || state.provider !== provider || state.state !== request.query.state || state.exp < Date.now() || typeof request.query.code !== "string") return response.status(400).json({ error: "Sign-in could not be verified. Start again from Buddy." });
    try {
      const tokenRequest = new URLSearchParams({ grant_type: "authorization_code", code: request.query.code, redirect_uri: callback(provider), client_id: providerConfig[provider].clientId()!, client_secret: providerConfig[provider].clientSecret()! });
      const tokenResponse = await fetch(providerConfig[provider].token, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: tokenRequest });
      const tokens = await tokenResponse.json() as { id_token?: string };
      if (!tokenResponse.ok || !tokens.id_token) throw new Error("Provider did not return an identity token.");
      const claims = await verifyIdToken(provider, tokens.id_token, state.nonce);
      setCookie(response, COOKIE_SESSION, seal({ provider, sub: claims.sub, email: claims.email, name: claims.name, exp: Math.floor(Date.now() / 1000) + maxSessionSeconds }), maxSessionSeconds);
      response.redirect("/sign-in.html?status=success");
    } catch { response.redirect("/sign-in.html?status=failed"); }
  });

  app.get("/api/auth/session", (request, response) => {
    const session = unseal<{ provider: Provider; sub: string; email?: string; name?: string; exp: number }>(cookies(request)[COOKIE_SESSION]);
    if (!session || session.exp <= Math.floor(Date.now() / 1000)) return response.json({ authenticated: false });
    response.json({ authenticated: true, provider: session.provider, profile: { subject: session.sub, email: session.email, name: session.name } });
  });
  app.post("/api/auth/sign-out", (_request, response) => { clearCookie(response, COOKIE_SESSION); response.status(204).end(); });
}
