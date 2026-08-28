import { createRemoteJWKSet, jwtVerify } from "jose";

const keys = createRemoteJWKSet(new URL(process.env.OIDC_JWKS_URL!));
export async function authenticate(req, res, next) {
  const token = req.headers.authorization?.replace(/^Bearer /, "");
  if (!token) return res.status(401).json({ error: "missing_token" });
  try {
    const verified = await jwtVerify(token, keys, {
      issuer: process.env.OIDC_ISSUER,
      audience: "orders-api",
    });
    req.user = { id: verified.payload.sub, scopes: verified.payload.scope?.split(" ") ?? [] };
    next();
  } catch {
    res.status(401).json({ error: "invalid_token" });
  }
}

export const requireScope = (scope) => (req, res, next) =>
  req.user.scopes.includes(scope) ? next() : res.status(403).json({ error: "forbidden" });
