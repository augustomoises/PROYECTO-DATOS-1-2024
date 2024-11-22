from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, DECIMAL, Date, TIMESTAMP, Text, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import date, timedelta

DATABASE_URL = "postgresql+psycopg2://augus:password@localhost:5432/mydb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CatalogoRol(Base):
    __tablename__ = "catalogo_roles"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True)
    telefono = Column(String)
    fecha_nacimiento = Column(Date)
    role_id = Column(Integer, ForeignKey("catalogo_roles.id"), nullable=False)
    role = relationship("CatalogoRol")

class Cliente(Base):
    __tablename__ = "cliente"
    usuario_id = Column(Integer, ForeignKey("usuario.id"), primary_key=True)
    dpi = Column(String, unique=True, nullable=False)
    estado_civil_id = Column(Integer, ForeignKey("catalogo_estado_civil.id"), nullable=False)
    direccion_casa_id = Column(Integer, ForeignKey("catalogo_direcciones.id"), nullable=False)
    direccion_trabajo_id = Column(Integer, ForeignKey("catalogo_direcciones.id"))
    ingresos_estimados = Column(DECIMAL(15, 2))
    created_at = Column(TIMESTAMP)

class Prestamo(Base):
    __tablename__ = "prestamo"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("cliente.usuario_id"), nullable=False)
    prestamo_status_id = Column(Integer, ForeignKey("prestamo_status.id"), nullable=False)
    monto_solicitado = Column(DECIMAL(15, 2), nullable=False)
    total_to_pay = Column(DECIMAL(15, 2), nullable=False)
    interest_rate = Column(DECIMAL(5, 2), nullable=False)
    amount_cuotas = Column(Integer, nullable=False)
    date_requested = Column(Date, nullable=False)
    razon_prestamo_id = Column(Integer, ForeignKey("catalogo_razon_prestamo.id"), nullable=False)

