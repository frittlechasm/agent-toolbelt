CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE
);

CREATE TABLE users (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL,
    email VARCHAR(320) NOT NULL,
    PRIMARY KEY (tenant_id, id),
    UNIQUE (tenant_id, email),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE RESTRICT
);

CREATE TABLE products (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL,
    sku VARCHAR(80) NOT NULL,
    replacement_product_id UUID,
    PRIMARY KEY (tenant_id, id),
    UNIQUE (tenant_id, sku),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE RESTRICT,
    FOREIGN KEY (tenant_id, replacement_product_id)
        REFERENCES products(tenant_id, id) ON DELETE NO ACTION
);

CREATE TABLE orders (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL,
    customer_id UUID NOT NULL,
    status VARCHAR(24) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (tenant_id, id),
    FOREIGN KEY (tenant_id, customer_id)
        REFERENCES users(tenant_id, id) ON DELETE RESTRICT,
    CHECK (status IN ('PENDING', 'PAID', 'CANCELLED'))
);

CREATE TABLE order_items (
    tenant_id UUID NOT NULL,
    order_id UUID NOT NULL,
    line_number INTEGER NOT NULL,
    product_id UUID NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (tenant_id, order_id, line_number),
    FOREIGN KEY (tenant_id, order_id)
        REFERENCES orders(tenant_id, id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id, product_id)
        REFERENCES products(tenant_id, id) ON DELETE RESTRICT,
    CHECK (quantity > 0)
);

CREATE TABLE fulfilment_events (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    order_id UUID NOT NULL,
    provider_reference VARCHAR(200) NOT NULL,
    payload JSONB NOT NULL,
    received_at TIMESTAMPTZ NOT NULL,
    UNIQUE (tenant_id, provider_reference),
    FOREIGN KEY (tenant_id, order_id)
        REFERENCES orders(tenant_id, id) ON DELETE CASCADE
);
