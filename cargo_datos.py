import pandas as pd
import psycopg2
from psycopg2 import sql
from datetime import datetime

# Carga los CSV
csv_prestamos = r'C:\Users\augus\Downloads\Proyecto Datos 1\prestamos - prestamos.csv'
csv_pagos_realizados = r'C:\Users\augus\Downloads\Proyecto Datos 1\pagos_realizados - pagos_realizados.csv'

df_prestamos = pd.read_csv(csv_prestamos)
df_pagos_realizados = pd.read_csv(csv_pagos_realizados)

# Maneja valores NaN
df_prestamos = df_prestamos.fillna('')
df_pagos_realizados = df_pagos_realizados.fillna('')

# Limpia los valores monetarios de las columnas correspondientes
columnas_monetarias = ['monto_solicitado', 'prestamo_total']  # Agrega otras columnas monetarias si las hay
for columna in columnas_monetarias:
    df_prestamos[columna] = df_prestamos[columna].replace({r'\$': '', ',': ''}, regex=True).astype(float)


# Conexión a PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="mydb",
    user="augus",
    password="password"
)
cursor = conn.cursor()

def insert_roles():
    roles = ['admin', 'cliente', 'analista']
    for role in roles:
        cursor.execute("SELECT id FROM catalogo_roles WHERE nombre = %s", (role,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO catalogo_roles (nombre) VALUES (%s)", (role,))
    conn.commit()

def get_role_id(role_name):
    cursor.execute("SELECT id FROM catalogo_roles WHERE nombre = %s", (role_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        raise ValueError(f"Role '{role_name}' not found in catalogo_roles")
def get_or_create_cuota_status(type_value):
    # Asegúrate de que el estado de la cuota existe o se crea si no existe
    query = sql.SQL("""
    INSERT INTO cuota_status (type)
    VALUES (%s)
    ON CONFLICT (type) DO NOTHING
    RETURNING id
    """)
    cursor.execute(query, (type_value,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    else:
        # Si no retorna resultado, lo buscamos
        cursor.execute("SELECT id FROM cuota_status WHERE type = %s", (type_value,))
        return cursor.fetchone()[0]


def insert_cuotas(row, prestamo_id, usuario_id):
    for i in range(1, 13):
        fecha_esperada = row.get(f'pago{i}_fecha_esperada')
        
        # Si la fecha es una cadena vacía o NaN, se asigna None
        if not fecha_esperada or pd.isna(fecha_esperada):
            fecha_esperada = None
        else:
            # Asegurarse de que sea una fecha válida para PostgreSQL
            try:
                fecha_esperada = pd.to_datetime(fecha_esperada).date()
            except ValueError:
                fecha_esperada = None

        # Inserta la cuota incluso si la fecha es None (NULL en la base de datos)
        query = sql.SQL("""
        INSERT INTO cuotas (prestamo_id, usuario_id, cuota_status_id, numero_cuota, 
                            amount_to_pay, date_to_pay)
        VALUES (%s, %s, %s, %s, %s, %s)
        """)
        cuota_status_id = get_or_create_cuota_status('pendiente')  # Asegúrate de que este valor exista
        amount_to_pay = row['prestamo_total'] / row['cuotas_pactadas']
        
        cursor.execute(query, (prestamo_id, usuario_id, cuota_status_id, i, amount_to_pay, fecha_esperada))





def insert_usuario(row):
    query = sql.SQL("""
    INSERT INTO usuario (username, password, nombre, email, telefono, fecha_nacimiento, role_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """)
    username = f"{row['codigo_cliente']}_{row['cliente_primer_nombre'].lower()}"
    password = "password_temporal"
    nombre = f"{row['cliente_primer_nombre']} {row['cliente_segundo_nombre']} {row['cliente_primer_apellido']} {row['cliente_segundo_apellido']}"
    nombre = ' '.join(nombre.split())  # Elimina espacios extras
    email = f"{username}@email.com"  # Placeholder
    telefono = ""
    fecha_nacimiento = row['fecha_nacimiento']
    role_id = get_role_id('cliente')

    cursor.execute(query, (username, password, nombre, email, telefono, fecha_nacimiento, role_id))
    return cursor.fetchone()[0]

def insert_cliente(row, usuario_id):
    query = sql.SQL("""
    INSERT INTO cliente (usuario_id, dpi, estado_civil_id, direccion_casa_id, ingresos_estimados)
    VALUES (%s, %s, %s, %s, %s)
    """)
    dpi = row['cui']
    estado_civil_id = get_estado_civil_id(row['estado_civil'])
    direccion_casa_id = get_or_create_direccion(row['vecindad'])
    ingresos_estimados = 0

    cursor.execute(query, (usuario_id, dpi, estado_civil_id, direccion_casa_id, ingresos_estimados))

def get_or_create_direccion(direccion):
    query = sql.SQL("""
    INSERT INTO catalogo_direcciones (direccion)
    VALUES (%s)
    ON CONFLICT (direccion) DO UPDATE SET direccion = EXCLUDED.direccion
    RETURNING id
    """)
    cursor.execute(query, (direccion,))
    return cursor.fetchone()[0]

def get_estado_civil_id(estado_civil):
    query = sql.SQL("""
    SELECT id FROM catalogo_estado_civil WHERE estado = %s
    """)
    cursor.execute(query, (estado_civil,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        insert_query = sql.SQL("""
        INSERT INTO catalogo_estado_civil (estado)
        VALUES (%s)
        RETURNING id
        """)
        cursor.execute(insert_query, (estado_civil,))
        return cursor.fetchone()[0]

def insert_prestamo(row, usuario_id):
    query = sql.SQL("""
    INSERT INTO prestamo (usuario_id, prestamo_status_id, monto_solicitado, total_to_pay, 
                          interest_rate, amount_cuotas, date_requested, razon_prestamo_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """)
    prestamo_status_id = get_or_create_prestamo_status(row['prestamo_estatus'])
    monto_solicitado = row['monto_solicitado']
    total_to_pay = row['prestamo_total']
    interest_rate = row['porcentaje_interes']
    amount_cuotas = row['cuotas_pactadas']
    date_requested = datetime.now().date()
    razon_prestamo_id = get_or_create_razon_prestamo(row['motivo_prestamo'])

    cursor.execute(query, (usuario_id, prestamo_status_id, monto_solicitado, total_to_pay,
                           interest_rate, amount_cuotas, date_requested, razon_prestamo_id))
    return cursor.fetchone()[0]

def get_or_create_prestamo_status(status):
    query = sql.SQL("""
    INSERT INTO prestamo_status (type)
    VALUES (%s)
    ON CONFLICT (type) DO UPDATE SET type = EXCLUDED.type
    RETURNING id
    """)
    cursor.execute(query, (status,))
    return cursor.fetchone()[0]

def get_or_create_razon_prestamo(razon):
    query = sql.SQL("""
    INSERT INTO catalogo_razon_prestamo (razon)
    VALUES (%s)
    ON CONFLICT (razon) DO UPDATE SET razon = EXCLUDED.razon
    RETURNING id
    """)
    cursor.execute(query, (razon,))
    return cursor.fetchone()[0]

def insert_cuotas(row, prestamo_id, usuario_id):
    for i in range(1, 13):
        fecha_esperada = row.get(f'pago{i}_fecha_esperada')
        if pd.notna(fecha_esperada):  # Solo inserta si la fecha no es NaN
            query = sql.SQL("""
            INSERT INTO cuotas (prestamo_id, usuario_id, cuota_status_id, numero_cuota, 
                                amount_to_pay, date_to_pay)
            VALUES (%s, %s, %s, %s, %s, %s)
            """)
            cuota_status_id = 1
            amount_to_pay = row['prestamo_total'] / row['cuotas_pactadas']
            cursor.execute(query, (prestamo_id, usuario_id, cuota_status_id, i, amount_to_pay, fecha_esperada))


insert_roles()

for _, row in df_prestamos.iterrows():
    try:
        usuario_id = insert_usuario(row)
        insert_cliente(row, usuario_id)
        prestamo_id = insert_prestamo(row, usuario_id)
        insert_cuotas(row, prestamo_id, usuario_id)
        conn.commit()  # Confirmar cada fila insertada
    except Exception as e:
        conn.rollback()  # En caso de error, revertir los cambios de esa fila
        print(f"Error procesando fila de préstamo: {e}")
        print(f"Fila con error: {row}")

cursor.close()
conn.close()

print("Proceso de carga de datos completado.")
