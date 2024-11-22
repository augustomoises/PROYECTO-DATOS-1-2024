import pandas as pd
import psycopg2

csv_file_path = r'PROYECTO FINAL\prestamos.csv'
data_prestamos = pd.read_csv(csv_file_path)
df = pd.read_csv(csv_file_path)

data_prestamos = df[['cliente_id','codigo_cliente','cliente_primer_nombre','cliente_segundo_nombre','cliente_tercer_nombre','cliente_primer_apellido','cliente_segundo_apellido','apellido_casada','genero','cui','depto_nacimiento','muni_nacimiento','vecindad','estado_civil','nacionalidad','ocupacion','fecha_nacimiento','fecha_vencimiento_dpi','prestamo_id','codigo_prestamo','monto_solicitado','cuotas_pactadas','porcentaje_interes','prestamo_iva','prestamo_cargos_administrativos','prestamo_total','motivo_prestamo','prestamo_estatus','referencia1_primer_nombre','referencia1_segundo_nombre','referencia1_tercer_nombre','referencia1_primer_apellido','referencia1_segundo_apellido','referencia1_telefono','referencia2_primer_nombre','referencia2_segundo_nombre','referencia2_tercer_nombre','referencia2_primer_apellido','referencia2_segundo_apellido','referencia2_telefono','referencia3_primer_nombre','referencia3_segundo_nombre','referencia3_tercer_nombre','referencia3_primer_apellido','referencia3_segundo_apellido','referencia3_telefono','referencia4_primer_nombre','referencia4_segundo_nombre','referencia4_tercer_nombre','referencia4_primer_apellido','referencia4_segundo_apellido','referencia4_telefono','pago1_fecha_esperada','pago2_fecha_esperada','pago3_fecha_esperada','pago4_fecha_esperada','pago5_fecha_esperada','pago6_fecha_esperada','pago7_fecha_esperada','pago8_fecha_esperada','pago9_fecha_esperada','pago10_fecha_esperada','pago11_fecha_esperada','pago12_fecha_esperada']].drop_duplicates().dropna(subset=['cliente_segundo_nombre','cliente_tercer_nombre','apellido_casada','referencia1_segundo_nombre','referencia1_tercer_nombre','referencia2_segundo_nombre','referencia2_tercer_nombre','referencia3_segundo_nombre','referencia3_tercer_nombre','referencia4_segundo_nombre','referencia4_tercer_nombre','pago3_fecha_esperada','pago4_fecha_esperada','pago5_fecha_esperada','pago6_fecha_esperada','pago7_fecha_esperada','pago8_fecha_esperada','pago9_fecha_esperada','pago10_fecha_esperada','pago11_fecha_esperada','pago12_fecha_esperada'])

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="test",
    user="test",
    password="test123"
)

cursor = conn.cursor()

