-- Tabla para roles de usuario
CREATE TABLE catalogo_roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR NOT NULL
);

-- Tabla de usuarios
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL UNIQUE,
    password VARCHAR NOT NULL,
    nombre VARCHAR NOT NULL,
    email VARCHAR UNIQUE,
    telefono VARCHAR,
    fecha_nacimiento DATE,
    role_id INT NOT NULL REFERENCES catalogo_roles(id)
);

-- Tabla para estados civiles
CREATE TABLE catalogo_estado_civil (
    id SERIAL PRIMARY KEY,
    estado VARCHAR NOT NULL
);

-- Catálogo de direcciones
CREATE TABLE catalogo_direcciones (
    id SERIAL PRIMARY KEY,
    direccion VARCHAR NOT NULL,
    descripcion VARCHAR
);

-- Tabla para clientes (extensión de usuario)
CREATE TABLE cliente (
    usuario_id INT PRIMARY KEY REFERENCES usuario(id),
    dpi VARCHAR NOT NULL UNIQUE,
    estado_civil_id INT NOT NULL REFERENCES catalogo_estado_civil(id),
    direccion_casa_id INT NOT NULL REFERENCES catalogo_direcciones(id),
    direccion_trabajo_id INT,
    ingresos_estimados DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Catálogo de tipos de analista
CREATE TABLE catalogo_tipo_analista (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR NOT NULL
);

-- Tabla para analistas (extensión de usuario)
CREATE TABLE analista (
    usuario_id INT PRIMARY KEY REFERENCES usuario(id),
    tipo_analista_id INT NOT NULL REFERENCES catalogo_tipo_analista(id)
);

-- Catálogo para razón de préstamo
CREATE TABLE catalogo_razon_prestamo (
    id SERIAL PRIMARY KEY,
    razon VARCHAR NOT NULL
);

-- Tabla para estados de préstamo
CREATE TABLE prestamo_status (
    id SERIAL PRIMARY KEY,
    type VARCHAR NOT NULL,
    description VARCHAR,
    date_accepted_rejected DATE,
    accepted_rejected_status VARCHAR,
    analyst_in_charge_id INT REFERENCES analista(usuario_id)
);

-- Tabla de préstamos con referencia a cliente(usuario_id)
CREATE TABLE prestamo (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL REFERENCES cliente(usuario_id),
    prestamo_status_id INT NOT NULL REFERENCES prestamo_status(id),
    monto_solicitado DECIMAL(15,2) NOT NULL,
    total_to_pay DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    amount_cuotas INT NOT NULL,
    date_requested DATE NOT NULL,
    razon_prestamo_id INT NOT NULL REFERENCES catalogo_razon_prestamo(id)
);

-- Tabla para estados de cuotas
CREATE TABLE cuota_status (
    id SERIAL PRIMARY KEY,
    type VARCHAR NOT NULL,
    description VARCHAR
);

-- Tabla de cuotas con referencia a cliente(usuario_id)
CREATE TABLE cuotas (
    id SERIAL PRIMARY KEY,
    prestamo_id INT NOT NULL REFERENCES prestamo(id),
    usuario_id INT NOT NULL REFERENCES cliente(usuario_id),
    cuota_status_id INT NOT NULL REFERENCES cuota_status(id),
    numero_cuota INT NOT NULL,
    amount_to_pay DECIMAL(15,2) NOT NULL,
    date_to_pay DATE NOT NULL,
    mora_amount DECIMAL(15,2) DEFAULT 0
);

-- Tabla para estados de comprobantes
CREATE TABLE comprobante_status (
    id SERIAL PRIMARY KEY,
    type VARCHAR NOT NULL,
    description VARCHAR
);

-- Tabla de comprobantes con referencia a cliente(usuario_id)
CREATE TABLE comprobante (
    id SERIAL PRIMARY KEY,
    cuotas_id INT NOT NULL REFERENCES cuotas(id),
    usuario_id INT NOT NULL REFERENCES cliente(usuario_id),
    comprobante_status_id INT NOT NULL REFERENCES comprobante_status(id),
    transaction_code VARCHAR UNIQUE NOT NULL,
    amount_payed DECIMAL(15,2) NOT NULL,
    date_payed DATE NOT NULL,
    description VARCHAR
);

-- Catálogo para tipos de referencia
CREATE TABLE catalogo_tipo_referencia (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR NOT NULL
);

-- Tabla de referencias 
CREATE TABLE referencia (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL REFERENCES cliente(usuario_id),
    tipo_referencia_id INT NOT NULL REFERENCES catalogo_tipo_referencia(id),
    nombre VARCHAR NOT NULL,
    email VARCHAR,
    telefono VARCHAR,
    relacion_con_cliente VARCHAR
);
