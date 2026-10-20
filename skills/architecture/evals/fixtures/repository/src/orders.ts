import { pool } from "./storage";

export async function createOrder(userId, items) {
  const total = items.reduce((sum, item) => sum + item.unitPrice * item.quantity, 0);
  const result = await pool.query(
    "insert into orders(user_id, items, total, status) values ($1, $2, $3, 'pending') returning *",
    [userId, JSON.stringify(items), total],
  );
  return result.rows[0];
}
