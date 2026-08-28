create table orders (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  items jsonb not null,
  total integer not null check (total >= 0),
  status text not null check (status in ('pending', 'paid')),
  created_at timestamptz not null default now()
);
