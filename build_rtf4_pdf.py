import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Canvas de dos pasadas para calcular dinámicamente el número total de páginas
    e imprimir encabezados y pies de página institucionales elegantes.
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
        self.setFillColor(colors.HexColor("#4A5568"))

        # Encabezado institucional
        self.drawString(54, 752, "INSTITUCIÓN UNIVERSITARIA PASCUAL BRAVO • BASES DE DATOS I")
        self.drawRightString(612 - 54, 752, "RTF4 — IMPLEMENTACIÓN Y REFINAMIENTO DDL")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(54, 745, 612 - 54, 745)

        # Pie de página institucional
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
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    # Paleta de Colores Institucional
    NAVY = colors.HexColor("#1B365D")
    SLATE = colors.HexColor("#2C3E50")
    DARK = colors.HexColor("#2D3748")
    MUTED = colors.HexColor("#64748B")
    BG_LIGHT = colors.HexColor("#F8FAFC")
    BG_HEADER = colors.HexColor("#E2E8F0")
    BORDER_CLR = colors.HexColor("#CBD5E1")

    # Tipografías y Estilos
    styles.add(ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=NAVY,
        alignment=1
    ))

    styles.add(ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=SLATE,
        alignment=1
    ))

    styles.add(ParagraphStyle(
        'SecTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=14.5,
        textColor=NAVY,
        spaceBefore=11,
        spaceAfter=4,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        'SubSecTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=SLATE,
        spaceBefore=7,
        spaceAfter=2.5,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.3,
        leading=11.4,
        textColor=DARK,
        spaceAfter=3
    ))

    styles.add(ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.3,
        leading=11.4,
        textColor=DARK,
        leftIndent=10,
        spaceAfter=2
    ))

    styles.add(ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.6,
        leading=9.5,
        textColor=NAVY,
        alignment=1
    ))

    styles.add(ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.4,
        leading=9.2,
        textColor=DARK
    ))

    styles.add(ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.4,
        leading=9.2,
        textColor=NAVY
    ))

    styles.add(ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.4,
        leading=9.2,
        textColor=DARK,
        alignment=1
    ))

    story = []

    # =========================================================================
    # 1. PORTADA INSTITUCIONAL
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("INSTITUCIÓN UNIVERSITARIA PASCUAL BRAVO", ParagraphStyle('H1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, leading=17, textColor=NAVY, alignment=1)))
    story.append(Paragraph("FACULTAD DE INGENIERÍA • DEPARTAMENTO DE SISTEMAS", ParagraphStyle('H2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=12, textColor=MUTED, alignment=1)))
    story.append(Paragraph("BASES DE DATOS I", ParagraphStyle('H3', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=13, textColor=SLATE, alignment=1)))
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1.5, color=NAVY, spaceBefore=0, spaceAfter=15))

    story.append(Paragraph("INFORME TÉCNICO DE AULA RTF4", styles['CoverSubtitle']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("IMPLEMENTACIÓN Y REFINAMIENTO DEL MODELO LÓGICO DDL", styles['CoverTitle']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Motor Relacional de Gestión Económica, Trazabilidad Contable e Inmutabilidad Transaccional<br/>para Servidores de Rol GTA (Economy RP)", ParagraphStyle('Desc', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=9, leading=12, textColor=DARK, alignment=1)))
    
    story.append(Spacer(1, 20))

    meta_data = [
        [Paragraph("<b>Proyecto de Aula:</b>", styles['TableCellBold']), Paragraph("Economy RP (Motor Económico Relacional)", styles['TableCell'])],
        [Paragraph("<b>Equipo de Trabajo:</b>", styles['TableCellBold']), Paragraph("Grupo 4", styles['TableCell'])],
        [Paragraph("<b>Docente Asesor:</b>", styles['TableCellBold']), Paragraph("Juan Camilo Palacio Alcaraz", styles['TableCell'])],
        [Paragraph("<b>Integrantes:</b>", styles['TableCellBold']), Paragraph("• Miguel Ángel Cardona Agudelo<br/>• Luisa María López Orrego<br/>• Jorge Luis Ordoñez Ávila", styles['TableCell'])],
        [Paragraph("<b>Materia / Semestre:</b>", styles['TableCellBold']), Paragraph("Bases de Datos I • Semestre 2026-2", styles['TableCell'])],
        [Paragraph("<b>Fecha de Entrega:</b>", styles['TableCellBold']), Paragraph("03 de Octubre de 2026", styles['TableCell'])]
    ]
    meta_table = Table(meta_data, colWidths=[130, 374])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.8, BORDER_CLR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 15))

    rubric_summary = [
        [Paragraph("<b>RÚBRICA DE EVALUACIÓN OFICIAL RTF4 (100% PONDERADO)</b>", styles['TableHeader']), Paragraph("<b>PESO</b>", styles['TableHeader'])],
        [Paragraph("1. Evolución y Refinamiento del Modelo Lógico (Antes vs. Después)", styles['TableCell']), Paragraph("<b>25% (1.25)</b>", styles['TableCellCenter'])],
        [Paragraph("2. Definición y Estructura del Esquema DDL Tabular", styles['TableCell']), Paragraph("<b>25% (1.25)</b>", styles['TableCellCenter'])],
        [Paragraph("3. Informe de Mejoras y Proceso de Normalización (1FN, 2FN, 3FN, BCNF, 4FN, DKNF)", styles['TableCell']), Paragraph("<b>20% (1.00)</b>", styles['TableCellCenter'])],
        [Paragraph("4. Pruebas Estructurales, Hallazgos y Manejo de Errores de Motor SGBD", styles['TableCell']), Paragraph("<b>20% (1.00)</b>", styles['TableCellCenter'])],
        [Paragraph("5. Estructura, Formato Institucional y Defensa Técnica del Modelo", styles['TableCell']), Paragraph("<b>10% (0.50)</b>", styles['TableCellCenter'])],
    ]
    rubric_table = Table(rubric_summary, colWidths=[404, 100])
    rubric_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
        ('BOX', (0, 0), (-1, -1), 0.8, BORDER_CLR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
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
    story.append(Paragraph("1. Objetivo de la Entrega", styles['SecTitle']))
    story.append(HRFlowable(width="100%", thickness=0.8, color=NAVY, spaceBefore=0, spaceAfter=5))
    story.append(Paragraph(
        "El objetivo principal de esta fase es la materialización y refinamiento del modelo lógico relacional en el Sistema Gestor de Bases de Datos (MySQL 8.0 con motor transaccional InnoDB), a partir del diseño conceptual previo. Se busca implementar y certificar la robustez del esquema DDL físico para validar la integridad referencial, suprimir inconsistencias y asegurar el estricto cumplimiento de las reglas del negocio de rol, resolviendo fallas críticas tales como:",
        styles['BodyDark']
    ))
    story.append(Paragraph("• <b>Inconsistencias en tipos de datos:</b> Estandarización a <code>DECIMAL(12,2)</code> para evitar pérdidas de precisión por coma flotante.", styles['BulletText']))
    story.append(Paragraph("• <b>Definición rigurosa de claves primarias y foráneas:</b> Eliminación de claves compuestas ambiguas y soporte de llaves subrogadas.", styles['BulletText']))
    story.append(Paragraph("• <b>Restricciones de integridad y dominio (CHECKs):</b> Blindaje de estados y tipos contables para evitar datos huérfanos o no tipificados.", styles['BulletText']))
    story.append(Paragraph("• <b>Consistencia transaccional y atomicidad (ACID):</b> Asegurar que en negociaciones de intercambio P2P y liquidación laboral ningún bien ni saldo quede duplicado o en el limbo.", styles['BulletText']))
    story.append(Paragraph("• <b>Inmutabilidad en el libro mayor contable:</b> Estructuración de un historial de transacciones <i>append-only</i> con partida doble.", styles['BulletText']))
    story.append(Paragraph("• <b>Automatización de políticas económicas:</b> Control en tiempo real de límites de posesión por jugador, periodos de enfriamiento laboral, tasas de drenaje anti-inflacionario y detección reactiva de bancarrota.", styles['BulletText']))

    story.append(Spacer(1, 3))

    # =========================================================================
    # 3. SECCIÓN 2: REGLAS DE NEGOCIO (RN001 - RN012)
    # =========================================================================
    story.append(Paragraph("2. Catálogo Oficial de Reglas de Negocio (RN001 - RN012)", styles['SecTitle']))
    story.append(HRFlowable(width="100%", thickness=0.8, color=NAVY, spaceBefore=0, spaceAfter=5))
    story.append(Paragraph("A continuación se detallan las reglas de negocio formalizadas para el dominio económico del servidor de rol GTA (Economy RP), expresando su condición lógica y su mecanismo de implementación exclusivo en la base de datos:", styles['BodyDark']))

    rn_data = [
        [Paragraph("<b>CÓD.</b>", styles['TableHeader']), Paragraph("<b>NOMBRE</b>", styles['TableHeader']), Paragraph("<b>DESCRIPCIÓN FUNCIONAL</b>", styles['TableHeader']), Paragraph("<b>FÓRMULA / CONDICIÓN</b>", styles['TableHeader']), Paragraph("<b>IMPACTO DDL / SGBD</b>", styles['TableHeader'])],
        [
            Paragraph("<b>RN001</b>", styles['TableCellBold']),
            Paragraph("Registro Único Laboral", styles['TableCellBold']),
            Paragraph("Al completar una jornada, el sistema calcula y acredita automáticamente la ganancia a la cuenta del jugador.", styles['TableCell']),
            Paragraph("Ganancia = Tarifa_base × Horas", styles['TableCellCenter']),
            Paragraph("Tabla <code>jornadas_laborales</code>, PK subrogada <code>id_jornada</code> y columna histórica inmutable <code>monto_pagado</code>.", styles['TableCell'])
        ],
        [
            Paragraph("<b>RN002</b>", styles['TableCellBold']),
            Paragraph("Propiedad Única y Exclusiva", styles['TableCellBold']),
            Paragraph("Un bien físico (vehículo con placa, propiedad) solo puede pertenecer a un único personaje a la vez.", styles['TableCell']),
            Paragraph("Propietario = 1 por cada Bien activo", styles['TableCellCenter']),
            Paragraph("Clave foránea atómica <code>items.id_jugador</code> con integridad referencial directa (1:N estricto).", styles['TableCell'])
        ],
        [
            Paragraph("<b>RN003</b>", styles['TableCellBold']),
            Paragraph("Inmutabilidad del Historial", styles['TableCellBold']),
            Paragraph("Toda transacción financiera o comercial registrada no puede ser editada ni eliminada bajo ninguna circunstancia.", styles['TableCell']),
            Paragraph("Política Append-Only (Sin UPDATE / DELETE)", styles['TableCellCenter']),
            Paragraph("Tablas <code>transacciones</code> y <code>detalles_transacciones</code> inmutables protegidas por disparadores.", styles['TableCell'])
        ],
        [
            Paragraph("<b>RN004</b>", styles['TableCellBold']),
            Paragraph("Restricción por Deuda / Embargo", styles['TableCellBold']),
            Paragraph("Un bien no puede transferirse si posee deuda activa, embargo o cuotas financieras pendientes.", styles['TableCell']),
            Paragraph("Restriccion = 'Ninguna'<br/>(tiene_deuda = FALSE)", styles['TableCellCenter']),
            Paragraph("Columna <code>tiene_deuda BOOLEAN NOT NULL DEFAULT FALSE</code> y validación en procedimiento de tradeo.", styles['TableCell'])
        ],
        [
            Paragraph("<b>RN005</b>", styles['TableCellBold']),
            Paragraph("Trazabilidad de Creación de Dinero", styles['TableCellBold']),
            Paragraph("Todo dinero inyectado (salarios, bonos iniciales) debe originarse formalmente de la cuenta oficial 'SISTEMA'.", styles['TableCell']),
            Paragraph("Origen = Cuenta_Sistema si Emisor = Sistema", styles['TableCellCenter']),
            Paragraph("<code>cuentas.tipo_cuenta = 'SISTEMA'</code> (id_jugador NULL) y asiento de partida doble en detalles.", styles['TableCell'])
        ],
        [
            Paragraph("<b>RN006</b>", styles['TableCellBold']),
            Paragraph("Comisión por Transferencia", styles['TableCellBold']),
            Paragraph("Toda compraventa o intercambio descuenta una comisión porcentual que se acredita a la Tesorería como drenaje anti-inflación.", styles['TableCell']),
            Paragraph("Comisión = Monto × Porcentaje_Comisión", styles['TableCellCenter']),
            Paragraph("Atributo <code>servidores.porcentaje_comision</code> y asiento secundario de drenaje fiscal en detalles.", styles['TableCell'])
        ],
        [
            Paragraph("<b>RN007</b>", styles['TableCellBold']),
            Paragraph("Límite Máximo de Propiedades", styles['TableCellBold']),
            Paragraph("Un jugador no puede registrar más bienes que el tope máximo parametrizado por el administrador.", styles['TableCell']),
            Paragraph("COUNT(Items) <= Limite_Bienes_Servidor", styles['TableCellCenter']),
            Paragraph("Atributo <code>servidores.limite_bienes_por_jugador</code> y control de aforo en inserción/tradeo.", styles['TableCell'])
        ],
        [
            Paragraph("<b>RN008</b>", styles['TableCellBold']),
            Paragraph("Enfriamiento Laboral (Cooldown)", styles['TableCellBold']),
            Paragraph("Un jugador debe cumplir un tiempo mínimo de descanso entre turnos del mismo empleo para evitar explotación.", styles['TableCell']),
            Paragraph("Hora_Actual - Hora_Ultima >= Tiempo_Cooldown", styles['TableCellCenter']),
            Paragraph("Atributo <code>servidores.tiempo_enfriamiento_min</code> e inspección temporal en inserción laboral.", styles['TableCell'])
        ],
        [
            Paragraph("<b>RN009</b>", styles['TableCellBold']),
            Paragraph("Penalización por Bancarrota", styles['TableCellBold']),
            Paragraph("Si el saldo disponible no cubre obligaciones o queda en negativo, el jugador pasa a estado 'BANCARROTA', bloqueando operaciones.", styles['TableCell']),
            Paragraph("Saldo < 0 => Estado = 'BANCARROTA'", styles['TableCellCenter']),
            Paragraph("Restricción <code>CHECK (estado IN ('ACTIVO','BANCARROTA','SUSPENDIDO'))</code> en <code>jugadores</code>.", styles['TableCell'])
        ],
        [
            Paragraph("<b>RN010</b>", styles['TableCellBold']),
            Paragraph("Confirmación Doble en Tradeo", styles['TableCellBold']),
            Paragraph("Ambas partes deben confirmar explícitamente los términos. Cualquier modificación reinicia los candados de confirmación.", styles['TableCell']),
            Paragraph("Ejecutar si (conf_j1 = TRUE AND conf_j2 = TRUE)", styles['TableCellCenter']),
            Paragraph("Banderas booleanas <code>confirmacion_j1</code> y <code>confirmacion_j2</code> en <code>negociaciones_tradeos</code>.", styles['TableCell'])
        ],
        [
            Paragraph("<b>RN011</b>", styles['TableCellBold']),
            Paragraph("Límite Diario de Tradeos", styles['TableCellBold']),
            Paragraph("Un operador no puede ejecutar más intercambios exitosos al día que el cupo configurado, evitando lavado de activos.", styles['TableCell']),
            Paragraph("COUNT(Tradeos_Hoy) <= limite_tradeos_diarios", styles['TableCellCenter']),
            Paragraph("Columna <code>servidores.limite_tradeos_diarios</code> y agregación temporal sobre <code>DATE(fecha_hora)</code>.", styles['TableCell'])
        ],
        [
            Paragraph("<b>RN012</b>", styles['TableCellBold']),
            Paragraph("Tradeo Único Simultáneo", styles['TableCellBold']),
            Paragraph("Un jugador solo puede tener una negociación abierta a la vez, impidiendo comprometer saldos o ítems en paralelo.", styles['TableCell']),
            Paragraph("COUNT(Negociaciones_Activas) <= 1", styles['TableCellCenter']),
            Paragraph("Restricción de dominio sobre el ciclo de vida <code>CHECK (estado IN (...))</code> en negociaciones.", styles['TableCell'])
        ],
    ]

    rn_table = Table(rn_data, colWidths=[36, 80, 164, 104, 120])
    rn_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
        ('BOX', (0, 0), (-1, -1), 0.8, BORDER_CLR),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(rn_table)

    story.append(Spacer(1, 6))

    # =========================================================================
    # 4. SECCIÓN 3: EVOLUCIÓN DEL MODELO LÓGICO (ANTES VS. DESPUÉS)
    # =========================================================================
    story.append(Paragraph("3. Evolución del Modelo Lógico (Antes vs. Después)", styles['SecTitle']))
    story.append(HRFlowable(width="100%", thickness=0.8, color=NAVY, spaceBefore=0, spaceAfter=5))

    story.append(Paragraph("3.1 Diagnóstico de Fallas en el Modelo Lógico Inicial (Antes)", styles['SubSecTitle']))
    story.append(Paragraph(
        "En la fase conceptual y lógica preliminar (RTF3), el modelo presentaba severas limitaciones estructurales que impedían su ejecución eficiente en un SGBD relacional de producción. Entre las fallas identificadas se destacan:",
        styles['BodyDark']
    ))
    story.append(Paragraph("• <b>Violación de 1FN por atributos multivaluados:</b> En <code>Transaccion</code> se pretendía registrar cadenas de texto como <code>Usuarios_Involucrados = 'Emisor: Carlos, Receptor: Ana'</code> y <code>Bienes_Afectados = 'Vehículo, Propiedad'</code>, imposibilitando búsquedas relacionales o integridad referencial.", styles['BulletText']))
    story.append(Paragraph("• <b>Clave compuesta ambigua en jornadas (2FN):</b> Se intentó definir <code>(id_jugador, id_empleo)</code> como PK compuesta, bloqueando a los jugadores de realizar más de un turno laboral en el mismo oficio a lo largo del tiempo (Error 1062 Duplicate Key).", styles['BulletText']))
    story.append(Paragraph("• <b>Restricción de unicidad rígida en cuentas (1:1):</b> En <code>T_Cuenta</code> se definía <code>id_jugador UNIQUE</code>, impidiendo que un operador administrara cuentas de ahorro, corrientes o comerciales, además de bloquear la cuenta central de Tesorería por falta de un titular físico.", styles['BulletText']))
    story.append(Paragraph("• <b>Falta de atomicidad en permutas:</b> El tradeo original solo permitía transferencias unilaterales (1 ítem por dinero), sin soporte para intercambios cruzados simultáneos de activos y fondos.", styles['BulletText']))
    story.append(Paragraph("• <b>Nomenclatura no normalizada:</b> Uso redundante del prefijo <code>T_</code> y nombres en singular que dificultaban el estándar relacional.", styles['BulletText']))

    story.append(Spacer(1, 3))
    story.append(Paragraph("3.2 Modelo Lógico Corregido y Refinado (Después)", styles['SubSecTitle']))
    story.append(Paragraph(
        "Tras la implementación en el SGBD MySQL (InnoDB), el esquema DDL se consolidó resolviendo las fallas conceptuales previas mediante las siguientes transformaciones estructurales:",
        styles['BodyDark']
    ))

    evol_data = [
        [Paragraph("<b>ENTIDAD</b>", styles['TableHeader']), Paragraph("<b>DISEÑO INICIAL (RTF3 / ANTES)</b>", styles['TableHeader']), Paragraph("<b>DISEÑO CORREGIDO (RTF4 / DESPUÉS)</b>", styles['TableHeader']), Paragraph("<b>MEJORA TÉCNICA APORTADA</b>", styles['TableHeader'])],
        [
            Paragraph("<b>servidores</b>", styles['TableCellBold']),
            Paragraph("Contenedor conceptual sin atributos claros de gobernanza.", styles['TableCell']),
            Paragraph("Tabla con <code>porcentaje_comision</code>, <code>limite_bienes</code>, <code>cooldown_min</code> y <code>limite_tradeos_diarios</code>.", styles['TableCell']),
            Paragraph("Centraliza la parametrización de RN006, RN007, RN008 y RN011.", styles['TableCell'])
        ],
        [
            Paragraph("<b>jugadores</b>", styles['TableCellBold']),
            Paragraph("Atributos genéricos, credenciales en texto plano, sin restricción de estado.", styles['TableCell']),
            Paragraph("PK simple, FK a servidores, username/correo únicos, hash criptográfico y <code>CHECK (estado IN (...))</code>.", styles['TableCell']),
            Paragraph("Integridad referencial, seguridad de acceso y soporte formal de estados judiciales (RN009).", styles['TableCell'])
        ],
        [
            Paragraph("<b>empleos</b>", styles['TableCellBold']),
            Paragraph("Mezclaba horas trabajadas con la definición del oficio.", styles['TableCell']),
            Paragraph("Catálogo desacoplado con <code>id_empleo PK</code>, FK a servidor, nombre y <code>tarifa_base DECIMAL(10,2)</code>.", styles['TableCell']),
            Paragraph("Desacoplamiento total entre la oferta laboral y los turnos individuales ejecutados.", styles['TableCell'])
        ],
        [
            Paragraph("<b>jornadas_laborales</b>", styles['TableCellBold']),
            Paragraph("Planteada con PK compuesta (jugador + empleo) y ganancia calculada dinámica.", styles['TableCell']),
            Paragraph("PK subrogada <code>id_jornada</code>, FKs independientes, horas trabajadas y <code>monto_pagado</code> inmutable.", styles['TableCell']),
            Paragraph("Cumplimiento estricto de 2FN y 3FN; historial laboral auditable sin desincronización de tarifas.", styles['TableCell'])
        ],
        [
            Paragraph("<b>cuentas</b>", styles['TableCellBold']),
            Paragraph("Atada 1:1 rígidamente a Jugador con UNIQUE. Sin cuenta oficial del sistema.", styles['TableCell']),
            Paragraph("PK simple, FK a jugador (nullable), FK a servidor, <code>tipo_cuenta CHECK ('PERSONAL','SISTEMA')</code>.", styles['TableCell']),
            Paragraph("Habilita la Tesorería Central (RN005) y elimina la restricción que impedía cuentas múltiples (1:N).", styles['TableCell'])
        ],
        [
            Paragraph("<b>items</b>", styles['TableCellBold']),
            Paragraph("Categoría como texto libre, fechas redundantes y sin control de deudas.", styles['TableCell']),
            Paragraph("PK simple, FK a jugador, precio tasado, fecha adquisición, flag <code>tiene_deuda</code> y estado de custodia.", styles['TableCell']),
            Paragraph("Cumple RN002 (un dueño por bien) y RN004 (bloqueo por gravamen o embargo).", styles['TableCell'])
        ],
        [
            Paragraph("<b>negociaciones_tradeos</b>", styles['TableCellBold']),
            Paragraph("Inexistente; se pretendía ejecutar el intercambio directamente sobre transacciones.", styles['TableCell']),
            Paragraph("Mesa bilateral simétrica con <code>id_item_j1/j2</code>, <code>monto_j1/j2</code>, doble confirmación y expiración.", styles['TableCell']),
            Paragraph("Garantiza la máquina de estados de negociación (RN010, RN012) con soporte de permuta cruzada.", styles['TableCell'])
        ],
        [
            Paragraph("<b>transacciones</b>", styles['TableCellBold']),
            Paragraph("Sobrecargada con listas de texto concatenadas (usuarios y bienes en un campo).", styles['TableCell']),
            Paragraph("Cabecera inmutable de libro mayor con tipo de operación, monto nominal, fecha_hora y estado.", styles['TableCell']),
            Paragraph("Estructura de auditoría contable de sólo adición (*append-only*) inalterable (RN003).", styles['TableCell'])
        ],
        [
            Paragraph("<b>detalles_transacciones</b>", styles['TableCellBold']),
            Paragraph("Inexistente en el diseño preliminar.", styles['TableCell']),
            Paragraph("Asientos contables por partida doble con cuenta_origen, cuenta_destino, tipo de movimiento y monto.", styles['TableCell']),
            Paragraph("Trazabilidad contable estricta al centavo y cumplimiento de 1FN.", styles['TableCell'])
        ],
    ]

    evol_table = Table(evol_data, colWidths=[85, 130, 159, 130])
    evol_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
        ('BOX', (0, 0), (-1, -1), 0.8, BORDER_CLR),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(evol_table)

    story.append(Spacer(1, 6))

    # =========================================================================
    # 5. SECCIÓN 4: ESTRUCTURA TABULAR DEL ESQUEMA DDL
    # =========================================================================
    story.append(Paragraph("4. Estructura del Esquema Tabular (DDL)", styles['SecTitle']))
    story.append(HRFlowable(width="100%", thickness=0.8, color=NAVY, spaceBefore=0, spaceAfter=5))
    story.append(Paragraph("A continuación se documenta de forma exhaustiva y rigurosa la estructura tabular de las entidades físicas en el motor MySQL (InnoDB), especificando tipos de datos, nulidad, claves, valores por defecto y su justificación técnica vinculada a las reglas de negocio:", styles['BodyDark']))

    def make_ddl_table(title, headers, rows, col_w):
        table_data = [[Paragraph(f"<b>{h}</b>", styles['TableHeader']) for h in headers]]
        for r in rows:
            formatted_row = []
            for idx, c in enumerate(r):
                if idx == 0:
                    formatted_row.append(Paragraph(f"<b>{c}</b>", styles['TableCellBold']))
                elif idx in (1, 2, 3):
                    formatted_row.append(Paragraph(c, styles['TableCellCenter']))
                else:
                    formatted_row.append(Paragraph(c, styles['TableCell']))
            table_data.append(formatted_row)
        
        t = Table(table_data, colWidths=col_w)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
            ('BOX', (0, 0), (-1, -1), 0.8, BORDER_CLR),
            ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 1.8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
            ('LEFTPADDING', (0, 0), (-1, -1), 3.5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3.5),
        ]))
        return KeepTogether([
            Paragraph(f"<b>Tabla: {title}</b>", styles['SubSecTitle']),
            Spacer(1, 1),
            t,
            Spacer(1, 4)
        ])

    ddl_headers = ["COLUMNA", "TIPO DE DATO", "NULO", "CLAVE / CONSTRAINT", "DEFAULT", "DESCRIPCIÓN Y REGLA VINCULADA"]
    col_w_ddl = [95, 80, 32, 105, 52, 140]

    # 1. servidores
    story.append(make_ddl_table(
        "servidores (Configuración y Gobernanza Económica)",
        ddl_headers,
        [
            ["id_servidor", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Identificador único de la instancia del servidor."],
            ["nombre", "VARCHAR(100)", "NO", "N/A", "N/A", "Nombre institucional del servidor de rol."],
            ["porcentaje_comision", "DECIMAL(5,2)", "NO", "CHECK (>= 0)", "5.00", "Tasa de drenaje fiscal en transacciones (RN006)."],
            ["limite_bienes_por_jugador", "INT", "NO", "CHECK (> 0)", "100", "Tope máximo de inventario por operador (RN007)."],
            ["tiempo_enfriamiento_min", "INT", "NO", "CHECK (>= 0)", "15", "Minutos obligatorios de descanso laboral (RN008)."],
            ["limite_tradeos_diarios", "INT", "NO", "CHECK (> 0)", "5", "Cupo máximo de tradeos diarios por usuario (RN011)."],
        ],
        col_w_ddl
    ))

    # 2. jugadores
    story.append(make_ddl_table(
        "jugadores (Usuarios y Operadores del Servidor)",
        ddl_headers,
        [
            ["id_jugador", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Identificador correlativo del jugador."],
            ["id_servidor", "INT", "NO", "FK → servidores(id)", "1", "Servidor al que pertenece el jugador."],
            ["nombre_usuario", "VARCHAR(50)", "NO", "UNIQUE", "N/A", "Tag de acceso y apodo único del personaje."],
            ["correo", "VARCHAR(150)", "NO", "UNIQUE", "N/A", "Dirección de correo electrónico personal."],
            ["contrasena_hash", "VARCHAR(255)", "NO", "N/A", "N/A", "Hash criptográfico seguro de credenciales."],
            ["fecha_registro", "DATETIME", "NO", "N/A", "CURRENT_TIMESTAMP", "Marca temporal de alta en el sistema."],
            ["estado", "VARCHAR(20)", "NO", "CHECK ('ACTIVO','BANCARROTA','SUSPENDIDO')", "'ACTIVO'", "Estado operativo y judicial del operador (RN009)."],
            ["es_admin", "BOOLEAN", "NO", "N/A", "FALSE", "Bandera de privilegios administrativos."],
        ],
        col_w_ddl
    ))

    # 3. empleos
    story.append(make_ddl_table(
        "empleos (Catálogo de Oficios y Tarifas)",
        ddl_headers,
        [
            ["id_empleo", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Identificador único de la plaza laboral."],
            ["id_servidor", "INT", "NO", "FK → servidores(id)", "1", "Servidor que habilita el empleo."],
            ["nombre_empleo", "VARCHAR(100)", "NO", "N/A", "N/A", "Denominación del oficio (ej. Minero, Mecánico)."],
            ["tarifa_base", "DECIMAL(10,2)", "NO", "CHECK (> 0)", "N/A", "Remuneración base por unidad de trabajo (RN001)."],
        ],
        col_w_ddl
    ))

    # 4. jornadas_laborales
    story.append(make_ddl_table(
        "jornadas_laborales (Historial de Turnos de Trabajo)",
        ddl_headers,
        [
            ["id_jornada", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Clave subrogada única del turno ejecutado."],
            ["id_jugador", "INT", "NO", "FK → jugadores(id)", "N/A", "Operador que desempeñó la jornada laboral."],
            ["id_empleo", "INT", "NO", "FK → empleos(id)", "N/A", "Oficio desempeñado durante el turno."],
            ["horas_trabajadas", "DECIMAL(6,2)", "NO", "CHECK (> 0)", "N/A", "Unidades de tiempo laboradas en la jornada."],
            ["fecha_hora", "DATETIME", "NO", "N/A", "CURRENT_TIMESTAMP", "Cierre de turno registrado por defecto (RN008)."],
            ["monto_pagado", "DECIMAL(10,2)", "NO", "CHECK (>= 0)", "0.00", "Monto histórico liquidado inmutable (RN001, 3FN)."],
        ],
        col_w_ddl
    ))

    # 5. cuentas
    story.append(make_ddl_table(
        "cuentas (Fondos Bancarios y Tesorería Central)",
        ddl_headers,
        [
            ["id_cuenta", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Identificador único de la cuenta monetaria."],
            ["id_jugador", "INT", "SÍ", "FK → jugadores(id)", "NULL", "Titular. NULL si representa la Tesorería (RN005)."],
            ["id_servidor", "INT", "SÍ", "FK → servidores(id)", "NULL", "Servidor al que pertenece la cuenta bancaria."],
            ["tipo_cuenta", "VARCHAR(20)", "NO", "CHECK ('PERSONAL','SISTEMA')", "'PERSONAL'", "Tipo de cuenta contable (RN005)."],
            ["saldo_inicial", "DECIMAL(12,2)", "NO", "N/A", "0.00", "Monto de apertura registrado en el sistema."],
            ["saldo_disponible", "DECIMAL(12,2)", "NO", "CHECK (>= 0)", "0.00", "Balance líquido activo para transacciones (RN009)."],
        ],
        col_w_ddl
    ))

    # 6. items
    story.append(make_ddl_table(
        "items (Inventario de Activos y Bienes)",
        ddl_headers,
        [
            ["id_item", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Identificador único de activo/propiedad."],
            ["id_jugador", "INT", "NO", "FK → jugadores(id)", "N/A", "Propietario legítimo único del bien (RN002)."],
            ["nombre", "VARCHAR(100)", "NO", "N/A", "N/A", "Nombre comercial, modelo o matrícula del bien."],
            ["precio", "DECIMAL(12,2)", "NO", "CHECK (>= 0)", "N/A", "Valor de avalúo comercial tasado."],
            ["fecha", "DATETIME", "NO", "N/A", "CURRENT_TIMESTAMP", "Fecha y hora de adquisición o inyección del bien."],
            ["tiene_deuda", "BOOLEAN", "NO", "N/A", "FALSE", "Indicador de gravamen o deuda pendiente (RN004)."],
            ["antiguedad_dias", "INT", "NO", "CHECK (>= 0)", "0", "Días acumulados para cálculo dinámico de depreciación."],
            ["estado_custodia", "VARCHAR(20)", "NO", "CHECK ('PERSONAL','EMBARGADO','EN_TRADE')", "'PERSONAL'", "Estado de posesión física y bloqueo transaccional."],
        ],
        col_w_ddl
    ))

    # 7. negociaciones_tradeos
    story.append(make_ddl_table(
        "negociaciones_tradeos (Mesa Bilateral de Intercambio P2P)",
        ddl_headers,
        [
            ["id_negociacion", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Identificador correlativo de la sesión P2P."],
            ["id_jugador_1", "INT", "NO", "FK → jugadores(id)", "N/A", "Operador iniciador / proponente de la oferta."],
            ["id_jugador_2", "INT", "NO", "FK → jugadores(id)", "N/A", "Operador receptor / contraparte del intercambio."],
            ["id_item_j1", "INT", "SÍ", "FK → items(id)", "NULL", "Ítem ofrecido por el Jugador 1."],
            ["id_item_j2", "INT", "SÍ", "FK → items(id)", "NULL", "Ítem ofrecido por el Jugador 2."],
            ["monto_j1", "DECIMAL(12,2)", "NO", "CHECK (>= 0)", "0.00", "Efectivo líquido adjunto por Jugador 1."],
            ["monto_j2", "DECIMAL(12,2)", "NO", "CHECK (>= 0)", "0.00", "Efectivo líquido adjunto por Jugador 2."],
            ["confirmacion_j1", "BOOLEAN", "NO", "N/A", "FALSE", "Aceptación explícita de Jugador 1 (RN010)."],
            ["confirmacion_j2", "BOOLEAN", "NO", "N/A", "FALSE", "Aceptación explícita de Jugador 2 (RN010)."],
            ["estado", "VARCHAR(50)", "NO", "CHECK ('PENDIENTE','ACEPTADO','EN_PROCESO','ESPERANDO_CONFIRMACION_FINAL','COMPLETADO','CANCELADO','EXPIRADO')", "'PENDIENTE'", "Máquina de estados de la negociación (RN012)."],
            ["fecha_creacion", "DATETIME", "NO", "N/A", "CURRENT_TIMESTAMP", "Momento exacto de apertura de la propuesta."],
            ["fecha_expiracion", "DATETIME", "NO", "N/A", "N/A", "Límite temporal antes de anulación por inactividad."],
        ],
        col_w_ddl
    ))

    # 8. transacciones
    story.append(make_ddl_table(
        "transacciones (Cabecera del Libro Mayor Inmutable)",
        ddl_headers,
        [
            ["id_transaccion", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Número de folio inmutable de la transacción."],
            ["id_item_afectado", "INT", "SÍ", "FK → items(id)", "NULL", "Bien transferido en la operación (si aplica)."],
            ["id_negociacion", "INT", "SÍ", "FK → negociaciones_tradeos(id)", "NULL", "Mesa de tradeo que originó el movimiento."],
            ["id_jornada", "INT", "SÍ", "FK → jornadas_laborales(id)", "NULL", "Jornada laboral origen del pago de nómina."],
            ["tipo_transaccion", "VARCHAR(30)", "NO", "CHECK ('PAGO_SALARIO','TRADEO_P2P','COMPRA_COMERCIANTE','AJUSTE_ADMIN')", "N/A", "Clasificación de la operación económica."],
            ["estado_transaccion", "VARCHAR(20)", "NO", "CHECK ('COMPLETADA','CANCELADA','REVERTIDA')", "'COMPLETADA'", "Resultado de auditoría del movimiento (RN003)."],
            ["monto", "DECIMAL(12,2)", "NO", "CHECK (>= 0)", "N/A", "Monto nominal bruto movilizado."],
            ["fecha_hora", "DATETIME", "NO", "N/A", "CURRENT_TIMESTAMP", "Marca temporal inmutable de ejecución (RN003)."],
        ],
        col_w_ddl
    ))

    # 9. detalles_transacciones
    story.append(make_ddl_table(
        "detalles_transacciones (Asientos Contables de Partida Doble)",
        ddl_headers,
        [
            ["id_detalle", "INT", "NO", "PK, AUTO_INCREMENT", "N/A", "Identificador único del asiento contable."],
            ["id_transaccion", "INT", "NO", "FK → transacciones(id)", "N/A", "Transacción cabecera vinculada."],
            ["cuenta_origen", "INT", "NO", "FK → cuentas(id)", "N/A", "Cuenta bancaria debitada en el movimiento."],
            ["cuenta_destino", "INT", "NO", "FK → cuentas(id)", "N/A", "Cuenta bancaria acreditada en el movimiento."],
            ["tipo_movimiento", "VARCHAR(10)", "NO", "CHECK ('DEBITO','CREDITO')", "N/A", "Sentido contable del asiento por partida doble."],
            ["monto_detalle", "DECIMAL(12,2)", "NO", "CHECK (> 0)", "N/A", "Cuantía monetaria exacta del asiento."],
            ["concepto", "VARCHAR(80)", "SÍ", "N/A", "NULL", "Glosa explicativa (ej. 'COMISION_DRENAJE_SISTEMA')."],
        ],
        col_w_ddl
    ))

    story.append(Spacer(1, 6))

    # =========================================================================
    # 6. SECCIÓN 5: INFORME DE MEJORAS Y PROCESO DE NORMALIZACIÓN
    # =========================================================================
    story.append(Paragraph("5. Informe de Mejoras y Proceso de Normalización", styles['SecTitle']))
    story.append(HRFlowable(width="100%", thickness=0.8, color=NAVY, spaceBefore=0, spaceAfter=5))

    story.append(Paragraph("5.1 Mejoras Implementadas en la Capa de Datos", styles['SubSecTitle']))
    story.append(Paragraph("• <b>Garantía de Cuenta Única de Sistema por Servidor:</b> Se habilitó la cuenta <code>tipo_cuenta = 'SISTEMA'</code> con <code>id_jugador = NULL</code>, permitiendo la inyección lícita de capital salarial y centralizando la recaudación fiscal de drenaje.", styles['BulletText']))
    story.append(Paragraph("• <b>Atomicidad Transaccional:</b> Las operaciones complejas de intercambio bilateral y pago laboral se ejecutan en bloques <code>START TRANSACTION ... COMMIT / ROLLBACK</code> con manejadores de error, garantizando que ante cualquier falla los datos se restauren a su estado previo sin inconsistencias.", styles['BulletText']))
    story.append(Paragraph("• <b>Inclusión de Disparadores e Inmutabilidad:</b> Protección de las tablas de auditoría contra sentencias <code>UPDATE</code> y <code>DELETE</code>, forzando un libro mayor contable inalterable.", styles['BulletText']))
    story.append(Paragraph("• <b>Gestión de Ciclo de Vida y Expiración:</b> Control automático de temporizadores para marcar negociaciones como 'EXPIRADO' cuando superan su ventana de validez.", styles['BulletText']))

    story.append(Spacer(1, 3))
    story.append(Paragraph("5.2 Sustentación Formal de Formas Normales (1FN a 4FN / DKNF)", styles['SubSecTitle']))

    norm_data = [
        [Paragraph("<b>FORMA NORMAL</b>", styles['TableHeader']), Paragraph("<b>CRITERIO TEÓRICO APLICADO</b>", styles['TableHeader']), Paragraph("<b>RESOLUCIÓN Y GARANTÍA EN ECONOMY RP</b>", styles['TableHeader'])],
        [
            Paragraph("<b>1FN (Atomicidad)</b>", styles['TableCellBold']),
            Paragraph("Cada celda contiene un único valor escalar indivisible; sin atributos multivaluados ni repetidos.", styles['TableCell']),
            Paragraph("Se descompuso la lista de participantes en <code>detalles_transacciones</code> (una cuenta origen y una destino por fila) y los bienes en <code>items</code> y <code>negociaciones_tradeos</code>.", styles['TableCell'])
        ],
        [
            Paragraph("<b>2FN (Dependencia Total)</b>", styles['TableCellBold']),
            Paragraph("Cumple 1FN y ningún atributo no-clave depende parcialmente de claves compuestas.", styles['TableCell']),
            Paragraph("Todas las tablas del sistema utilizan claves primarias simples subrogadas (<code>id_jornada</code>, <code>id_cuenta</code>, etc.), anulando matemáticamente dependencias parciales.", styles['TableCell'])
        ],
        [
            Paragraph("<b>3FN (Sin Transitividad)</b>", styles['TableCellBold']),
            Paragraph("Cumple 2FN y ningún atributo no-clave depende transitivamente de otro atributo no-clave.", styles['TableCell']),
            Paragraph("En <code>jornadas_laborales</code> se sustituyó el cálculo dinámico de ganancia por <code>monto_pagado</code> inmutable, evitando depender de cambios futuros en la tarifa base de <code>empleos</code>.", styles['TableCell'])
        ],
        [
            Paragraph("<b>FNBC / BCNF</b>", styles['TableCellBold']),
            Paragraph("Todo determinante funcional en el esquema constituye formalmente una superclave.", styles['TableCell']),
            Paragraph("Se eliminaron dependencias encubiertas soportando todas las relaciones estrictamente sobre claves primarias enteras o índices <code>UNIQUE</code> declarados.", styles['TableCell'])
        ],
        [
            Paragraph("<b>4FN (Multivaluadas)</b>", styles['TableCellBold']),
            Paragraph("No existen dependencias multivaluadas no triviales independientes entre sí.", styles['TableCell']),
            Paragraph("El historial laboral, las cuentas monetarias y los ítems de un jugador residen en tablas independientes vinculadas unívocamente por la FK <code>id_jugador</code>.", styles['TableCell'])
        ],
        [
            Paragraph("<b>DKNF (Dominio/Clave)</b>", styles['TableCellBold']),
            Paragraph("Toda restricción es consecuencia directa de la definición de dominios y restricciones de clave.", styles['TableCell']),
            Paragraph("Todas las reglas de negocio se imponen nativamente mediante restricciones <code>CHECK</code>, <code>NOT NULL</code>, <code>UNIQUE</code> y <code>FOREIGN KEY</code>.", styles['TableCell'])
        ],
    ]

    norm_table = Table(norm_data, colWidths=[95, 180, 229])
    norm_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
        ('BOX', (0, 0), (-1, -1), 0.8, BORDER_CLR),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(norm_table)

    story.append(Spacer(1, 6))

    # =========================================================================
    # 7. SECCIÓN 6: PRUEBAS ESTRUCTURALES Y MANEJO DE ERRORES DE MOTOR
    # =========================================================================
    story.append(Paragraph("6. Pruebas Estructurales, Hallazgos y Manejo de Errores", styles['SecTitle']))
    story.append(HRFlowable(width="100%", thickness=0.8, color=NAVY, spaceBefore=0, spaceAfter=5))
    story.append(Paragraph("Para certificar la robustez del esquema DDL en MySQL 8.0 (InnoDB), se ejecutó una suite exhaustiva de pruebas de estrés estructural e inserción controlada, documentando los códigos de error reales del motor y su correspondiente resolución técnica:", styles['BodyDark']))

    story.append(Paragraph("6.1 Bitácora de Errores Encontrados y Mitigados en SGBD", styles['SubSecTitle']))

    def make_error_box(err_num, err_code, title, sql_text, fail_desc, cause_desc, fix_desc, sql_fixed):
        content = [
            Paragraph(f"<b>CASO DE ERROR {err_num}: {title} (MySQL Error Code: {err_code})</b>", styles['TableCellBold']),
            Spacer(1, 1),
            Paragraph(f"<b>Sentencia SQL Probada:</b><br/><code>{sql_text}</code>", styles['TableCell']),
            Paragraph(f"<b>Mensaje del Motor SGBD:</b> <font color='#C53030'><b>{fail_desc}</b></font>", styles['TableCell']),
            Paragraph(f"<b>Causa Técnica:</b> {cause_desc}", styles['TableCell']),
            Paragraph(f"<b>Resolución y Mitigación DDL:</b> {fix_desc}", styles['TableCell']),
            Paragraph(f"<b>Código Corregido / Verificación:</b><br/><code>{sql_fixed}</code>", styles['TableCell'])
        ]
        t = Table([[content]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.8, BORDER_CLR),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        return KeepTogether([t, Spacer(1, 3.5)])

    story.append(make_error_box(
        1, "1064", "Error de Sintaxis por Palabra Residual",
        "INSERT INTO servidores (nombre, porcentaje_comision, limite_bienes_por_jugador, tiempo_enfriamiento_min) VALUES ('Servidor Prueba', 5.00, 10, 1); servidores",
        "Error Code: 1064. You have an error in your SQL syntax; check the manual near 'servidores' at line 1.",
        "Se incluyó accidentalmente la palabra residual 'servidores' al final de la sentencia.",
        "Se depuró la instrucción eliminando el token sobrante.",
        "INSERT INTO servidores (nombre, porcentaje_comision, limite_bienes_por_jugador, tiempo_enfriamiento_min) VALUES ('Servidor Prueba', 5.00, 10, 1);"
    ))

    story.append(make_error_box(
        2, "1062", "Intento de Duplicación en Cuenta Única de Sistema",
        "INSERT INTO cuentas (id_servidor, tipo_cuenta, saldo_inicial, saldo_disponible) VALUES (1, 'SISTEMA', 1000000.00, 1000000.00);",
        "Error Code: 1062. Duplicate entry '1' for key 'cuentas.uq_cuenta_sistema_por_servidor'",
        "El servidor 1 ya contaba con una cuenta de Sistema activa. El índice UNIQUE impidió la creación de una segunda cuenta duplicada.",
        "CORRECTO: El error valida la regla de gobernanza que prohíbe múltiples tesorerías para un mismo servidor.",
        "SELECT * FROM cuentas WHERE id_servidor = 1 AND tipo_cuenta = 'SISTEMA';"
    ))

    story.append(make_error_box(
        3, "1054", "Inserción sobre Columna Inexistente (Columna Desconocida)",
        "INSERT INTO jugadores (id_servidor, nombre_usuario, nivel) VALUES (1, 'Usuario_Prueba', 1);",
        "Error Code: 1054. Unknown column 'nivel' in 'field list'",
        "Se intentó insertar en el campo 'nivel' el cual no existe en la definición DDL normalizada de jugadores.",
        "Se sincronizó la consulta de inserción con las columnas oficiales del esquema DDL.",
        "INSERT INTO jugadores (id_servidor, nombre_usuario, correo, contrasena_hash) VALUES (1, 'Usuario_Prueba', 'user@rp.com', 'hash123');"
    ))

    story.append(make_error_box(
        4, "1452", "Violación de Integridad Referencial en Jugador (Servidor Inexistente)",
        "INSERT INTO jugadores (id_servidor, nombre_usuario, correo, contrasena_hash) VALUES (9999, 'Jugador_Alpha', 'alpha@email.com', 'hash_secret_123');",
        "Error Code: 1452. Cannot add or update a child row: a foreign key constraint fails (`economy_rp`.`jugadores`, CONSTRAINT `fk_jugador_servidor` FOREIGN KEY (`id_servidor`) REFERENCES `servidores` (`id_servidor`))",
        "El motor InnoDB interceptó la FK id_servidor = 9999 que no existe en la tabla padre servidores.",
        "CORRECTO: El SGBD bloquea la creación de jugadores huérfanos sin servidor asignado.",
        "INSERT INTO jugadores (id_servidor, nombre_usuario, correo, contrasena_hash) VALUES (@id_servidor_real, 'Jugador_Alpha', 'alpha@email.com', 'hash_secret_123');"
    ))

    story.append(make_error_box(
        5, "1452", "Violación de Integridad Referencial en Cuentas (Jugador Inexistente)",
        "INSERT INTO cuentas (id_jugador, id_servidor, tipo_cuenta, saldo_inicial, saldo_disponible) VALUES (9999, 1, 'PERSONAL', 5000.00, 5000.00);",
        "Error Code: 1452. Cannot add or update a child row: a foreign key constraint fails (`economy_rp`.`cuentas`, CONSTRAINT `fk_cuenta_jugador` FOREIGN KEY (`id_jugador`) REFERENCES `jugadores` (`id_jugador`))",
        "No existe ningún operador registrado con id_jugador = 9999.",
        "CORRECTO: Protege la apertura de billeteras sin titular verificado.",
        "INSERT INTO cuentas (id_jugador, id_servidor, tipo_cuenta, saldo_inicial, saldo_disponible) VALUES (@id_jugador_real, 1, 'PERSONAL', 5000.00, 5000.00);"
    ))

    story.append(make_error_box(
        6, "1452", "Violación de Integridad Referencial en Empleos (Servidor Inexistente)",
        "INSERT INTO empleos (id_servidor, nombre_empleo, tarifa_base) VALUES (9999, 'Minero', 150.00);",
        "Error Code: 1452. Cannot add or update a child row: a foreign key constraint fails (`economy_rp`.`empleos`, CONSTRAINT `fk_empleo_servidor` FOREIGN KEY (`id_servidor`) REFERENCES `servidores` (`id_servidor`))",
        "Se intentó habilitar un empleo sobre un servidor inexistente.",
        "CORRECTO: Asegura que todo catálogo laboral esté vinculado a una instancia de juego activa.",
        "INSERT INTO empleos (id_servidor, nombre_empleo, tarifa_base) VALUES (@id_servidor_real, 'Minero', 150.00);"
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("6.2 Suite de Pruebas de Validación de Integridad y Lógica Transaccional", styles['SubSecTitle']))
    story.append(Paragraph("A continuación se documentan las pruebas avanzadas de validación de reglas de negocio y manejo de excepciones mediante bloques transaccionales y disparadores:", styles['BodyDark']))

    def make_test_case_box(test_num, title, objective, sql_run, expected_res, actual_risk, fix_code):
        content = [
            Paragraph(f"<b>PRUEBA {test_num}: {title}</b>", styles['TableCellBold']),
            Spacer(1, 1),
            Paragraph(f"<b>Objetivo de la Prueba:</b> {objective}", styles['TableCell']),
            Paragraph(f"<b>Sentencia SQL Ejecutada:</b><br/><code>{sql_run}</code>", styles['TableCell']),
            Paragraph(f"<b>Resultado Esperado:</b> {expected_res}", styles['TableCell']),
            Paragraph(f"<b>Diagnóstico de Riesgo Mitigado:</b> {actual_risk}", styles['TableCell']),
            Paragraph(f"<b>Restricción / Código DDL de Blindaje:</b><br/><code>{fix_code}</code>", styles['TableCell'])
        ]
        t = Table([[content]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.8, BORDER_CLR),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        return KeepTogether([t, Spacer(1, 3.5)])

    story.append(make_test_case_box(
        "8", "Horas Laborales Inválidas (Negativas o Cero)",
        "Validar que el motor rechace jornadas laborales con horas menores o iguales a cero (RN001).",
        "INSERT INTO jornadas_laborales (id_jugador, id_empleo, horas_trabajadas) VALUES (1, 1, -10.0);",
        "Error de validación y aborto inmediato de la inserción sin alterar saldos.",
        "Si no se controla, un valor negativo generaría montos pagados negativos, drenando saldo indebido al jugador.",
        "CONSTRAINT chk_horas_positivas CHECK (horas_trabajadas > 0) -- y validación en Trigger con SIGNAL SQLSTATE '45000' 'Las horas trabajadas deben ser mayores a cero';"
    ))

    story.append(make_test_case_box(
        "9", "Intento de Robo / Oferta de Ítem Ajeno en Tradeo",
        "Verificar que un operador solo pueda incluir en una propuesta de intercambio activos que le pertenezcan legítimamente (RN002).",
        "CALL sp_abrir_negociacion(@jugador_A, @jugador_B, @item_de_C, NULL, 0, 0, 10);",
        "El procedimiento intercepta la no coincidencia de titularidad y aborta con error 45000.",
        "Garantiza que ningún bien pueda ser negociado por un tercero no autorizado.",
        "IF NOT EXISTS (SELECT 1 FROM items WHERE id_item = p_id_item_j1 AND id_jugador = p_id_jugador_1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El item ofrecido no le pertenece al proponente'; END IF;"
    ))

    story.append(make_test_case_box(
        "10", "Confirmación de Negociación Fuera de Tiempo (Expirada)",
        "Comprobar que una sesión de tradeo vencida no pueda ser confirmada ni ejecute movimientos de fondos (RN010, RN012).",
        "CALL sp_confirmar_tradeo(@id_negociacion_expirada, @jugador_A);",
        "Error 'La negociación ya expiró' y transición del estado a 'EXPIRADO'.",
        "Evita que se ejecuten tratos obsoletos cuyos términos ya no son válidos para ambas partes.",
        "IF v_fecha_exp < NOW() THEN UPDATE negociaciones_tradeos SET estado = 'EXPIRADO' WHERE id_negociacion = p_id; SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La negociacion ya expiro'; END IF;"
    ))

    story.append(make_test_case_box(
        "11", "Exceso de Límite de Inventario por Tradeo",
        "Verificar que el límite de propiedades por servidor se respete al recibir bienes vía tradeo P2P (RN007).",
        "CALL sp_confirmar_tradeo(@negociacion, @jugador_receptor_lleno);",
        "El procedimiento calcula el balance neto de ítems; si supera el límite del servidor, cancela la negociación y arroja error 45000.",
        "Evita el acaparamiento de activos en una sola cuenta mediante transferencias entre jugadores.",
        "IF (v_cant_actual - 1 + 1) > v_limite_servidor THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El tradeo excede el limite de bienes permitido'; END IF;"
    ))

    story.append(make_test_case_box(
        "12", "Intento de Tradeo Consigo Mismo",
        "Comprobar que un operador no pueda abrir una sala de intercambio con su propia cuenta (RN012).",
        "INSERT INTO negociaciones_tradeos (id_jugador_1, id_jugador_2, ...) VALUES (1, 1, ...);",
        "Violación de restricción CHECK y bloqueo inmediato en el motor relacional.",
        "Evita el auto-bloqueo de sesiones y el colapso de la máquina de estados de doble confirmación.",
        "CONSTRAINT chk_negociacion_distintos CHECK (id_jugador_1 <> id_jugador_2)"
    ))

    story.append(Spacer(1, 6))

    # =========================================================================
    # 8. SECCIÓN 7: DEFENSA TÉCNICA Y SUSTENTACIÓN DEL ESQUEMA
    # =========================================================================
    story.append(Paragraph("7. Defensa Técnica y Sustentación del Esquema", styles['SecTitle']))
    story.append(HRFlowable(width="100%", thickness=0.8, color=NAVY, spaceBefore=0, spaceAfter=5))
    story.append(Paragraph(
        "La arquitectura del esquema DDL de Economy RP en MySQL 8.0 (InnoDB) no es un repositorio pasivo, sino un motor transaccional gobernado por reglas estrictas de integridad relacional. A nivel de defensa técnica, se sustenta el comportamiento del sistema respondiendo a las preguntas fundamentales de flujo de información:",
        styles['BodyDark']
    ))

    story.append(Paragraph("<b>1. ¿Por qué el modelo restringe el traspaso de bienes en ciertas condiciones?</b>", styles['SubSecTitle']))
    story.append(Paragraph(
        "El modelo bloquea de forma intransigente la transferencia de cualquier ítem que registre gravámenes (<code>tiene_deuda = TRUE</code>, RN004) o cuyo titular no coincida con el operador autenticado (<code>items.id_jugador != emisor</code>, RN002). Asimismo, el motor rechaza la transacción si el receptor ya alcanzó su cuota máxima de inventario (RN007) o si no dispone de liquidez suficiente para cubrir el importe acordado más el 5% de comisión tributaria (RN006). Estas restricciones protegen a la comunidad de estafas, venta fraudulenta de vehículos embargados y sobregiros contables.",
        styles['BodyDark']
    ))

    story.append(Paragraph("<b>2. ¿Por qué el modelo permite la emisión de dinero sólo a través de canales específicos?</b>", styles['SubSecTitle']))
    story.append(Paragraph(
        "El esquema prohíbe la creación de dinero 'de la nada' mediante inserciones directas en cuentas personales. Todo flujo de entrada a la economía debe ser respaldado por una jornada laboral completada (<code>jornadas_laborales</code>) y registrado como un débito formal a la cuenta oficial de Tesorería del SISTEMA (RN005). Esto asegura que la masa monetaria en circulación sea 100% auditable mediante la suma simétrica de débitos y créditos en <code>detalles_transacciones</code>.",
        styles['BodyDark']
    ))

    story.append(Paragraph("<b>3. ¿Por qué se implementó Inmutabilidad Contable por Partida Doble?</b>", styles['SubSecTitle']))
    story.append(Paragraph(
        "En un entorno financiero virtual, la modificación arbitraria de saldos mediante sentencias <code>UPDATE</code> destruye la trazabilidad histórica. Al estructurar <code>transacciones</code> y <code>detalles_transacciones</code> bajo un patrón de sólo adición (*append-only*), cualquier ajuste administrativo debe realizarse mediante un nuevo asiento compensatorio, protegiendo la fe pública y la confianza de los participantes.",
        styles['BodyDark']
    ))

    story.append(Paragraph("<b>4. Garantía de Propiedades ACID en el Motor Relacional:</b>", styles['SubSecTitle']))
    story.append(Paragraph("• <b>Atomicidad (A):</b> Todas las operaciones de intercambio P2P y liquidación laboral se ejecutan en transacciones explícitas con manejadores <code>EXIT HANDLER FOR SQLEXCEPTION ROLLBACK</code>, garantizando que todo se aplique en su totalidad o se revierta por completo.", styles['BulletText']))
    story.append(Paragraph("• <b>Consistencia (C):</b> El cumplimiento riguroso de 1FN a 4FN, las llaves foráneas y las restricciones <code>CHECK</code> aseguran que la base de datos nunca quede en un estado inválido.", styles['BulletText']))
    story.append(Paragraph("• <b>Aislamiento (I):</b> Las consultas de verificación emplean bloqueos pesimistas (<code>SELECT ... FOR UPDATE</code>), evitando condiciones de carrera en operaciones concurrentes.", styles['BulletText']))
    story.append(Paragraph("• <b>Durabilidad (D):</b> Los registros persistidos en MySQL con el motor transaccional InnoDB garantizan la recuperación total ante fallos de hardware o caídas de red.", styles['BulletText']))

    story.append(Spacer(1, 5))

    # =========================================================================
    # 9. SECCIÓN 8: ANEXO DE MODIFICACIONES Y RESPUESTA A RETROALIMENTACIÓN
    # =========================================================================
    story.append(Paragraph("8. Anexo: Modificaciones y Resoluciones tras Retroalimentación Sincrónica", styles['SecTitle']))
    story.append(HRFlowable(width="100%", thickness=0.8, color=NAVY, spaceBefore=0, spaceAfter=5))
    story.append(Paragraph("A continuación se sintetizan formalmente las mejoras aplicadas a partir de las observaciones del docente asesor en la sesión sincrónica:", styles['BodyDark']))

    anexo_data = [
        [Paragraph("<b>OBSERVACIÓN DOCENTE</b>", styles['TableHeader']), Paragraph("<b>RIESGO RELACIONAL DIAGNOSTICADO</b>", styles['TableHeader']), Paragraph("<b>SOLUCIÓN DDL IMPLEMENTADA</b>", styles['TableHeader'])],
        [
            Paragraph("<b>Punto 1: Estructura de Ítems y Posesión Rígida</b>", styles['TableCellBold']),
            Paragraph("FK <code>id_jugador</code> rígida (1:N) impedía que los bienes pertenecieran a concesionarios o quedaran bloqueados en tradeo sin perder al dueño legítimo.", styles['TableCell']),
            Paragraph("Se modularizó con <code>id_jugador INT NULL</code> y se incorporaron <code>estado_custodia CHECK ('PERSONAL','EMBARGADO','EN_TRADE')</code> y <code>tipo_propietario CHECK ('JUGADOR','CONCESIONARIO','SISTEMA')</code>.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Punto 2: Cardinalidad de Cuentas Financieras</b>", styles['TableCellBold']),
            Paragraph("Restricción <code>UNIQUE</code> en <code>id_jugador</code> forzaba relación 1:1, impidiendo cuentas múltiples (ahorro, comercial, corporativa).", styles['TableCell']),
            Paragraph("Se eliminó la restricción <code>UNIQUE</code> en <code>cuentas.id_jugador</code>, habilitando formalmente cardinalidad 1:N clasificada mediante <code>tipo_cuenta CHECK (...)</code>.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Punto 3: Atomicidad y Simetría Contable</b>", styles['TableCellBold']),
            Paragraph("Riesgo de descuadre contable si la simetría débito/crédito dependía únicamente de inserciones externas.", styles['TableCell']),
            Paragraph("Se blindó mediante bloques transaccionales atómicos ACID con bloqueos pesimistas en InnoDB, asegurando <code>SUM(Débitos) = SUM(Créditos)</code> con ROLLBACK automático ante cualquier falla.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Punto 4: Estandarización de Nomenclatura</b>", styles['TableCellBold']),
            Paragraph("Uso de prefijo <code>T_</code> y singularidades inconsistentes.", styles['TableCell']),
            Paragraph("Se normalizó el DDL completo eliminando el prefijo <code>T_</code> y estandarizando nombres de tablas en plural (<code>servidores</code>, <code>jugadores</code>, etc.) en <i>snake_case</i> minúscula.", styles['TableCell'])
        ],
    ]

    anexo_table = Table(anexo_data, colWidths=[120, 180, 204])
    anexo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
        ('BOX', (0, 0), (-1, -1), 0.8, BORDER_CLR),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(KeepTogether([anexo_table]))

    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.8, color=BORDER_CLR, spaceBefore=0, spaceAfter=10))

    # Firmas
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Miguel Ángel Cardona Agudelo</b><br/>Desarrollo DB & DDL", styles['TableCellCenter']),
            Paragraph("____________________________<br/><b>Luisa María López Orrego</b><br/>Normalización & Calidad", styles['TableCellCenter']),
            Paragraph("____________________________<br/><b>Jorge Luis Ordoñez Ávila</b><br/>Pruebas & Auditoría", styles['TableCellCenter']),
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
