# ERD schema model

Prepare one UTF-8 JSON object for `scripts/render_erd.py`. Array order controls the rendered group, table, column, constraint, and relationship order.

## Example

```json
{
  "title": "Order service schema",
  "subtitle": "Tables involved in order creation and fulfilment.",
  "version": "release/2.4",
  "sources": ["db/migration/V001__orders.sql"],
  "groups": [
    {"id": "orders", "label": "Orders", "description": "Transactional data"}
  ],
  "tables": [
    {
      "id": "orders",
      "name": "sales.orders",
      "group": "orders",
      "columns": [
        {"name": "tenant_id", "type": "uuid", "nullable": false, "primaryKey": true},
        {"name": "id", "type": "uuid", "nullable": false, "primaryKey": true}
      ],
      "constraints": [
        {"kind": "primary-key", "columns": ["tenant_id", "id"], "text": "PRIMARY KEY (tenant_id, id)"}
      ]
    },
    {
      "id": "order_items",
      "name": "sales.order_items",
      "group": "orders",
      "columns": [
        {"name": "tenant_id", "type": "uuid", "nullable": false},
        {"name": "order_id", "type": "uuid", "nullable": false}
      ]
    }
  ],
  "relationships": [
    {
      "id": "order_items_order",
      "from": {"table": "order_items", "columns": ["tenant_id", "order_id"], "cardinality": "0..*"},
      "to": {"table": "orders", "columns": ["tenant_id", "id"], "cardinality": "1"},
      "enforcement": "foreign-key",
      "onDelete": "CASCADE"
    }
  ]
}
```

## Contract

### Root and groups

- `title`, `groups`, `tables`, and `relationships` are required. `subtitle`, `version`, and string-array `sources` are optional.
- IDs must be unique within their collection.
- A group requires `id` and `label`; `description` is optional. Every table references one group.

### Tables

- `id`, `name`, `group`, and a non-empty `columns` array are required.
- `existing` defaults to `false`. Use it for referenced tables outside the requested or proposed scope.
- `note`, `source`, and `constraints` are optional.
- A column requires `name` and `type`. `nullable` defaults to `true`; `primaryKey` and `unique` default to `false`. Primary-key columns are normalized to non-null.
- A constraint requires `kind` and `text`. Kinds are `primary-key`, `unique`, `check`, `index`, `exclusion`, and `invariant`.
- A `primary-key` or `unique` constraint requires an ordered `columns` array. The renderer uses it to verify foreign-key targets.
- Column-level `primaryKey` and `unique` flags remain useful for single-column keys and visual markers.
- Express multi-column primary and unique constraints in `constraints`; never mark each component as individually unique.

## Relationships

- `id`, `from`, `to`, and `enforcement` are required.
- Both endpoints require `table`, a non-empty `columns` array, and `cardinality`.
- Source and target column arrays must have equal length. Position defines each column mapping.
- An enforced foreign key's ordered target tuple must match a declared primary or unique key.
- Cardinalities are `0..1`, `1`, `0..*`, `1..*`, and `unknown`.
- `enforcement` is `foreign-key`, `logical`, or `derived`.
- `onDelete` and `onUpdate` apply only to `foreign-key` relationships. Preserve the source action rather than assuming a database default.
- `label`, `note`, and `source` are optional.
- Cardinality describes how many rows may occur at that endpoint for one row at the opposite endpoint.
- Confirm it from constraints and domain rules; use `unknown` when the source does not establish it.
