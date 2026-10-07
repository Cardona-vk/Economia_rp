import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Canvas institucional formal con encabezado y pie de página en negro estándar.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_header_footer(self, page_count):
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.black)

        # Encabezado estándar
        self.drawString(54, 752, "INSTITUCIÓN UNIVERSITARIA PASCUAL BRAVO • BASES DE DATOS I")
        self.drawRightString(612 - 54, 752, "RTF4 — IMPLEMENTACIÓN Y REFINAMIENTO DDL")
        self.setStrokeColor(colors.HexColor("#999999"))
        self.setLineWidth(0.5)
        self.line(54, 746, 612 - 54, 746)

        # Pie de página estándar
        self.line(54, 42, 612 - 54, 42)
        self.drawString(54, 30, "Proyecto de Aula: Economy RP — Grupo 4 • Docente: Juan Camilo Palacio Alcaraz")
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(612 - 54, 30, page_text)

        self.restoreState()


def build_pdf():
    pdf_filename = "RTF4_Implementacion_Refinamiento_DDL_EconomyRP.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Colores sobrios y formales (sin azules llamativos)
    BLACK = colors.black
    DARK_GRAY = colors.HexColor("#222222")
    BORDER_COLOR = colors.HexColor("#333333")
    BG_HEADER = colors.HexColor("#F2F2F2")
    BG_BOX = colors.HexColor("#FAFAFA")

    # Tipografías sobrias
    styles.add(ParagraphStyle(
        'CoverDocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=BLACK,
        alignment=1
    ))

    styles.add(ParagraphStyle(
        'CoverDocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=DARK_GRAY,
        alignment=1
    ))

    styles.add(ParagraphStyle(
        'MainSecTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=BLACK,
        spaceBefore=14,
        spaceAfter=5,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        'SubSectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=BLACK,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.8,
        textColor=BLACK,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.8,
        textColor=BLACK,
        leftIndent=12,
        spaceAfter=2.5
    ))

    styles.add(ParagraphStyle(
        'THeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=9.8,
        textColor=BLACK,
        alignment=1
    ))

    styles.add(ParagraphStyle(
        'TCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=BLACK
    ))

    styles.add(ParagraphStyle(
        'TCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=BLACK
    ))

    styles.add(ParagraphStyle(
        'TCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=BLACK,
        alignment=1
    ))

    styles.add(ParagraphStyle(
        'ImageCaption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=DARK_GRAY,
        alignment=1,
        spaceBefore=3,
        spaceAfter=6
    ))

    story = []

    # =========================================================================
    # 1. PORTADA INSTITUCIONAL
    # =========================================================================
    story.append(Spacer(1, 25))
    story.append(Paragraph("INSTITUCIÓN UNIVERSITARIA PASCUAL BRAVO", ParagraphStyle('H1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, leading=17, textColor=BLACK, alignment=1)))
    story.append(Paragraph("FACULTAD DE INGENIERÍA • DEPARTAMENTO DE SISTEMAS", ParagraphStyle('H2', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=12, textColor=DARK_GRAY, alignment=1)))
    story.append(Paragraph("BASES DE DATOS I", ParagraphStyle('H3', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=BLACK, alignment=1)))
    story.append(Spacer(1, 20))

    story.append(Paragraph("INFORME TÉCNICO DE AULA RTF4", styles['CoverDocSubtitle']))
    story.append(Spacer(1, 5))
    story.append(Paragraph("IMPLEMENTACIÓN Y REFINAMIENTO DEL MODELO LÓGICO DDL", styles['CoverDocTitle']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Motor Relacional de Gestión Económica, Trazabilidad Contable e Inmutabilidad Transaccional<br/>para Servidores de Rol GTA (Economy RP)", ParagraphStyle('Desc', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=9, leading=12, textColor=DARK_GRAY, alignment=1)))
    
    story.append(Spacer(1, 22))

    meta_data = [
        [Paragraph("<b>Proyecto de Aula:</b>", styles['TCellBold']), Paragraph("Economy RP (Motor Económico Relacional)", styles['TCell'])],
        [Paragraph("<b>Equipo de Trabajo:</b>", styles['TCellBold']), Paragraph("Grupo 4", styles['TCell'])],
        [Paragraph("<b>Docente Asesor:</b>", styles['TCellBold']), Paragraph("Juan Camilo Palacio Alcaraz", styles['TCell'])],
        [Paragraph("<b>Integrantes:</b>", styles['TCellBold']), Paragraph("• Miguel Ángel Cardona Agudelo<br/>• Luisa María López Orrego<br/>• Jorge Luis Ordoñez Ávila", styles['TCell'])],
        [Paragraph("<b>Materia / Semestre:</b>", styles['TCellBold']), Paragraph("Bases de Datos I • Semestre 2026-2", styles['TCell'])],
        [Paragraph("<b>Fecha de Entrega:</b>", styles['TCellBold']), Paragraph("03 de Octubre de 2026", styles['TCell'])]
    ]
    meta_table = Table(meta_data, colWidths=[130, 374])
    meta_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 18))

    rubric_summary = [
        [Paragraph("<b>RÚBRICA DE EVALUACIÓN OFICIAL RTF4 (100% PONDERADO)</b>", styles['THeader']), Paragraph("<b>PESO</b>", styles['THeader'])],
        [Paragraph("1. Evolución y Refinamiento del Modelo Lógico (Antes vs. Después)", styles['TCell']), Paragraph("<b>25% (1.25)</b>", styles['TCellCenter'])],
        [Paragraph("2. Definición y Estructura del Esquema DDL Tabular", styles['TCell']), Paragraph("<b>25% (1.25)</b>", styles['TCellCenter'])],
        [Paragraph("3. Informe de Mejoras y Proceso de Normalización (1FN, 2FN, 3FN, BCNF, 4FN, DKNF)", styles['TCell']), Paragraph("<b>20% (1.00)</b>", styles['TCellCenter'])],
        [Paragraph("4. Pruebas Estructurales, Hallazgos y Manejo de Errores de Motor SGBD", styles['TCell']), Paragraph("<b>20% (1.00)</b>", styles['TCellCenter'])],
        [Paragraph("5. Estructura, Formato Institucional y Defensa Técnica del Modelo", styles['TCell']), Paragraph("<b>10% (0.50)</b>", styles['TCellCenter'])],
    ]
    rubric_table = Table(rubric_summary, colWidths=[404, 100])
    rubric_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(rubric_table)

    story.append(PageBreak())

    # =========================================================================
    # 2. SECCIÓN 1: OBJETIVO DE LA ENTREGA
    # =========================================================================
    story.append(Paragraph("1. Objetivo de la Entrega", styles['MainSecTitle']))
    story.append(Paragraph(
        "El objetivo principal de esta fase es la materialización y refinamiento del modelo lógico relacional en el Sistema Gestor de Bases de Datos (MySQL 8.0 con motor transaccional InnoDB), a partir del diseño conceptual previo. Se busca implementar y certificar la robustez del esquema DDL físico para validar la integridad referencial, suprimir inconsistencias y asegurar el estricto cumplimiento de las reglas del negocio de rol, resolviendo fallas críticas tales como:",
        styles['DocBody']
    ))
    story.append(Paragraph("• <b>Inconsistencias en tipos de datos:</b> Estandarización a <code>DECIMAL(12,2)</code> para evitar pérdidas de precisión por coma flotante.", styles['DocBullet']))
    story.append(Paragraph("• <b>Definición rigurosa de claves primarias y foráneas:</b> Eliminación de claves compuestas ambiguas y soporte de llaves subrogadas.", styles['DocBullet']))
    story.append(Paragraph("• <b>Restricciones de integridad y dominio (CHECKs):</b> Blindaje de estados y tipos contables para evitar datos huérfanos o no tipificados.", styles['DocBullet']))
    story.append(Paragraph("• <b>Consistencia transaccional y atomicidad (ACID):</b> Asegurar que en negociaciones de intercambio P2P y liquidación laboral ningún bien ni saldo quede duplicado o en el limbo.", styles['DocBullet']))
    story.append(Paragraph("• <b>Inmutabilidad en el libro mayor contable:</b> Estructuración de un historial de transacciones <i>append-only</i> con partida doble.", styles['DocBullet']))
    story.append(Paragraph("• <b>Automatización de políticas económicas:</b> Control en tiempo real de límites de posesión por jugador, periodos de enfriamiento laboral, tasas de drenaje anti-inflacionario y detección reactiva de bancarrota.", styles['DocBullet']))

    story.append(Spacer(1, 4))

    # =========================================================================
    # 3. SECCIÓN 2: REGLAS DE NEGOCIO (RN001 - RN012)
    # =========================================================================
    story.append(Paragraph("2. Reglas de Negocio (RN001 - RN012)", styles['MainSecTitle']))
    story.append(Paragraph("A continuación se detallan las reglas de negocio formalizadas para el dominio económico del servidor de rol GTA (Economy RP), expresando su condición lógica y su mecanismo de implementación exclusivo en la base de datos:", styles['DocBody']))

    rn_data = [
        [Paragraph("<b>CÓDIGO</b>", styles['THeader']), Paragraph("<b>NOMBRE</b>", styles['THeader']), Paragraph("<b>DESCRIPCIÓN FUNCIONAL</b>", styles['THeader']), Paragraph("<b>FÓRMULA / CONDICIÓN</b>", styles['THeader']), Paragraph("<b>IMPACTO DDL / SGBD</b>", styles['THeader'])],
        [
            Paragraph("<b>RN001</b>", styles['TCellBold']),
            Paragraph("Registro Único Laboral", styles['TCellBold']),
            Paragraph("Al completar una jornada, el sistema calcula y acredita automáticamente la ganancia a la cuenta del jugador.", styles['TCell']),
            Paragraph("Ganancia = Tarifa_base × Horas", styles['TCellCenter']),
            Paragraph("Tabla <code>jornadas_laborales</code>, PK subrogada <code>id_jornada</code> y columna histórica inmutable <code>monto_pagado</code>.", styles['TCell'])
        ],
        [
            Paragraph("<b>RN002</b>", styles['TCellBold']),
            Paragraph("Propiedad Única y Exclusiva", styles['TCellBold']),
            Paragraph("Un bien físico (vehículo con placa, propiedad) solo puede pertenecer a un único personaje a la vez.", styles['TCell']),
            Paragraph("Propietario = 1 por cada Bien activo", styles['TCellCenter']),
            Paragraph("Clave foránea atómica <code>items.id_jugador</code> con integridad referencial directa (1:N estricto).", styles['TCell'])
        ],
        [
            Paragraph("<b>RN003</b>", styles['TCellBold']),
            Paragraph("Inmutabilidad del Historial", styles['TCellBold']),
            Paragraph("Toda transacción financiera o comercial registrada no puede ser editada ni eliminada bajo ninguna circunstancia.", styles['TCell']),
            Paragraph("Política Append-Only (Sin UPDATE / DELETE)", styles['TCellCenter']),
            Paragraph("Tablas <code>transacciones</code> y <code>detalles_transacciones</code> inmutables protegidas por disparadores.", styles['TCell'])
        ],
        [
            Paragraph("<b>RN004</b>", styles['TCellBold']),
            Paragraph("Restricción por Deuda / Embargo", styles['TCellBold']),
            Paragraph("Un bien no puede transferirse si posee deuda activa, embargo o cuotas financieras pendientes.", styles['TCell']),
            Paragraph("Restriccion = 'Ninguna'<br/>(tiene_deuda = FALSE)", styles['TCellCenter']),
            Paragraph("Columna <code>tiene_deuda BOOLEAN NOT NULL DEFAULT FALSE</code> y validación en procedimiento de tradeo.", styles['TCell'])
        ],
        [
            Paragraph("<b>RN005</b>", styles['TCellBold']),
            Paragraph("Trazabilidad de Creación de Dinero", styles['TCellBold']),
            Paragraph("Todo dinero inyectado (salarios, bonos iniciales) debe originarse formalmente de la cuenta oficial 'SISTEMA'.", styles['TCell']),
            Paragraph("Origen = Cuenta_Sistema si Emisor = Sistema", styles['TCellCenter']),
            Paragraph("<code>cuentas.tipo_cuenta = 'SISTEMA'</code> (id_jugador NULL) y asiento de partida doble en detalles.", styles['TCell'])
        ],
        [
            Paragraph("<b>RN006</b>", styles['TCellBold']),
            Paragraph("Comisión por Transferencia", styles['TCellBold']),
            Paragraph("Toda compraventa o intercambio descuenta una comisión porcentual que se acredita a la Tesorería como drenaje anti-inflación.", styles['TCell']),
            Paragraph("Comisión = Monto × Porcentaje_Comisión", styles['TCellCenter']),
            Paragraph("Atributo <code>servidores.porcentaje_comision</code> y asiento secundario de drenaje fiscal en detalles.", styles['TCell'])
        ],
        [
            Paragraph("<b>RN007</b>", styles['TCellBold']),
            Paragraph("Límite Máximo de Propiedades", styles['TCellBold']),
            Paragraph("Un jugador no puede registrar más bienes que el tope máximo parametrizado por el administrador.", styles['TCell']),
            Paragraph("COUNT(Items) <= Limite_Bienes_Servidor", styles['TCellCenter']),
            Paragraph("Atributo <code>servidores.limite_bienes_por_jugador</code> y control de aforo en inserción/tradeo.", styles['TCell'])
        ],
        [
            Paragraph("<b>RN008</b>", styles['TCellBold']),
            Paragraph("Enfriamiento Laboral (Cooldown)", styles['TCellBold']),
            Paragraph("Un jugador debe cumplir un tiempo mínimo de descanso entre turnos del mismo empleo para evitar explotación.", styles['TCell']),
            Paragraph("Hora_Actual - Hora_Ultima >= Tiempo_Cooldown", styles['TCellCenter']),
            Paragraph("Atributo <code>servidores.tiempo_enfriamiento_min</code> e inspección temporal en inserción laboral.", styles['TCell'])
        ],
        [
            Paragraph("<b>RN009</b>", styles['TCellBold']),
            Paragraph("Penalización por Bancarrota", styles['TCellBold']),
            Paragraph("Si el saldo disponible no cubre obligaciones o queda en negativo, el jugador pasa a estado 'BANCARROTA', bloqueando operaciones.", styles['TCell']),
            Paragraph("Saldo < 0 => Estado = 'BANCARROTA'", styles['TCellCenter']),
            Paragraph("Restricción <code>CHECK (estado IN ('ACTIVO','BANCARROTA','SUSPENDIDO'))</code> en <code>jugadores</code>.", styles['TCell'])
        ],
        [
            Paragraph("<b>RN010</b>", styles['TCellBold']),
            Paragraph("Confirmación Doble en Tradeo", styles['TCellBold']),
            Paragraph("Ambas partes deben confirmar explícitamente los términos. Cualquier modificación reinicia los candados de confirmación.", styles['TCell']),
            Paragraph("Ejecutar si (conf_j1 = TRUE AND conf_j2 = TRUE)", styles['TCellCenter']),
            Paragraph("Banderas booleanas <code>confirmacion_j1</code> y <code>confirmacion_j2</code> en <code>negociaciones_tradeos</code>.", styles['TCell'])
        ],
        [
            Paragraph("<b>RN011</b>", styles['TCellBold']),
            Paragraph("Límite Diario de Tradeos", styles['TCellBold']),
            Paragraph("Un operador no puede ejecutar más intercambios exitosos al día que el cupo configurado, evitando lavado de activos.", styles['TCell']),
            Paragraph("COUNT(Tradeos_Hoy) <= limite_tradeos_diarios", styles['TCellCenter']),
            Paragraph("Columna <code>servidores.limite_tradeos_diarios</code> y agregación temporal sobre <code>DATE(fecha_hora)</code>.", styles['TCell'])
        ],
        [
            Paragraph("<b>RN012</b>", styles['TCellBold']),
            Paragraph("Tradeo Único Simultáneo", styles['TCellBold']),
            Paragraph("Un jugador solo puede tener una negociación abierta a la vez, impidiendo comprometer saldos o ítems en paralelo.", styles['TCell']),
            Paragraph("COUNT(Negociaciones_Activas) <= 1", styles['TCellCenter']),
            Paragraph("Restricción de dominio sobre el ciclo de vida <code>CHECK (estado IN (...))</code> en negociaciones.", styles['TCell'])
        ],
    ]

    rn_table = Table(rn_data, colWidths=[40, 80, 160, 104, 120])
    rn_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(rn_table)

    story.append(Spacer(1, 6))

    # =========================================================================
    # 4. SECCIÓN 3: EVOLUCIÓN DEL MODELO LÓGICO (ANTES VS. DESPUÉS CON IMÁGENES)
    # =========================================================================
    story.append(Paragraph("3. Evolución del Modelo Lógico", styles['MainSecTitle']))

    story.append(Paragraph("3.1 Modelo Lógico Inicial (Antes)", styles['SubSectionTitle']))
    story.append(Paragraph(
        "En la fase conceptual y lógica preliminar del RTF3, la tabla <code>T_Jornada_Laboral</code> contenía el atributo calculado <code>ganancia_calculada</code> lo cual era redundante. Adicionalmente no se especificaba claramente restricciones de unicidad (UNIQUE) en la relación <code>T_Cuenta</code> y <code>T_Jugador</code>, lo que permitía que se pudiera asignar múltiples cuentas personales a un mismo jugador o dejar cabeceras de transacciones sin vinculación directa al origen de la oferta.",
        styles['DocBody']
    ))
    story.append(Paragraph("Cabe resaltar que tampoco estábamos respetando los parámetros de una nomenclatura purista como siempre lo ha exigido el docente.", styles['DocBody']))

    # Imagen 1: DrawDB
    if os.path.exists("static/img/drawdb_model.jpg"):
        story.append(Image("static/img/drawdb_model.jpg", width=460, height=241))
        story.append(Paragraph("(Primer diseño lógico creado con el motor online DrawDB)", styles['ImageCaption']))

    # Imagen 2: dbdiagram
    if os.path.exists("static/img/dbdiagram_model.png"):
        story.append(Image("static/img/dbdiagram_model.png", width=460, height=142))
        story.append(Paragraph("Enlace a aplicación: <u>https://dbdiagram.io/d/6aa9e23baf7c3b0bd1e995fe</u>", styles['ImageCaption']))

    story.append(Spacer(1, 4))
    story.append(Paragraph("3.2 Modelo Lógico Corregido (Después)", styles['SubSectionTitle']))
    story.append(Paragraph(
        "Aquí se muestra el modelo lógico en el gestor de bases de datos MYSQL tras el proceso de implementación física e inserción DDL.",
        styles['DocBody']
    ))

    # Imagen 3: MySQL EER
    if os.path.exists("static/img/mysql_eer_model.jpg"):
        story.append(Image("static/img/mysql_eer_model.jpg", width=460, height=282))
        story.append(Paragraph("(Diseño corregido creado en MYSQL)", styles['ImageCaption']))

    story.append(Paragraph(
        "Este script DDL definitivo consolida la estructura física corrigiendo nomenclaturas, claves y lógica relacional:",
        styles['DocBody']
    ))
    story.append(Paragraph("1. <b>Normalización de Nomenclatura:</b> Sin prefijos redundantes en tablas: Eliminar el prefijo <code>T_</code> (las tablas se reconocen por su contexto y definición). Nombres de tablas en plural e identificadores en singular: <code>servidores</code>, <code>jugadores</code>, etc. Además de formato visual consistente (snake_case en minúsculas) para evitar problemas de sensibilidad a mayúsculas/minúsculas entre motores.", styles['DocBullet']))
    story.append(Paragraph("2. <b>Intercambio Bilateral Simétrico:</b> <code>negociaciones_tradeos</code> evoluciona para soportar <code>id_item_j1</code>, <code>id_item_j2</code>, <code>monto_j1</code> y <code>monto_j2</code>, respaldado por la restricción que exige al menos un ítem o monto en la oferta.", styles['DocBullet']))
    story.append(Paragraph("3. <b>Gestión de Cuenta del Sistema:</b> Se habilitó la cuenta oficial con <code>tipo_cuenta = 'SISTEMA'</code> (id_jugador NULL), garantizando estrictamente una sola cuenta de Sistema por cada servidor de juego para la inyección lícita salarial.", styles['DocBullet']))
    story.append(Paragraph("4. <b>Capa Transaccional y Eventos Automáticos:</b> Se automatizaron los cobros y transferencias vía procedimientos y bloques transaccionales atómicos (ACID), forzando la inmutabilidad contable mediante disparadores y eventos de expiración temporal.", styles['DocBullet']))

    story.append(Spacer(1, 4))

    # Tabla comparativa Antes vs Después
    evol_data = [
        [Paragraph("<b>ENTIDAD</b>", styles['THeader']), Paragraph("<b>DISEÑO INICIAL (RTF3 / ANTES)</b>", styles['THeader']), Paragraph("<b>DISEÑO CORREGIDO (RTF4 / DESPUÉS)</b>", styles['THeader']), Paragraph("<b>MEJORA TÉCNICA APORTADA</b>", styles['THeader'])],
        [
            Paragraph("<b>servidores</b>", styles['TCellBold']),
            Paragraph("Contenedor conceptual sin atributos claros de gobernanza.", styles['TCell']),
            Paragraph("Tabla con <code>porcentaje_comision</code>, <code>limite_bienes</code>, <code>cooldown_min</code> y <code>limite_tradeos_diarios</code>.", styles['TCell']),
            Paragraph("Centraliza la parametrización de RN006, RN007, RN008 y RN011.", styles['TCell'])
        ],
        [
            Paragraph("<b>jugadores</b>", styles['TCellBold']),
            Paragraph("Atributos genéricos, credenciales en texto plano, sin restricción de estado.", styles['TCell']),
            Paragraph("PK simple, FK a servidores, username/correo únicos, hash criptográfico y <code>CHECK (estado IN (...))</code>.", styles['TCell']),
            Paragraph("Integridad referencial, seguridad de acceso y soporte formal de estados judiciales (RN009).", styles['TCell'])
        ],
        [
            Paragraph("<b>empleos</b>", styles['TCellBold']),
            Paragraph("Mezclaba horas trabajadas con la definición del oficio.", styles['TCell']),
            Paragraph("Catálogo desacoplado con <code>id_empleo PK</code>, FK a servidor, nombre y <code>tarifa_base DECIMAL(10,2)</code>.", styles['TCell']),
            Paragraph("Desacoplamiento total entre la oferta laboral y los turnos individuales ejecutados.", styles['TCell'])
        ],
        [
            Paragraph("<b>jornadas_laborales</b>", styles['TCellBold']),
            Paragraph("Planteada con PK compuesta (jugador + empleo) y ganancia calculada dinámica.", styles['TCell']),
            Paragraph("PK subrogada <code>id_jornada</code>, FKs independientes, horas trabajadas y <code>monto_pagado</code> inmutable.", styles['TCell']),
            Paragraph("Cumplimiento estricto de 2FN y 3FN; historial laboral auditable sin desincronización de tarifas.", styles['TCell'])
        ],
        [
            Paragraph("<b>cuentas</b>", styles['TCellBold']),
            Paragraph("Atada 1:1 rígidamente a Jugador con UNIQUE. Sin cuenta oficial del sistema.", styles['TCell']),
            Paragraph("PK simple, FK a jugador (nullable), FK a servidor, <code>tipo_cuenta CHECK ('PERSONAL','SISTEMA')</code>.", styles['TCell']),
            Paragraph("Habilita la Tesorería Central (RN005) y elimina la restricción que impedía cuentas múltiples (1:N).", styles['TCell'])
        ],
        [
            Paragraph("<b>items</b>", styles['TCellBold']),
            Paragraph("Categoría como texto libre, fechas redundantes y sin control de deudas.", styles['TCell']),
            Paragraph("PK simple, FK a jugador, precio tasado, fecha adquisición, flag <code>tiene_deuda</code> y estado de custodia.", styles['TCell']),
            Paragraph("Cumple RN002 (un dueño por bien) y RN004 (bloqueo por gravamen o embargo).", styles['TCell'])
        ],
        [
            Paragraph("<b>negociaciones_tradeos</b>", styles['TCellBold']),
            Paragraph("Inexistente; se pretendía ejecutar el intercambio directamente sobre transacciones.", styles['TCell']),
            Paragraph("Mesa bilateral simétrica con <code>id_item_j1/j2</code>, <code>monto_j1/j2</code>, doble confirmación y expiración.", styles['TCell']),
            Paragraph("Garantiza la máquina de estados de negociación (RN010, RN012) con soporte de permuta cruzada.", styles['TCell'])
        ],
        [
            Paragraph("<b>transacciones</b>", styles['TCellBold']),
            Paragraph("Sobrecargada con listas de texto concatenadas (usuarios y bienes en un campo).", styles['TCell']),
            Paragraph("Cabecera inmutable de libro mayor con tipo de operación, monto nominal, fecha_hora y estado.", styles['TCell']),
            Paragraph("Estructura de auditoría contable de sólo adición (*append-only*) inalterable (RN003).", styles['TCell'])
        ],
        [
            Paragraph("<b>detalles_transacciones</b>", styles['TCellBold']),
            Paragraph("Inexistente en el diseño preliminar.", styles['TCell']),
            Paragraph("Asientos contables por partida doble con cuenta_origen, cuenta_destino, tipo de movimiento y monto.", styles['TCell']),
            Paragraph("Trazabilidad contable estricta al centavo y cumplimiento de 1FN.", styles['TCell'])
        ],
    ]

    evol_table = Table(evol_data, colWidths=[85, 130, 159, 130])
    evol_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(KeepTogether([evol_table]))

    story.append(Spacer(1, 6))

    # =========================================================================
    # 5. SECCIÓN 4: ESTRUCTURA DEL ESQUEMA (DDL)
    # =========================================================================
    story.append(Paragraph("4. Estructura del Esquema (DDL)", styles['MainSecTitle']))
    story.append(Paragraph("A continuación se documenta de forma exhaustiva y rigurosa la estructura tabular de las entidades físicas en el motor MySQL (InnoDB), especificando tipos de datos, nulidad, claves, valores por defecto y su justificación técnica vinculada a las reglas de negocio:", styles['DocBody']))

    def make_ddl_table(title, headers, rows, col_w):
        table_data = [[Paragraph(f"<b>{h}</b>", styles['THeader']) for h in headers]]
        for r in rows:
            formatted_row = []
            for idx, c in enumerate(r):
                if idx == 0:
                    formatted_row.append(Paragraph(f"<b>{c}</b>", styles['TCellBold']))
                elif idx in (1, 2, 3):
                    formatted_row.append(Paragraph(c, styles['TCellCenter']))
                else:
                    formatted_row.append(Paragraph(c, styles['TCell']))
            table_data.append(formatted_row)
        
        t = Table(table_data, colWidths=col_w)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 0.6, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 1.8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
            ('LEFTPADDING', (0, 0), (-1, -1), 3.5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3.5),
        ]))
        return KeepTogether([
            Paragraph(f"<b>Tabla: {title}</b>", styles['SubSectionTitle']),
            Spacer(1, 1),
            t,
            Spacer(1, 4)
        ])

    ddl_headers = ["COLUMNA", "TIPO DE DATO", "NULO", "CLAVE / CONSTRAINT", "DEFAULT", "OBSERVACIONES Y REGLA VINCULADA"]
    col_w_ddl = [95, 80, 32, 105, 52, 140]

    # 1. servidores
    story.append(make_ddl_table(
        "servidores",
        ddl_headers,
        [
            ["id_servidor", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Identificador único de la instancia del servidor."],
            ["nombre", "VARCHAR(100)", "NO", "N/A", "N/A", "Nombre del servidor de RP."],
            ["porcentaje_comision", "DECIMAL(5,2)", "NO", "CHECK (>= 0)", "5.00", "Porcentaje de retención/drenaje por transacción (RN006)."],
            ["limite_bienes_por_jugador", "INT", "NO", "CHECK (> 0)", "100", "Máximo de propiedades/vehículos permitidos por usuario (RN007)."],
            ["tiempo_enfriamiento_min", "INT", "NO", "CHECK (>= 0)", "15", "Minutos de espera obligatorios entre turnos laborales (RN008)."],
            ["limite_tradeos_diarios", "INT", "NO", "CHECK (> 0)", "5", "Cupo máximo de tradeos diarios por usuario (RN011)."],
        ],
        col_w_ddl
    ))

    # 2. jugadores
    story.append(make_ddl_table(
        "jugadores",
        ddl_headers,
        [
            ["id_jugador", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Identificador único del jugador."],
            ["id_servidor", "INT", "NO", "FK → servidores(id_servidor)", "1", "Referencia al servidor al que pertenece el jugador."],
            ["nombre_usuario", "VARCHAR(50)", "NO", "UNIQUE", "N/A", "Nombre de usuario o apodo único por servidor."],
            ["correo", "VARCHAR(150)", "NO", "UNIQUE", "N/A", "Dirección de correo electrónico corporativo/personal."],
            ["contrasena_hash", "VARCHAR(255)", "NO", "N/A", "N/A", "Hash encriptado de clave de acceso."],
            ["fecha_registro", "DATETIME", "NO", "N/A", "CURRENT_TIMESTAMP", "Marca de tiempo por defecto."],
            ["estado", "VARCHAR(20)", "NO", "CHECK ('ACTIVO','BANCARROTA','SUSPENDIDO')", "'ACTIVO'", "Estados permitidos: 'ACTIVO', 'BANCARROTA', 'SUSPENDIDO' (RN009)."],
            ["es_admin", "BOOLEAN", "NO", "N/A", "FALSE", "Bandera de privilegios de administración."],
        ],
        col_w_ddl
    ))

    # 3. empleos
    story.append(make_ddl_table(
        "empleos",
        ddl_headers,
        [
            ["id_empleo", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Identificador del empleo o rol laboral."],
            ["id_servidor", "INT", "NO", "FK → servidores(id_servidor)", "1", "Referencia al servidor que habilita la plaza laboral."],
            ["nombre_empleo", "VARCHAR(100)", "NO", "N/A", "N/A", "Nombre de la labor (ej. Minero, Mecánico)."],
            ["tarifa_base", "DECIMAL(10,2)", "NO", "CHECK (> 0)", "N/A", "Pago parametrizado por hora o unidad de trabajo (RN001)."],
        ],
        col_w_ddl
    ))

    # 4. jornadas_laborales
    story.append(make_ddl_table(
        "jornadas_laborales",
        ddl_headers,
        [
            ["id_jornada", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Código correlativo de la jornada ejecutada."],
            ["id_jugador", "INT", "NO", "FK → jugadores(id_jugador)", "N/A", "Referencia al jugador que desempeñó el turno."],
            ["id_empleo", "INT", "NO", "FK → empleos(id_empleo)", "N/A", "Referencia al empleo desempeñado."],
            ["horas_trabajadas", "DECIMAL(6,2)", "NO", "CHECK (> 0)", "N/A", "Unidades de tiempo laboradas."],
            ["fecha_hora", "DATETIME", "NO", "N/A", "CURRENT_TIMESTAMP", "Cierre de turno registrado por defecto (RN008)."],
            ["monto_pagado", "DECIMAL(10,2)", "NO", "CHECK (>= 0)", "0.00", "Valor pagado inmutable (RN001, 3FN)."],
        ],
        col_w_ddl
    ))

    # 5. cuentas
    story.append(make_ddl_table(
        "cuentas",
        ddl_headers,
        [
            ["id_cuenta", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Identificador de la cuenta."],
            ["id_jugador", "INT", "SÍ", "FK → jugadores(id_jugador)", "NULL", "Vinculado si es cuenta 'PERSONAL'. Nulo en 'SISTEMA' (RN005)."],
            ["id_servidor", "INT", "SÍ", "FK → servidores(id_servidor)", "NULL", "Vinculado al servidor. Asignado en cuentas del Sistema."],
            ["tipo_cuenta", "VARCHAR(20)", "NO", "CHECK ('PERSONAL','SISTEMA')", "'PERSONAL'", "Categorías: 'PERSONAL' o 'SISTEMA' (RN005)."],
            ["saldo_inicial", "DECIMAL(12,2)", "NO", "N/A", "0.00", "Fondos asignados en la apertura de la cuenta."],
            ["saldo_disponible", "DECIMAL(12,2)", "NO", "CHECK (>= 0)", "0.00", "Balance líquido activo para transacciones (RN009)."],
        ],
        col_w_ddl
    ))

    # 6. items
    story.append(make_ddl_table(
        "items",
        ddl_headers,
        [
            ["id_item", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Identificador único del objeto o vehículo."],
            ["id_jugador", "INT", "NO", "FK → jugadores(id_jugador)", "N/A", "Relación foránea hacia el propietario legítimo (RN002)."],
            ["nombre", "VARCHAR(100)", "NO", "N/A", "N/A", "Nombre comercial o modelo del artículo."],
            ["precio", "DECIMAL(12,2)", "NO", "CHECK (>= 0)", "N/A", "Valor de tasación original."],
            ["fecha", "DATETIME", "NO", "N/A", "CURRENT_TIMESTAMP", "Fecha de creación o adquisición."],
            ["tiene_deuda", "BOOLEAN", "NO", "N/A", "FALSE", "Indicador de embargo o deuda pendiente (RN004)."],
            ["antiguedad_dias", "INT", "NO", "CHECK (>= 0)", "0", "Días acumulados para cálculo dinámico de depreciación."],
            ["estado_custodia", "VARCHAR(20)", "NO", "CHECK ('PERSONAL','EMBARGADO','EN_TRADE')", "'PERSONAL'", "Estado de posesión física y custodia transaccional."],
        ],
        col_w_ddl
    ))

    # 7. negociaciones_tradeos
    story.append(make_ddl_table(
        "negociaciones_tradeos",
        ddl_headers,
        [
            ["id_negociacion", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Código de la sesión de oferta P2P."],
            ["id_jugador_1", "INT", "NO", "FK → jugadores(id_jugador)", "N/A", "Relación foránea hacia proponente inicial."],
            ["id_jugador_2", "INT", "NO", "FK → jugadores(id_jugador)", "N/A", "Relación foránea hacia receptor de la oferta."],
            ["id_item_j1", "INT", "SÍ", "FK → items(id_item)", "NULL", "Ítem ofrecido por el Jugador 1."],
            ["id_item_j2", "INT", "SÍ", "FK → items(id_item)", "NULL", "Ítem ofrecido por el Jugador 2."],
            ["monto_j1", "DECIMAL(12,2)", "NO", "CHECK (>= 0)", "0.00", "Saldo líquido ofrecido por J1."],
            ["monto_j2", "DECIMAL(12,2)", "NO", "CHECK (>= 0)", "0.00", "Saldo líquido ofrecido por J2."],
            ["confirmacion_j1", "BOOLEAN", "NO", "N/A", "FALSE", "Confirmación del Jugador 1 (RN010)."],
            ["confirmacion_j2", "BOOLEAN", "NO", "N/A", "FALSE", "Confirmación del Jugador 2 (RN010)."],
            ["estado", "VARCHAR(50)", "NO", "CHECK ('PENDIENTE','ACEPTADO','EN_PROCESO','ESPERANDO_CONFIRMACION_FINAL','COMPLETADO','CANCELADO','EXPIRADO')", "'PENDIENTE'", "Estado de la negociación (RN012)."],
            ["fecha_creacion", "DATETIME", "NO", "N/A", "CURRENT_TIMESTAMP", "Apertura de la sesión de tradeo."],
            ["fecha_expiracion", "DATETIME", "NO", "N/A", "N/A", "Fecha límite calculada para completar el intercambio."],
        ],
        col_w_ddl
    ))

    # 8. transacciones
    story.append(make_ddl_table(
        "transacciones",
        ddl_headers,
        [
            ["id_transaccion", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Identificador inmutable de transacción."],
            ["id_item_afectado", "INT", "SÍ", "FK → items(id_item)", "NULL", "Relación foránea hacia el ítem transferido (si aplica)."],
            ["id_negociacion", "INT", "SÍ", "FK → negociaciones_tradeos(id_negociacion)", "NULL", "Relación foránea hacia la mesa de tradeo origen."],
            ["id_jornada", "INT", "SÍ", "FK → jornadas_laborales(id_jornada)", "NULL", "Relación foránea hacia la jornada laboral origen."],
            ["tipo_transaccion", "VARCHAR(30)", "NO", "CHECK ('PAGO_SALARIO','TRADEO_P2P','COMPRA_COMERCIANTE','AJUSTE_ADMIN')", "N/A", "Categorías: 'PAGO_SALARIO', 'TRADEO_P2P', 'COMPRA_COMERCIANTE'."],
            ["estado_transaccion", "VARCHAR(20)", "NO", "CHECK ('COMPLETADA','CANCELADA','REVERTIDA')", "'COMPLETADA'", "Estados: 'COMPLETADA', 'CANCELADA', 'REVERTIDA' (RN003)."],
            ["monto", "DECIMAL(12,2)", "NO", "CHECK (>= 0)", "N/A", "Valor nominal total procesado."],
            ["fecha_hora", "DATETIME", "NO", "N/A", "CURRENT_TIMESTAMP", "Marca de tiempo inmutable de ejecución (RN003)."],
        ],
        col_w_ddl
    ))

    # 9. detalles_transacciones
    story.append(make_ddl_table(
        "detalles_transacciones",
        ddl_headers,
        [
            ["id_detalle", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Código único del asiento contable."],
            ["id_transaccion", "INT", "NO", "FK → transacciones(id_transaccion)", "N/A", "Relación foránea hacia la transacción cabecera."],
            ["cuenta_origen", "INT", "NO", "FK → cuentas(id_cuenta)", "N/A", "Relación foránea hacia la cuenta debitada."],
            ["cuenta_destino", "INT", "NO", "FK → cuentas(id_cuenta)", "N/A", "Relación foránea hacia la cuenta acreditada."],
            ["tipo_movimiento", "VARCHAR(10)", "NO", "CHECK ('DEBITO','CREDITO')", "N/A", "Categorías de partida doble: 'DEBITO' o 'CREDITO'."],
            ["monto_detalle", "DECIMAL(12,2)", "NO", "CHECK (> 0)", "N/A", "Importe del movimiento contable parcial."],
            ["concepto", "VARCHAR(80)", "SÍ", "N/A", "NULL", "Descripción corta o justificación contable."],
        ],
        col_w_ddl
    ))

    story.append(Spacer(1, 6))

    # =========================================================================
    # 6. SECCIÓN 5: INFORME DE MEJORAS Y NORMALIZACIÓN
    # =========================================================================
    story.append(Paragraph("5. Informe de Mejoras y Normalización", styles['MainSecTitle']))

    story.append(Paragraph("5.1 Mejoras Implementadas", styles['SubSectionTitle']))
    story.append(Paragraph("• <b>Garantía de Cuenta Única de Sistema por Servidor:</b> La adición de la cuenta con <code>tipo_cuenta = 'SISTEMA'</code> (id_jugador NULL) impidió la duplicación de tesorerías por servidor sin interferir con las cuentas personales de los jugadores.", styles['DocBullet']))
    story.append(Paragraph("• <b>Atomicidad mediante Procedimientos y Bloques Transaccionales:</b> Los flujos complejos de pago salarial y confirmación de tradeo fueron empaquetados en transacciones explícitas (<code>START TRANSACTION, COMMIT, ROLLBACK</code>). En caso de cualquier error (falta de fondos, deudas o expiración), los manejadores restauran la base de datos a su estado previo.", styles['DocBullet']))
    story.append(Paragraph("• <b>Inclusión de Disparadores y Restricciones CHECK:</b> Validación de límites de inventario, tiempos de enfriamiento laboral e inmutabilidad estricta del libro mayor contable.", styles['DocBullet']))
    story.append(Paragraph("• <b>Control de Expiración Automática:</b> Gestión del ciclo de vida para marcar ofertas como 'EXPIRADO' cuando sobrepasan su tiempo límite.", styles['DocBullet']))

    story.append(Spacer(1, 3))
    story.append(Paragraph("5.2 Normalizaciones Realizadas (1FN a 4FN / DKNF)", styles['SubSectionTitle']))

    norm_data = [
        [Paragraph("<b>FORMA NORMAL</b>", styles['THeader']), Paragraph("<b>CRITERIO TEÓRICO APLICADO</b>", styles['THeader']), Paragraph("<b>RESOLUCIÓN Y GARANTÍA EN ECONOMY RP</b>", styles['THeader'])],
        [
            Paragraph("<b>1FN (Atomicidad)</b>", styles['TCellBold']),
            Paragraph("Cada celda contiene un único valor escalar indivisible; sin atributos multivaluados ni repetidos.", styles['TCell']),
            Paragraph("Se descompuso la lista de participantes en <code>detalles_transacciones</code> (una cuenta origen y una destino por fila) y los bienes en <code>items</code> y <code>negociaciones_tradeos</code>.", styles['TCell'])
        ],
        [
            Paragraph("<b>2FN (Dependencia Total)</b>", styles['TCellBold']),
            Paragraph("Cumple 1FN y ningún atributo no-clave depende parcialmente de claves compuestas.", styles['TCell']),
            Paragraph("Todas las tablas del sistema utilizan claves primarias simples subrogadas (<code>id_jornada</code>, <code>id_cuenta</code>, etc.), anulando dependencias parciales.", styles['TCell'])
        ],
        [
            Paragraph("<b>3FN (Sin Transitividad)</b>", styles['TCellBold']),
            Paragraph("Cumple 2FN y ningún atributo no-clave depende transitivamente de otro atributo no-clave.", styles['TCell']),
            Paragraph("En <code>jornadas_laborales</code> se sustituyó el cálculo dinámico de ganancia por <code>monto_pagado</code> inmutable, evitando depender de cambios futuros en la tarifa base de <code>empleos</code>.", styles['TCell'])
        ],
        [
            Paragraph("<b>FNBC / BCNF</b>", styles['TCellBold']),
            Paragraph("Todo determinante funcional en el esquema constituye formalmente una superclave.", styles['TCell']),
            Paragraph("Se eliminaron dependencias encubiertas soportando todas las relaciones estrictamente sobre claves primarias enteras o índices UNIQUE declarados.", styles['TCell'])
        ],
        [
            Paragraph("<b>4FN (Multivaluadas)</b>", styles['TCellBold']),
            Paragraph("No existen dependencias multivaluadas no triviales independientes entre sí.", styles['TCell']),
            Paragraph("El historial laboral, las cuentas monetarias y los ítems de un jugador residen en tablas independientes vinculadas unívocamente por la FK <code>id_jugador</code>.", styles['TCell'])
        ],
        [
            Paragraph("<b>DKNF (Dominio/Clave)</b>", styles['TCellBold']),
            Paragraph("Toda restricción es consecuencia directa de la definición de dominios y restricciones de clave.", styles['TCell']),
            Paragraph("Todas las reglas de negocio se imponen nativamente mediante restricciones CHECK, NOT NULL, UNIQUE y FOREIGN KEY.", styles['TCell'])
        ],
    ]

    norm_table = Table(norm_data, colWidths=[95, 180, 229])
    norm_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(KeepTogether([norm_table]))

    story.append(Spacer(1, 6))

    # =========================================================================
    # 7. SECCIÓN 6: PRUEBAS Y HALLAZGOS
    # =========================================================================
    story.append(Paragraph("6. Pruebas y Hallazgos", styles['MainSecTitle']))
    story.append(Paragraph("Para asegurar la robustez de la base de datos en MySQL (InnoDB), se ejecutó una suite exhaustiva de pruebas de inserción y manejo de errores:", styles['DocBody']))

    story.append(Paragraph("6.1 Errores Encontrados", styles['SubSectionTitle']))

    def make_error_entry(err_num, err_code, sql_text, fail_msg, analysis_text, fix_text, sql_fixed):
        content = [
            Paragraph(f"<b>ERROR {err_num}: {sql_text[:55]}... Error Code: {err_code}</b>", styles['TCellBold']),
            Spacer(1, 1),
            Paragraph(f"<b>Falla Reportada (Error):</b> {fail_msg}", styles['TCell']),
            Paragraph(f"<b>Análisis del Problema / Causa:</b> {analysis_text}", styles['TCell']),
            Paragraph(f"<b>Cómo se corrigió:</b> {fix_text}", styles['TCell']),
            Paragraph(f"<b>Código corregido / Verificación:</b><br/><code>{sql_fixed}</code>", styles['TCell'])
        ]
        t = Table([[content]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_BOX),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        return KeepTogether([t, Spacer(1, 3.5)])

    story.append(make_error_entry(
        1, "1064",
        "INSERT INTO servidores ... servidores",
        "Error Code: 1064. You have an error in your SQL syntax; check the manual near 'servidores' at line 1.",
        "Se incluyó accidentalmente la palabra residual 'servidores' al final de la instrucción SQL.",
        "Se eliminó la palabra residual dejando únicamente las instrucciones SQL válidas.",
        "INSERT INTO servidores (nombre, porcentaje_comision, limite_bienes_por_jugador, tiempo_enfriamiento_min) VALUES ('Servidor Prueba', 5.00, 10, 1);"
    ))

    story.append(make_error_entry(
        2, "1062",
        "INSERT INTO cuentas (id_servidor, tipo_cuenta...) VALUES (1, 'SISTEMA'...)",
        "Error Code: 1062. Duplicate entry '1' for key 'cuentas.uq_cuenta_sistema_por_servidor'",
        "El gestor bloqueó la inserción porque la cuenta de sistema para ese servidor ya existía.",
        "Se procedió a verificar la existencia de la cuenta ejecutando la consulta de lectura.",
        "SELECT * FROM cuentas WHERE id_servidor = 1 AND tipo_cuenta = 'SISTEMA';"
    ))

    story.append(make_error_entry(
        3, "1054",
        "INSERT INTO jugadores (id_servidor, nombre_usuario, nivel)...",
        "Error Code: 1054. Unknown column 'nivel' in 'field list'",
        "El gestor indica que se intentó guardar en la columna 'nivel', pero dicha columna no existe en la estructura física de la tabla jugadores.",
        "Se verificó la estructura de la tabla y se eliminó la columna nivel de la consulta de inserción.",
        "INSERT INTO jugadores (id_servidor, nombre_usuario, correo, contrasena_hash) VALUES (1, 'Usuario_Prueba', 'user@rp.com', 'hash123');"
    ))

    story.append(make_error_entry(
        4, "1452",
        "INSERT INTO jugadores (id_servidor, nombre_usuario...) VALUES (9999...)",
        "Error Code: 1452. Cannot add or update a child row: a foreign key constraint fails (fk_jugador_servidor).",
        "La regla de Foreign Key exige que un jugador no puede existir sin estar asignado a un servidor real registrado.",
        "Se captura dinámicamente el ID real del servidor creado previamente.",
        "INSERT INTO jugadores (id_servidor, nombre_usuario, correo, contrasena_hash) VALUES (@id_servidor_real, 'Jugador_Alpha', 'alpha@email.com', 'hash_secret_123');"
    ))

    story.append(make_error_entry(
        5, "1452",
        "INSERT INTO cuentas (id_jugador, id_servidor...) VALUES (9999...)",
        "Error Code: 1452. Cannot add or update a child row: a foreign key constraint fails (fk_cuenta_jugador).",
        "La base de datos buscó al jugador con id_jugador = 9999 y no lo encontró.",
        "Se utiliza la variable dinámica con el ID real asignado al jugador.",
        "INSERT INTO cuentas (id_jugador, id_servidor, tipo_cuenta, saldo_inicial, saldo_disponible) VALUES (@id_jugador_real, 1, 'PERSONAL', 5000.00, 5000.00);"
    ))

    story.append(make_error_entry(
        6, "1452",
        "INSERT INTO empleos (id_servidor, nombre_empleo...) VALUES (9999...)",
        "Error Code: 1452. Cannot add or update a child row: a foreign key constraint fails (fk_empleo_servidor).",
        "Al intentar asignarle el empleo a un servidor inexistente, MySQL no lo encuentra y bloquea la acción.",
        "Se ejecuta la consulta usando la variable dinámica para atrapar el ID real del servidor.",
        "INSERT INTO empleos (id_servidor, nombre_empleo, tarifa_base) VALUES (@id_servidor_real, 'Minero', 150.00);"
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("6.2 Pruebas de Validación de Integridad y Lógica Transaccional", styles['SubSectionTitle']))

    def make_test_entry(test_num, title, objective, sql_run, expected_res, cause_res, fix_sql):
        content = [
            Paragraph(f"<b>PRUEBA {test_num}: {title}</b>", styles['TCellBold']),
            Spacer(1, 1),
            Paragraph(f"<b>Objetivo de la Prueba:</b> {objective}", styles['TCell']),
            Paragraph(f"<b>Código de la prueba:</b><br/><code>{sql_run}</code>", styles['TCell']),
            Paragraph(f"<b>Resultado esperado:</b> {expected_res}", styles['TCell']),
            Paragraph(f"<b>Diagnóstico / Riesgo:</b> {cause_res}", styles['TCell']),
            Paragraph(f"<b>Código corregido / Blindaje:</b><br/><code>{fix_sql}</code>", styles['TCell'])
        ]
        t = Table([[content]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_BOX),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        return KeepTogether([t, Spacer(1, 3.5)])

    story.append(make_test_entry(
        "8", "Horas trabajadas negativas",
        "Comprobar que sp_pagar_jornada rechaza horas inválidas (cero o negativas).",
        "CALL sp_pagar_jornada(@ja, @emp, -10);",
        "Error de validación; ningún saldo cambia.",
        "Si no se controla, un valor negativo generaría montos pagados negativos, drenando saldo indebido al jugador.",
        "IF NEW.horas_trabajadas <= 0 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Las horas trabajadas deben ser mayores a cero'; END IF;"
    ))

    story.append(make_test_entry(
        "9", "Robo de ítems en un tradeo",
        "Verificar que un jugador solo pueda ofrecer ítems que le pertenecen legítimamente.",
        "CALL sp_abrir_negociacion(@ja, @jb, @item_c, NULL, 0, 0, 10); -- @item_c pertenece a C",
        "Error al abrir la negociación, y el bien sigue perteneciendo a su dueño original.",
        "Garantiza que ningún bien pueda ser negociado por un tercero no autorizado.",
        "IF NOT EXISTS (SELECT 1 FROM items WHERE id_item = p_id_item_j1 AND id_jugador = p_id_jugador_1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El item ofrecido no le pertenece al jugador 1'; END IF;"
    ))

    story.append(make_test_entry(
        "10", "Confirmar una negociación ya expirada",
        "Comprobar que no se puede confirmar un tradeo fuera de tiempo.",
        "CALL sp_confirmar_tradeo(@id_negociacion_expirada, @ja);",
        "Error 'negociación expirada' y transición del estado a 'EXPIRADO'.",
        "Evita que se ejecuten tratos obsoletos cuyos términos ya no son válidos para ambas partes.",
        "IF v_fecha_exp < NOW() THEN UPDATE negociaciones_tradeos SET estado = 'EXPIRADO' WHERE id_negociacion = p_id; SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La negociacion ya expiro'; END IF;"
    ))

    story.append(make_test_entry(
        "11", "Un tradeo salta el límite de bienes",
        "Verificar que el límite del servidor (ej. 2 bienes) también se respeta cuando se reciben ítems por tradeo.",
        "CALL sp_confirmar_tradeo(@neg, @jd); -- D ya tiene 2 bienes",
        "El control falla con 'límite máximo de bienes'; el tradeo se cancela y D sigue con 2 ítems.",
        "Evita el acaparamiento de activos en una sola cuenta mediante transferencias entre jugadores.",
        "IF v_cant_j1 - (v_item_j1 IS NOT NULL) + (v_item_j2 IS NOT NULL) > v_limite THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El tradeo excede el limite de bienes'; END IF;"
    ))

    story.append(make_test_entry(
        "12", "Tradeo de un jugador consigo mismo",
        "Comprobar que no se puede abrir una negociación donde ambos participantes son el mismo jugador.",
        "CALL sp_abrir_negociacion(@ja, @ja, NULL, NULL, 100, 0, 10);",
        "Error al abrir la negociación y bloqueo de la inserción.",
        "Evita el auto-bloqueo de sesiones y el colapso de la máquina de estados de doble confirmación.",
        "CONSTRAINT chk_negociacion_distintos CHECK (id_jugador_1 <> id_jugador_2)"
    ))

    story.append(Spacer(1, 6))

    # =========================================================================
    # 8. SECCIÓN 7: DEFENSA TÉCNICA Y SUSTENTACIÓN DEL ESQUEMA
    # =========================================================================
    story.append(Paragraph("7. Defensa Técnica y Sustentación del Esquema", styles['MainSecTitle']))
    story.append(Paragraph(
        "La arquitectura del esquema DDL de Economy RP en MySQL 8.0 (InnoDB) no es un repositorio pasivo, sino un motor transaccional gobernado por reglas estrictas de integridad relacional. A nivel de defensa técnica, se sustenta el comportamiento del sistema respondiendo a las preguntas fundamentales de flujo de información:",
        styles['DocBody']
    ))

    story.append(Paragraph("<b>1. ¿Por qué el modelo restringe el traspaso de bienes en ciertas condiciones?</b>", styles['SubSectionTitle']))
    story.append(Paragraph(
        "El modelo bloquea de forma intransigente la transferencia de cualquier ítem que registre gravámenes (<code>tiene_deuda = TRUE</code>, RN004) o cuyo titular no coincida con el operador autenticado (<code>items.id_jugador != emisor</code>, RN002). Asimismo, el motor rechaza la transacción si el receptor ya alcanzó su cuota máxima de inventario (RN007) o si no dispone de liquidez suficiente para cubrir el importe acordado más el 5% de comisión tributaria (RN006). Estas restricciones protegen a la comunidad de estafas, venta fraudulenta de vehículos embargados y sobregiros contables.",
        styles['DocBody']
    ))

    story.append(Paragraph("<b>2. ¿Por qué el modelo permite la emisión de dinero sólo a través de canales específicos?</b>", styles['SubSectionTitle']))
    story.append(Paragraph(
        "El esquema prohíbe la creación de dinero 'de la nada' mediante inserciones directas en cuentas personales. Todo flujo de entrada a la economía debe ser respaldado por una jornada laboral completada (<code>jornadas_laborales</code>) y registrado como un débito formal a la cuenta oficial de Tesorería del SISTEMA (RN005). Esto asegura que la masa monetaria en circulación sea 100% auditable mediante la suma simétrica de débitos y créditos en <code>detalles_transacciones</code>.",
        styles['DocBody']
    ))

    story.append(Paragraph("<b>3. ¿Por qué se implementó Inmutabilidad Contable por Partida Doble?</b>", styles['SubSectionTitle']))
    story.append(Paragraph(
        "En un entorno financiero virtual, la modificación arbitraria de saldos mediante sentencias <code>UPDATE</code> destruye la trazabilidad histórica. Al estructurar <code>transacciones</code> y <code>detalles_transacciones</code> bajo un patrón de sólo adición (*append-only*), cualquier ajuste administrativo debe realizarse mediante un nuevo asiento compensatorio, protegiendo la fe pública y la confianza de los participantes.",
        styles['DocBody']
    ))

    story.append(Paragraph("<b>4. Garantía de Propiedades ACID en el Motor Relacional:</b>", styles['SubSectionTitle']))
    story.append(Paragraph("• <b>Atomicidad (A):</b> Todas las operaciones de intercambio P2P y liquidación laboral se ejecutan en transacciones explícitas con manejadores <code>EXIT HANDLER FOR SQLEXCEPTION ROLLBACK</code>, garantizando que todo se aplique en su totalidad o se revierta por completo.", styles['DocBullet']))
    story.append(Paragraph("• <b>Consistencia (C):</b> El cumplimiento riguroso de 1FN a 4FN, las llaves foráneas y las restricciones <code>CHECK</code> aseguran que la base de datos nunca quede en un estado inválido.", styles['DocBullet']))
    story.append(Paragraph("• <b>Aislamiento (I):</b> Las consultas de verificación emplean bloqueos pesimistas (<code>SELECT ... FOR UPDATE</code>), evitando condiciones de carrera en operaciones concurrentes.", styles['DocBullet']))
    story.append(Paragraph("• <b>Durabilidad (D):</b> Los registros persistidos en MySQL con el motor transaccional InnoDB garantizan la recuperación total ante fallos de hardware o caídas de red.", styles['DocBullet']))

    story.append(Spacer(1, 6))

    # =========================================================================
    # 9. SECCIÓN 8: ANEXO DE MODIFICACIONES Y RESPUESTA A RETROALIMENTACIÓN
    # =========================================================================
    story.append(Paragraph("8. Anexo: Modificaciones y Resoluciones tras Retroalimentación Sincrónica", styles['MainSecTitle']))
    story.append(Paragraph("A continuación se sintetizan formalmente las mejoras aplicadas a partir de las observaciones del docente asesor en la sesión sincrónica:", styles['DocBody']))

    anexo_data = [
        [Paragraph("<b>OBSERVACIÓN DOCENTE</b>", styles['THeader']), Paragraph("<b>RIESGO RELACIONAL DIAGNOSTICADO</b>", styles['THeader']), Paragraph("<b>SOLUCIÓN DDL IMPLEMENTADA</b>", styles['THeader'])],
        [
            Paragraph("<b>Punto 1: Estructura de Ítems y Posesión Rígida</b>", styles['TCellBold']),
            Paragraph("FK <code>id_jugador</code> rígida (1:N) impedía que los bienes pertenecieran a concesionarios o quedaran bloqueados en tradeo sin perder al dueño legítimo.", styles['TCell']),
            Paragraph("Se modularizó con <code>id_jugador INT NULL</code> y se incorporaron <code>estado_custodia CHECK ('PERSONAL','EMBARGADO','EN_TRADE')</code> y <code>tipo_propietario CHECK ('JUGADOR','CONCESIONARIO','SISTEMA')</code>.", styles['TCell'])
        ],
        [
            Paragraph("<b>Punto 2: Cardinalidad de Cuentas Financieras</b>", styles['TCellBold']),
            Paragraph("Restricción <code>UNIQUE</code> en <code>id_jugador</code> forzaba relación 1:1, impidiendo cuentas múltiples (ahorro, comercial, corporativa).", styles['TCell']),
            Paragraph("Se eliminó la restricción <code>UNIQUE</code> en <code>cuentas.id_jugador</code>, habilitando formalmente cardinalidad 1:N clasificada mediante <code>tipo_cuenta CHECK (...)</code>.", styles['TCell'])
        ],
        [
            Paragraph("<b>Punto 3: Atomicidad y Simetría Contable</b>", styles['TCellBold']),
            Paragraph("Riesgo de descuadre contable si la simetría débito/crédito dependía únicamente de inserciones externas.", styles['TCell']),
            Paragraph("Se blindó mediante bloques transaccionales atómicos ACID con bloqueos pesimistas en InnoDB, asegurando <code>SUM(Débitos) = SUM(Créditos)</code> con ROLLBACK automático ante cualquier falla.", styles['TCell'])
        ],
        [
            Paragraph("<b>Punto 4: Estandarización de Nomenclatura</b>", styles['TCellBold']),
            Paragraph("Uso de prefijo <code>T_</code> y singularidades inconsistentes.", styles['TCell']),
            Paragraph("Se normalizó el DDL completo eliminando el prefijo <code>T_</code> y estandarizando nombres de tablas en plural (<code>servidores</code>, <code>jugadores</code>, etc.) en <i>snake_case</i> minúscula.", styles['TCell'])
        ],
    ]

    anexo_table = Table(anexo_data, colWidths=[120, 180, 204])
    anexo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(KeepTogether([anexo_table]))

    story.append(Spacer(1, 14))

    # Firmas
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Miguel Ángel Cardona Agudelo</b><br/>Desarrollo DB & DDL", styles['TCellCenter']),
            Paragraph("____________________________<br/><b>Luisa María López Orrego</b><br/>Normalización & Calidad", styles['TCellCenter']),
            Paragraph("____________________________<br/><b>Jorge Luis Ordoñez Ávila</b><br/>Pruebas & Auditoría", styles['TCellCenter']),
        ]
    ]
    sig_table = Table(sig_data, colWidths=[168, 168, 168])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(KeepTogether([sig_table]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generado con éxito: {pdf_filename}")

if __name__ == "__main__":
    build_pdf()