for index, row in data_prestamos.iterrows():
    codigo_cliente = row['codigo_cliente']
    nombres = [row['cliente_primer_nombre'], row['cliente_segundo_nombre'], row['cliente_tercer_nombre']]
    apellidos = [row['cliente_primer_apellido'], row['cliente_segundo_apellido'], row['apellido_casada']]
    genero = row['genero']
    cui = row['cui']
    direccion = [row['vecindad']]
    estado_civil = row['estado_civil']
    ocupacion = row['ocupacion']

    codigo_prestamo = row['codigo_prestamo']
    monto_solicitado = row['monto_solicitado']
    cuotas_pactadas = row['cuotas_pactadas']
    porcentaje_interes = row['porcentaje_interes']
    prestamo_iva = row['prestamo_iva']
    prestamo_cargos_administrativos = row['prestamo_cargos_administrativos']
    prestamo_total = row['prestamo_total']
    motivo_prestamo = row['motivo_prestamo']
    prestamo_estatus = row['prestamo_estatus']


    nombres_referencia1 = [row['referencia1_primer_nombre'], row['referencia1_segundo_nombre'], row['referencia1_tercer_nombre']]
    apellidos_referencia1 = [row['referencia1_primer_apellido'], row['referencia1_segundo_apellido']]
    telefono_referencia1 = row['referencia1_telefono']

    nombres_referencia2 = [row['referencia2_primer_nombre'], row['referencia2_segundo_nombre'], row['referencia2_tercer_nombre']]
    apellidos_referencia2 = [row['referencia2_primer_apellido'], row['referencia2_segundo_apellido']]
    telefono_referencia2 = row['referencia2_telefono']

    nombres_referencia3 = [row['referencia3_primer_nombre'], row['referencia3_segundo_nombre'], row['referencia3_tercer_nombre']]
    apellidos_referencia3 = [row['referencia3_primer_apellido'], row['referencia3_segundo_apellido']]
    telefono_referencia3 = row['referencia3_telefono']

    nombres_referencia4 = [row['referencia4_primer_nombre'], row['referencia4_segundo_nombre'], row['referencia4_tercer_nombre']]
    apellidos_referencia4 = [row['referencia4_primer_apellido'], row['referencia4_segundo_apellido']]
    telefono_referencia4 = row['referencia4_telefono']

    fecha_pago1 = row['pago1_fecha_esperada']
    fecha_pago2 = row['pago2_fecha_esperada']
    fecha_pago3 = row['pago3_fecha_esperada']
    fecha_pago4 = row['pago4_fecha_esperada']
    fecha_pago5 = row['pago5_fecha_esperada']
    fecha_pago6 = row['pago6_fecha_esperada']
    fecha_pago7 = row['pago7_fecha_esperada']
    fecha_pago8 = row['pago8_fecha_esperada']
    fecha_pago9 = row['pago9_fecha_esperada']
    fecha_pago10 = row['pago10_fecha_esperada']
    fecha_pago11 = row['pago11_fecha_esperada']
    fecha_pago12 = row['pago12_fecha_esperada']


    try:
        cursor.execute("""INSERT INTO catalogo_genero (genero) VALUES (%s)""", (genero,))
        cursor.execute("""SELECT id FROM catalogo_genero WHERE genero = %s;""", (genero,))
        genero_id = cursor.fetchone()[0]

        cursor.execute("""INSERT INTO usuario (nombre, apellido, genero_id) VALUES (%s, %s, %s)""", (nombres,apellidos,genero_id))
        cursor.execute("""SELECT id FROM usuario;""")
        usuario_id = cursor.fetchone()[0]

        cursor.execute("""INSERT INTO catalogo_estado_civil (estado_civil) VALUES (%s)""", (estado_civil,))
        cursor.execute("""SELECT id FROM catalogo_estado_civil WHERE estado_civil = %s;""", (estado_civil,))
        estado_civil_id = cursor.fetchone()[0]

        cursor.execute("""INSERT INTO catalogo_direcciones (direccion) VALUES (%s)""", (direccion,))
        cursor.execute("""SELECT id FROM catalogo_direcciones WHERE direccion = cast(%s as text);""", (direccion,))
        direccion_id = cursor.fetchone()[0]

        cursor.execute("""INSERT INTO cliente (usuario_id, codigo_cliente, cui, estado_civil_id, direccion_id, ocupacion) VALUES (%s, %s, %s, %s, %s, %s)""", (usuario_id, codigo_cliente, cui, estado_civil_id, direccion_id, ocupacion))
        cursor.execute("""SELECT id FROM cliente""")
        cliente_id = cursor.fetchone()[0]

        cursor.execute("""INSERT INTO referencia (cliente_id, nombre, apellido, telefono) VALUES (%s, %s, %s, %s)""", (cliente_id, nombres_referencia1, apellidos_referencia1, telefono_referencia1))
        cursor.execute("""INSERT INTO referencia (cliente_id, nombre, apellido, telefono) VALUES (%s, %s, %s, %s)""", (cliente_id, nombres_referencia2, apellidos_referencia2, telefono_referencia2))
        cursor.execute("""INSERT INTO referencia (cliente_id, nombre, apellido, telefono) VALUES (%s, %s, %s, %s)""", (cliente_id, nombres_referencia3, apellidos_referencia3, telefono_referencia3))
        cursor.execute("""INSERT INTO referencia (cliente_id, nombre, apellido, telefono) VALUES (%s, %s, %s, %s)""", (cliente_id, nombres_referencia4, apellidos_referencia4, telefono_referencia4))

        # ------------------------------------

        cursor.execute("""INSERT INTO prestamo (codigo_prestamo, usuario_id, monto_solicitado, cuotas_patadas, porcentaje_interes, prestamo_iva, prestamo_cargos_administrativos, prestamo_total, razon_prestamo, prestamo_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (codigo_prestamo, usuario_id, monto_solicitado, cuotas_pactadas, porcentaje_interes, prestamo_iva, prestamo_cargos_administrativos, prestamo_total, motivo_prestamo, prestamo_estatus))



        cursor.execute("""INSERT INTO catalogo_prestamo_status (descripcion) VALUES (%s)""", (prestamo_estatus,))
        cursor.execute("""SELECT id FROM catalogo_prestamo_status WHERE descripcion = %s;""", (prestamo_estatus,))
        catalogo_prestamo_status_id = cursor.fetchone()[0]

        cursor.execute("""INSERT INTO prestamo_status (status_id) VALUES (%s)""", (catalogo_prestamo_status_id,))

    except Exception as e:
        print(f"Error insertando datos: {e}")
        conn.rollback()
    else:
        conn.commit()

cursor.close()
conn.close()