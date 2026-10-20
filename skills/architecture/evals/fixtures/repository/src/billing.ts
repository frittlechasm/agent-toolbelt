import { pool } from "./storage";

export async function chargeOrder(orderId, userId) {
  const order = await pool.query("select * from orders where id = $1 and user_id = $2", [orderId, userId]);
  if (!order.rowCount) throw new Error("order_not_found");
  const response = await fetch(`${process.env.ACMEPAY_URL}/charges`, {
    method: "POST",
    headers: {
      authorization: `Bearer ${process.env.ACMEPAY_TOKEN}`,
      "content-type": "application/json",
      "idempotency-key": orderId,
    },
    body: JSON.stringify({ orderId, amount: order.rows[0].total }),
  });
  if (!response.ok) throw new Error("charge_failed");
  await pool.query("update orders set status = 'paid' where id = $1", [orderId]);
  return response.json();
}