class Cuota(Base):
    __tablename__ = "cuotas"
    id = Column(Integer, primary_key=True)
    prestamo_id = Column(Integer, ForeignKey("prestamo.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("cliente.usuario_id"), nullable=False)
    cuota_status_id = Column(Integer, ForeignKey("cuota_status.id"), nullable=False)
    numero_cuota = Column(Integer, nullable=False)
    amount_to_pay = Column(DECIMAL(15, 2), nullable=False)
    date_to_pay = Column(Date, nullable=False)
    mora_amount = Column(DECIMAL(15, 2), default=0)

class Comprobante(Base):
    __tablename__ = "comprobante"
    id = Column(Integer, primary_key=True)
    cuotas_id = Column(Integer, ForeignKey("cuotas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("cliente.usuario_id"), nullable=False)
    comprobante_status_id = Column(Integer, ForeignKey("comprobante_status.id"), nullable=False)
    transaction_code = Column(String, unique=True, nullable=False)
    amount_payed = Column(DECIMAL(15, 2), nullable=False)
    date_payed = Column(Date, nullable=False)
    description = Column(Text)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def get_usuario(username: str, password: str, db: Session):
    user = db.query(Usuario).filter(Usuario.username == username, Usuario.password == password).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return user
def get_current_analyst(username: str, password: str, db: Session = Depends(get_db)):
    user = get_usuario(username, password, db)
    if user.role.nombre != "Analista":
        raise HTTPException(status_code=403, detail="El usuario no tiene permisos para esta operación")
    return user

def get_current_client(username: str, password: str, db: Session = Depends(get_db)):
    user = get_usuario(username, password, db)
    if user.role.nombre != "Cliente":
        raise HTTPException(status_code=403, detail="El usuario no tiene permisos para esta operación")
    return user

@app.post("/prestamos/")
def crear_prestamo(
    usuario_id: int,
    monto_solicitado: float,
    interest_rate: float,
    amount_cuotas: int,
    razon_prestamo_id: int,
    username: str,
    password: str,
    db: Session = Depends(get_db),
):
    current_user = get_current_client(username, password, db)  # Validación de cliente
    if current_user.id != usuario_id:
        raise HTTPException(status_code=403, detail="El usuario no tiene permisos para crear préstamos para otros clientes.")

    if monto_solicitado < 400:
        raise HTTPException(status_code=400, detail="Monto mínimo es de Q400.00")
    if monto_solicitado > 10000 and amount_cuotas > 12:
        raise HTTPException(status_code=400, detail="No se permiten más de 12 cuotas para montos mayores a Q10,000")
    total_to_pay = monto_solicitado * (1 + (interest_rate / 100))
    nuevo_prestamo = Prestamo(
        usuario_id=usuario_id,
        monto_solicitado=monto_solicitado,
        interest_rate=interest_rate,
        amount_cuotas=amount_cuotas,
        razon_prestamo_id=razon_prestamo_id,
        total_to_pay=total_to_pay,
        date_requested=date.today(),
        prestamo_status_id=1,
    )
    db.add(nuevo_prestamo)
    db.commit()
    db.refresh(nuevo_prestamo)
    for i in range(1, amount_cuotas + 1):
        nueva_cuota = Cuota(
            prestamo_id=nuevo_prestamo.id,
            usuario_id=usuario_id,
            cuota_status_id=1,
            numero_cuota=i,
            amount_to_pay=total_to_pay / amount_cuotas,
            date_to_pay=date.today() + timedelta(days=30 * i),
        )
        db.add(nueva_cuota)
    db.commit()
    return {"msg": "Préstamo creado", "id": nuevo_prestamo.id}


@app.post("/comprobantes/")
def registrar_comprobante(
    cuotas_id: int,
    transaction_code: str,
    amount_payed: float,
    username: str,
    password: str,
    db: Session = Depends(get_db),
):
    current_user = get_current_client(username, password, db)  # Validación de cliente
    cuota = db.query(Cuota).filter(Cuota.id == cuotas_id, Cuota.usuario_id == current_user.id).first()
    if not cuota:
        raise HTTPException(status_code=404, detail="Cuota no encontrada")
    mora = max(0, cuota.amount_to_pay - amount_payed) * 0.05
    cuota.mora_amount += mora
    cuota.amount_to_pay -= amount_payed
    cuota.cuota_status_id = 2 if cuota.amount_to_pay <= 0 else 1
    nuevo_comprobante = Comprobante(
        cuotas_id=cuotas_id,
        usuario_id=current_user.id,
        transaction_code=transaction_code,
        amount_payed=amount_payed,
        date_payed=date.today(),
        comprobante_status_id=1,
    )
    db.add(nuevo_comprobante)
    db.commit()
    return {"msg": "Comprobante registrado"}


@app.get("/reportes/prestamos/")
def reporte_prestamos(db: Session = Depends(get_db)):
    prestamos = db.query(Prestamo).all()
    return prestamos

@app.get("/usuarios/")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return usuarios
@app.get("/prestamos/cliente/")
def prestamos_cliente(username: str, password: str, db: Session = Depends(get_db)):
    current_user = get_current_client(username, password, db)  # Validación de cliente
    prestamos = db.query(Prestamo).filter(Prestamo.usuario_id == current_user.id).all()
    return prestamos
@app.get("/reportes/prestamos/")
def reporte_prestamos(username: str, password: str, db: Session = Depends(get_db)):
    current_user = get_current_analyst(username, password, db)  # Validación de analista
    prestamos = db.query(Prestamo).all()
    return prestamos
@app.put("/prestamos/{prestamo_id}/revisar")
def revisar_prestamo(
    prestamo_id: int,
    aprobado: bool,
    interest_rate: float = None,
    iva: float = None,
    costos_administrativos: float = None,
    username: str = None,
    password: str = None,
    db: Session = Depends(get_db)
):
    current_user = get_current_analyst(username, password, db)  # Validación de analista

    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    # Actualiza la tasa de interés si se proporciona
    if interest_rate:
        prestamo.interest_rate = interest_rate

    # Calcula y asigna IVA y costos administrativos si se proporcionan
    if iva:
        prestamo.total_to_pay += prestamo.monto_solicitado * (iva / 100)
    if costos_administrativos:
        prestamo.total_to_pay += costos_administrativos

    # Actualiza el estado del préstamo
    prestamo.prestamo_status_id = 2 if aprobado else 3  # 2: Aprobado, 3: Rechazado
    db.commit()
    return {"msg": f"Préstamo {'aprobado' if aprobado else 'rechazado'} con éxito"}

@app.put("/comprobantes/{comprobante_id}/validar")
def validar_comprobante(
    comprobante_id: int,
    aprobado: bool,
    razon_rechazo: str = None,
    username: str = None,
    password: str = None,
    db: Session = Depends(get_db)
):
    current_user = get_current_analyst(username, password, db)  # Validación de analista

    comprobante = db.query(Comprobante).filter(Comprobante.id == comprobante_id).first()
    if not comprobante:
        raise HTTPException(status_code=404, detail="Comprobante no encontrado")

    if aprobado:
        comprobante.comprobante_status_id = 2  # Estado aprobado
    else:
        comprobante.comprobante_status_id = 3  # Estado rechazado
        comprobante.description = razon_rechazo if razon_rechazo else "Rechazado sin razón especificada"

    db.commit()
    return {"msg": f"Comprobante {'aprobado' if aprobado else 'rechazado'} con éxito"}
@app.get("/prestamos/{prestamo_id}/finiquito")
def solicitar_finiquito(
    prestamo_id: int,
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    current_user = get_current_client(username, password, db)  # Validación de cliente

    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id, Prestamo.usuario_id == current_user.id).first()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    cuotas = db.query(Cuota).filter(Cuota.prestamo_id == prestamo.id).all()
    if any(cuota.cuota_status_id != 2 for cuota in cuotas):  # Verifica si alguna cuota no está pagada
        raise HTTPException(status_code=400, detail="No todas las cuotas han sido pagadas")

    if any(cuota.mora_amount > 0 for cuota in cuotas):  # Verifica si hay mora pendiente
        raise HTTPException(status_code=400, detail="El préstamo tiene mora pendiente")

    return {"msg": "Préstamo pagado en su totalidad. Finiquito generado con éxito."}

@app.get("/reportes/prestamos/todos")
def reporte_prestamos_detallado(username: str, password: str, db: Session = Depends(get_db)):
    current_user = get_current_analyst(username, password, db)  # Validación de analista
    prestamos = db.query(Prestamo).join(Cliente).join(Usuario).all()

    reporte = []
    for prestamo in prestamos:
        cliente = prestamo.usuario
        reporte.append({
            "nombre_cliente": cliente.nombre,
            "estado_civil": cliente.estado_civil_id,
            "ingresos_estimados": cliente.ingresos_estimados,
            "monto_prestado": prestamo.monto_solicitado,
            "cantidad_cuotas": prestamo.amount_cuotas,
            "pagos_realizados": db.query(Cuota).filter(Cuota.prestamo_id == prestamo.id, Cuota.cuota_status_id == 2).count()
        })

    return reporte

@app.get("/reportes/prestamos/rechazados")
def reporte_prestamos_rechazados(username: str, password: str, db: Session = Depends(get_db)):
    current_user = get_current_analyst(username, password, db)  # Validación de analista
    prestamos = db.query(Prestamo).filter(Prestamo.prestamo_status_id == 3).all()  # 3: Rechazado

    reporte = []
    for prestamo in prestamos:
        cliente = prestamo.usuario
        reporte.append({
            "nombre_cliente": cliente.nombre,
            "estado_civil": cliente.estado_civil_id,
            "ingresos_estimados": cliente.ingresos_estimados,
            "monto_solicitado": prestamo.monto_solicitado,
            "razon_rechazo": "Razón del rechazo si la tienes almacenada",
        })

    return reporte

@app.get("/reportes/prestamos/morosos")
def reporte_prestamos_morosos(dias_atraso: int, username: str, password: str, db: Session = Depends(get_db)):
    current_user = get_current_analyst(username, password, db)  # Validación de analista
    if dias_atraso not in [1, 30, 60, 90]:
        raise HTTPException(status_code=400, detail="Los días de atraso deben ser 1, 30, 60, o 90")

    prestamos_morosos = db.query(Prestamo).join(Cuota).filter(
        Cuota.date_to_pay < date.today() - timedelta(days=dias_atraso),
        Cuota.cuota_status_id != 2  # Cuota no pagada
    ).all()

    reporte = []
    for prestamo in prestamos_morosos:
        cliente = prestamo.usuario
        reporte.append({
            "nombre_cliente": cliente.nombre,
            "dias_atraso": dias_atraso,
            "monto_prestado": prestamo.monto_solicitado,
            "cantidad_cuotas": prestamo.amount_cuotas,
        })

    return reporte

@app.get("/reportes/prestamos/resumen")
def resumen_total_prestamos(username: str, password: str, db: Session = Depends(get_db)):
    current_user = get_current_analyst(username, password, db)  # Validación de analista

    prestamos = db.query(Prestamo).all()
    total_prestado = sum(prestamo.monto_solicitado for prestamo in prestamos)
    total_intereses = sum((prestamo.total_to_pay - prestamo.monto_solicitado) for prestamo in prestamos)

    return {
        "total_prestado": total_prestado,
        "total_intereses": total_intereses,
        "total_prestamos": len(prestamos)
    }
