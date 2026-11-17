let pending: Promise<unknown> | undefined;

export function loadProfile() {
  return pending ??= fetch("/profile").then(response => response.json());
}

export function clearCache() {
  pending = undefined;
}
