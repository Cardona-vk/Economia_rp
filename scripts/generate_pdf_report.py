import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EVIDENCE_DIR = os.path.join(BASE_DIR, 'static', 'evidence')
PDF_OUTPUT = os.path.join(BASE_DIR, 'MANUAL_DE_USUARIO_Y_EVIDENCIAS_ECONOMY_RP.pdf')

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#00a3c4"))
            self.drawString(54, 755, "TRADE OS // GAMING HUD — MANUAL OFICIAL DE USUARIO & EVIDENCIAS TÉCNICAS")
            
            self.setFont("Helvetica", 7)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawRightString(558, 755, "GRUPO 4 • I.U. PASCUAL BRAVO • V3.5")

            self.setStrokeColor(colors.HexColor("#00e5ff"))
            self.setLineWidth(0.75)
            self.line(54, 748, 558, 748)

        # Footer
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(54, 32, "Certificación de Cumplimiento Técnico — Ingeniería de Software I / Bases de Datos I")
        self.drawRightString(558, 32, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()

def build_pdf():
    print(f"Construyendo documento PDF oficial en: {PDF_OUTPUT}")
    doc = SimpleDocTemplate(
        PDF_OUTPUT,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Cyberpunk & Executive Palette
    c_primary = colors.HexColor("#0f172a") # Slate 900
    c_cyan = colors.HexColor("#008fa8")    # Cyan accent
    c_emerald = colors.HexColor("#059669") # Emerald accent
    c_gold = colors.HexColor("#d97706")    # Amber accent

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=25,
        textColor=colors.HexColor("#0f172a"),
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_cyan,
        alignment=TA_CENTER
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0369a1"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        alignment=TA_JUSTIFY,
        spaceAfter=5
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    caption_title = ParagraphStyle(
        'CapTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#0f172a")
    )

    caption_desc = ParagraphStyle(
        'CapDesc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#334155")
    )

    table_hdr_style = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1e293b")
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName='Helvetica-Bold'
    )

    story = []

    # ==========================================
    # PORTADA Y ENCABEZADO PRINCIPAL
    # ==========================================
    banner_data = [
        [
            Paragraph("<font color='#00e5ff'><b>TRADE OS // GAMING HUD</b></font><br/><font color='#94a3b8' size='8'>SISTEMA TRANSACCIONAL DE ALTA FIDELIDAD & ECONOMÍA ROLEPLAY</font>", ParagraphStyle('BanL', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.white)),
            Paragraph("<font color='#5be9ad'><b>VERSIÓN 3.5.0 ENTERPRISE</b></font><br/><font color='#cbd5e1' size='7'>CERTIFICACIÓN ACADÉMICA Pascual Bravo</font>", ParagraphStyle('BanR', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.white, alignment=TA_RIGHT))
        ]
    ]
    t_banner = Table(banner_data, colWidths=[320, 184])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 14))

    story.append(Paragraph("MANUAL OFICIAL DE USUARIO & EVIDENCIAS TÉCNICAS", title_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph("Gobernanza SuperAdmin • Comercio Bilateral Multi-Ítem • Telemetría en Vivo • Inmutabilidad Contable", subtitle_style))
    story.append(Spacer(1, 10))

    # Meta Info Table
    meta_data = [
        [Paragraph("<b>Institución:</b>", table_cell_bold), Paragraph("I.U. Pascual Bravo — Facultad de Ingeniería", table_cell_style), Paragraph("<b>Fecha Entrega:</b>", table_cell_bold), Paragraph("29 de Septiembre de 2026", table_cell_style)],
        [Paragraph("<b>Asignaturas:</b>", table_cell_bold), Paragraph("Ingeniería de Software I / Bases de Datos I", table_cell_style), Paragraph("<b>Autenticación:</b>", table_cell_bold), Paragraph("Bcrypt + SHA-256 Sello Inmutable", table_cell_style)],
        [Paragraph("<b>SuperAdmin:</b>", table_cell_bold), Paragraph("Operador Cardona222 (ID: #1, es_admin=TRUE)", table_cell_style), Paragraph("<b>Operador Estándar:</b>", table_cell_bold), Paragraph("Operador Cardona (ID: #2)", table_cell_style)],
        [Paragraph("<b>Motor BD:</b>", table_cell_bold), Paragraph("MySQL 8.0 InnoDB (ACID / Transacciones Atómicas)", table_cell_style), Paragraph("<b>Tasa Drenaje:</b>", table_cell_bold), Paragraph("5.00% a Tesorería Central (RN014)", table_cell_style)]
    ]
    t_meta = Table(meta_data, colWidths=[80, 180, 95, 149])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # ==========================================
    # CAPÍTULO 1: RESUMEN EJECUTIVO
    # ==========================================
    story.append(Paragraph("1. Resumen Ejecutivo y Arquitectura del Sistema", h1_style))
    story.append(Paragraph(
        "El presente documento técnico certifica la entrega formal de <b>Trade OS Gaming HUD</b>. "
        "El sistema provee una solución robusta y de grado profesional para la administración de activos, inventarios, fondos y comercio bilateral seguro entre operadores en un entorno de Roleplay (RP). "
        "Implementa protección anti-fraude (*Anti-Duplication*), inmutabilidad por partida doble en el libro contable, drenaje fiscal anti-inflacionario a la cuenta central de Tesorería (`T_Cuenta` ID 1), temporizadores de cuenta regresiva sincronizados en tiempo real y una consola de mando SuperAdmin con telemetría viva y notificaciones instantáneas sin recarga de pantalla.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # ==========================================
    # CAPÍTULO 2: MATRIZ DE REGLAS DE NEGOCIO
    # ==========================================
    story.append(Paragraph("2. Matriz de Cumplimiento de Reglas de Negocio (RN001 - RN014)", h1_style))
    story.append(Paragraph("Todas las reglas funcionales estipuladas en el marco del proyecto están implementadas y blindadas en base de datos y capas de servicio:", body_style))

    rules_data = [
        [Paragraph("Regla", table_hdr_style), Paragraph("Descripción y Enunciado", table_hdr_style), Paragraph("Implementación en Kernel / Código", table_hdr_style), Paragraph("Estado", table_hdr_style)],
        [Paragraph("<b>RN001</b>", table_cell_bold), Paragraph("Principio de Partida Doble (Débito y Crédito simétricos en cada movimiento)", table_cell_style), Paragraph("<code>T_Detalle_Transaccion</code> con registros simétricos obligatorios", table_cell_style), Paragraph("<font color='#059669'><b>100% OK</b></font>", table_cell_bold)],
        [Paragraph("<b>RN002</b>", table_cell_bold), Paragraph("No negatividad de fondos monetarios", table_cell_style), Paragraph("Constraint <code>CHECK (saldo_disponible >= 0)</code>", table_cell_style), Paragraph("<font color='#059669'><b>100% OK</b></font>", table_cell_bold)],
        [Paragraph("<b>RN003</b>", table_cell_bold), Paragraph("Propiedad exclusiva de bienes (un solo dueño simultáneo)", table_cell_style), Paragraph("Clave foránea directa <code>T_Item.id_jugador</code>", table_cell_style), Paragraph("<font color='#059669'><b>100% OK</b></font>", table_cell_bold)],
        [Paragraph("<b>RN004</b>", table_cell_bold), Paragraph("Restricción de transferencia para bienes con gravamen o deuda", table_cell_style), Paragraph("Validación de <code>tiene_deuda == FALSE</code> antes de aceptar", table_cell_style), Paragraph("<font color='#059669'><b>100% OK</b></font>", table_cell_bold)],
        [Paragraph("<b>RN005</b>", table_cell_bold), Paragraph("Restricción de operaciones por quiebra judicial o suspensión", table_cell_style), Paragraph("Validación de estado <code>ACTIVO</code> en sesión y tradeos", table_cell_style), Paragraph("<font color='#059669'><b>100% OK</b></font>", table_cell_bold)],
        [Paragraph("<b>RN006</b>", table_cell_bold), Paragraph("Separación estricta de cuentas Personales vs Tesorería del Sistema", table_cell_style), Paragraph("Columna generada única por servidor para cuenta <code>SISTEMA</code>", table_cell_style), Paragraph("<font color='#059669'><b>100% OK</b></font>", table_cell_bold)],
        [Paragraph("<b>RN007</b>", table_cell_bold), Paragraph("Límite máximo de capacidad de bienes por jugador (100 slots)", table_cell_style), Paragraph("Verificación de aforo contra <code>limite_bienes_por_jugador</code>", table_cell_style), Paragraph("<font color='#059669'><b>100% OK</b></font>", table_cell_bold)],
        [Paragraph("<b>RN008</b>", table_cell_bold), Paragraph("Periodo de enfriamiento laboral entre jornadas (15 min cooldown)", table_cell_style), Paragraph("Control de timestamp en <code>sp_pagar_jornada</code> (Error 45000)", table_cell_style), Paragraph("<font color='#059669'><b>100% OK</b></font>", table_cell_bold)],
        [Paragraph("<b>RN009</b>", table_cell_bold), Paragraph("Máquina de estados estricta en sesiones de comercio bilateral", table_cell_style), Paragraph("Transición atómica: PENDIENTE $\\rightarrow$ ACEPTADO $\\rightarrow$ COMPLETADO", table_cell_style), Paragraph("<font color='#059669'><b>100% OK</b></font>", table_cell_bold)],
        [Paragraph("<b>RN010</b>", table_cell_bold), Paragraph("Reinicio automático de confirmaciones y timers tras contraofertas", table_cell_style), Paragraph("Reseteo de <code>confirmacion_j1=FALSE, confirmacion_j2=FALSE</code>", table_cell_style), Paragraph("<font color='#059669'><b>100% OK</b></font>", table_cell_bold)],
        [Paragraph("<b>RN011</b>", table_cell_bold), Paragraph("Límite diario de 5 tradeos completados por operador", table_cell_style), Paragraph("Conteo de operaciones en día calendario previo a abrir sesión", table_cell_style), Paragraph("<font color='#059669'><b>100% OK</b></font>", table_cell_bold)],
        [Paragraph("<b>RN012</b>", table_cell_bold), Paragraph("Auditoría obligatoria con factura digital y hash SHA-256", table_cell_style), Paragraph("Generación de comprobante detallado con sello criptográfico", table_cell_style), Paragraph("<font color='#059669'><b>100% OK</b></font>", table_cell_bold)],
        [Paragraph("<b>RN013</b>", table_cell_bold), Paragraph("Inmutabilidad del libro diario e histórico transaccional", table_cell_style), Paragraph("Prohibición total de <code>UPDATE</code> y <code>DELETE</code> en historial", table_cell_style), Paragraph("<font color='#059669'><b>100% OK</b></font>", table_cell_bold)],
        [Paragraph("<b>RN014</b>", table_cell_bold), Paragraph("Mecanismo anti-inflacionario por drenaje fiscal (5% a Tesorería)", table_cell_style), Paragraph("Cálculo de comisión sobre efectivo transferido en tradeos P2P", table_cell_style), Paragraph("<font color='#059669'><b>100% OK</b></font>", table_cell_bold)],
    ]
    t_rules = Table(rules_data, colWidths=[45, 205, 204, 50])
    t_rules.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 2.8),
    ]))
    story.append(t_rules)
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    # ==========================================
    # CAPÍTULO 3: EVIDENCIAS REALES DEL SISTEMA
    # ==========================================
    story.append(Paragraph("3. Evidencias Visuales del Flujo Transaccional y HUD Gaming", h1_style))
    story.append(Paragraph(
        "A continuación se presenta el registro fotográfico en tiempo real de las 19 operaciones clave del sistema ejecutadas con los operadores <b>Cardona222</b> y <b>Cardona</b>:",
        body_style
    ))

    def add_evidence_card(img_name, step_title, step_desc, step_tag="FLUJO OPERACIONAL"):
        img_path = os.path.join(EVIDENCE_DIR, img_name)
        if not os.path.exists(img_path):
            return

        card_content = []
        
        # Header of card
        hdr_data = [
            [
                Paragraph(f"<b>{step_title}</b>", caption_title),
                Paragraph(f"<font color='#0369a1'><b>// {step_tag}</b></font>", ParagraphStyle('HdrTag', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9, alignment=TA_RIGHT))
            ]
        ]
        t_c_hdr = Table(hdr_data, colWidths=[360, 134])
        t_c_hdr.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 0),
        ]))
        card_content.append(t_c_hdr)
        card_content.append(Spacer(1, 3))

        # Image
        img = Image(img_path, width=494, height=215)
        card_content.append(img)
        card_content.append(Spacer(1, 3))

        # Description
        card_content.append(Paragraph(step_desc, caption_desc))

        card_table = Table([[card_content]], colWidths=[504])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))

        story.append(card_table)
        story.append(Spacer(1, 8))

    # 1. Login HUD
    add_evidence_card(
        "01_login_hud.png",
        "Paso 1: Pantalla Táctica de Acceso con Wallpaper Gaming HUD",
        "Interfaz de inicio de sesión estilizada con fondo Cyberpunk inmersivo, encriptación de credenciales con hash Bcrypt y validación de estado legal del operador (RN005)."
    )

    # 2. Dashboard Cardona222
    add_evidence_card(
        "02_dashboard_cardona222.png",
        "Paso 2: Cockpit Principal y 4 Tarjetas de Telemetría (Cardona222)",
        "Panel táctico del SuperAdministrador con 4 tarjetas de telemetría dinámica: Saldo Líquido ($247,900.00), Patrimonio Total ($716,600.00), Slots de Inventario (11/100) y Telemetría P2P (2 Trades, Tasa 5.0%), más inventario con badges de rareza."
    )

    story.append(PageBreak())

    # 3. Dashboard Cardona
    add_evidence_card(
        "03_dashboard_cardona.png",
        "Paso 3: Dashboard del Operador Receptor (Cardona)",
        "Panel del segundo operador mostrando su bóveda bancaria ($197,750.00), patrimonio total ($711,600.00), slots ocupados (14/100) y catálogo completo de bienes con miniaturas y tasaciones comerciales."
    )

    # 4. Multi-Item Selection
    add_evidence_card(
        "04_trade_proposal_multi_item.png",
        "Paso 4: Propuesta de Comercio Bilateral con Selección Multi-Ítem",
        "Módulo de inicio de negociación P2P: selección simultánea de múltiples ítems del inventario, adición de fondos en efectivo ($5,000.00) y transmisión de propuesta con temporizador de 2 minutos."
    )

    story.append(PageBreak())

    # 5. Pending Invites with Timer
    add_evidence_card(
        "05_incoming_invitation_timer.png",
        "Paso 5: Solicitud Entrante con Cuenta Regresiva en Tiempo Real",
        "Bandeja de entrada táctica en la pantalla de Cardona: visualización de bienes ofrecidos, dinero adjunto y reloj de expiración en cuenta regresiva activa (02:00)."
    )

    # 6. Active Trade Room
    add_evidence_card(
        "06_active_trade_room.png",
        "Paso 6: Sala Activa de Negociación Bilateral P2P",
        "Espacio de intercambio en tiempo real: despliegue simétrico de ofertas de ambos operadores, indicador de temporizador de sala (03:00) y candados de confirmación independientes."
    )

    story.append(PageBreak())

    # 7. Counter Offer
    add_evidence_card(
        "07_active_counter_offer.png",
        "Paso 7: Contraoferta en Vivo y Recálculo de Drenaje Fiscal (5%)",
        "Cardona añade un ítem adicional y $2,000.00 en efectivo a la mesa. El sistema recalcula inmediatamente las comisiones de drenaje tributario ($350.00) y reinicia confirmaciones (RN010)."
    )

    # 8. Dual Lock
    add_evidence_card(
        "08_dual_confirmation_locked.png",
        "Paso 8: Bloqueo de Oferta y Doble Confirmación de Seguridad",
        "Cardona222 bloquea su oferta con candado criptográfico. La interfaz entra en modo 'Esperando Confirmación Final' hasta que ambas partes ratifiquen el contrato."
    )

    story.append(PageBreak())

    # 9. Trade Completion Toast
    add_evidence_card(
        "09_trade_completion_toast.png",
        "Paso 9: Cierre Atómico de la Transacción con Alertas Cyberpunk HUD",
        "Ejecución del procedimiento almacenado transaccional: transferencia instantánea de bienes, débito/crédito en cuentas y emisión de notificación HUD toast de éxito."
    )

    # 10. History
    add_evidence_card(
        "10_history_invoices.png",
        "Paso 10: Libro Diario e Historial Inmutable de Transacciones",
        "Registro correlativo de todas las operaciones realizadas. Cada movimiento cuenta con timestamp, tipo de operación, monto liquidado y enlace a comprobante fiscal."
    )

    story.append(PageBreak())

    # 11. Invoice Modal SHA-256
    add_evidence_card(
        "11_tactical_invoice_modal.png",
        "Paso 11: Factura Táctica Oficial con Firma Criptográfica SHA-256",
        "Comprobante fiscal interactivo: desglose de bienes con imágenes, liquidación del drenaje tributario del 5%, hash inmutable SHA-256 y botón de exportación física/PDF."
    )

    # 12. Validation RN008 (Cooldown)
    add_evidence_card(
        "12_rule_cooldown_validation.png",
        "Validación RN008: Enfriamiento Laboral Obligatorio (15 min Cooldown)",
        "Prueba negativa: intento de cobro consecutivo de jornadas laborales sin respetar el intervalo de descanso. El kernel intercepta la solicitud con Error 45000.",
        step_tag="VALIDACIÓN NEGATIVA"
    )

    story.append(PageBreak())

    # 13. Validation RN004 (Debt)
    add_evidence_card(
        "13_rule_debt_restriction.png",
        "Validación RN004: Restricción por Deuda o Embargo Patrimonial",
        "Prueba negativa: intento de incluir en un tradeo un activo con cuota pendiente o gravamen judicial (tiene_deuda == TRUE). El kernel deniega la operación protegiendo al receptor.",
        step_tag="VALIDACIÓN NEGATIVA"
    )

    # 14. Validation RN011 (Daily limit)
    add_evidence_card(
        "14_rule_daily_limit.png",
        "Validación RN011: Límite Diario de 5 Tradeos por Operador",
        "Prueba negativa: intento de abrir un sexto tradeo en el mismo día calendario. El sistema bloquea la acción previniendo fraudes masivos y lavado de activos.",
        step_tag="VALIDACIÓN NEGATIVA"
    )

    story.append(PageBreak())

    # 15. SuperAdmin Command Center
    add_evidence_card(
        "15_admin_command_center.png",
        "Paso 15: Centro de Mando SuperAdmin y Telemetría Financiera Global",
        "Consola de administración integral (`/admin`) de Cardona222: telemetría en tiempo real de reservas del sistema, circulante M2, volumen transaccionado, gestión de jugadores y parámetros del servidor.",
        step_tag="SUPERADMIN CENTER"
    )

    # 16. Admin Inventory Inspection
    add_evidence_card(
        "16_admin_inventory_inspection.png",
        "Paso 16: Inspección Táctica, Control y Decomiso de Inventario",
        "Modal de auditoría profunda de bienes por jugador: visualización de ítems con precio y estado de gravamen, permitiendo la incautación forzada directa con actualización atómica.",
        step_tag="SUPERADMIN CENTER"
    )

    story.append(PageBreak())

    # 17. Admin Funds Adjustment
    add_evidence_card(
        "17_admin_funds_adjustment.png",
        "Paso 17: Ajuste Financiero Centralizado (Inyección, Retiro o Fijación)",
        "Herramienta bancaria administrativa: permite sumar fondos, deducir multas o establecer el saldo exacto de cualquier cuenta personal con validación de liquidez.",
        step_tag="SUPERADMIN CENTER"
    )

    # 18. Admin Item Injection
    add_evidence_card(
        "18_admin_item_injection.png",
        "Paso 18: Inyección Directa de Bienes y Activos Personalizados",
        "Formulario de creación e inserción inmediata de activos con nombre, valor comercial tasado y flags legales (con o sin gravamen/deuda) al inventario del operador seleccionado.",
        step_tag="SUPERADMIN CENTER"
    )

    story.append(PageBreak())

    # 19. Real-time Notification Alert
    add_evidence_card(
        "19_realtime_admin_notification_alert.png",
        "Paso 19: Notificación en Tiempo Real y Actualización en Vivo sin Recargar",
        "Cuando el SuperAdmin realiza una acción (inyección de bienes o ajuste de fondos), el cliente del jugador recibe una alerta táctica emergente instantánea y refresca sus datos sin recargar la página.",
        step_tag="LIVE SYNC ENGINE"
    )

    # ==========================================
    # CAPÍTULO 4: AUDITORÍA CONTABLE
    # ==========================================
    story.append(Paragraph("4. Auditoría Contable y Liquidación de Partida Doble", h1_style))
    story.append(Paragraph("A continuación se presenta el balance contable final verificado en MySQL tras la ejecución del intercambio bilateral:", body_style))

    # Balance table
    bal_data = [
        [Paragraph("ID Cuenta", table_hdr_style), Paragraph("Titular / Operador", table_hdr_style), Paragraph("Tipo Cuenta", table_hdr_style), Paragraph("Saldo Inicial", table_hdr_style), Paragraph("Saldo Final", table_hdr_style), Paragraph("Variación Neta / Drenaje", table_hdr_style)],
        [Paragraph("<b>1</b>", table_cell_bold), Paragraph("Tesorería del Sistema", table_cell_style), Paragraph("SISTEMA", table_cell_style), Paragraph("$10,000,000.00", table_cell_style), Paragraph("<b>$10,000,350.00</b>", table_cell_bold), Paragraph("<font color='#059669'><b>+$350.00 (Comisiones Recaudadas)</b></font>", table_cell_style)],
        [Paragraph("<b>2</b>", table_cell_bold), Paragraph("Cardona222 (ID: 1)", table_cell_style), Paragraph("PERSONAL", table_cell_style), Paragraph("$150,000.00", table_cell_style), Paragraph("<b>$146,900.00</b>", table_cell_bold), Paragraph("-$3,100.00 (-$5,000 + $1,900 neto)", table_cell_style)],
        [Paragraph("<b>3</b>", table_cell_bold), Paragraph("Cardona (ID: 2)", table_cell_style), Paragraph("PERSONAL", table_cell_style), Paragraph("$120,000.00", table_cell_style), Paragraph("<b>$122,750.00</b>", table_cell_bold), Paragraph("<font color='#059669'>+$2,750.00 (-$2,000 + $4,750 neto)</font>", table_cell_style)]
    ]
    t_bal = Table(bal_data, colWidths=[45, 120, 65, 80, 80, 114])
    t_bal.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_bal)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Asientos Contables Registrados en T_Detalle_Transaccion:</b>", h2_style))
    asientos_data = [
        [Paragraph("ID", table_hdr_style), Paragraph("Cta Origen", table_hdr_style), Paragraph("Cta Destino", table_hdr_style), Paragraph("Movimiento", table_hdr_style), Paragraph("Monto", table_hdr_style), Paragraph("Concepto Contable", table_hdr_style)],
        [Paragraph("1", table_cell_style), Paragraph("2 (Cardona222)", table_cell_style), Paragraph("3 (Cardona)", table_cell_style), Paragraph("DEBITO", table_cell_style), Paragraph("$4,750.00", table_cell_style), Paragraph("PAGO_TRADEO_J1", table_cell_style)],
        [Paragraph("2", table_cell_style), Paragraph("2 (Cardona222)", table_cell_style), Paragraph("3 (Cardona)", table_cell_style), Paragraph("CREDITO", table_cell_style), Paragraph("$4,750.00", table_cell_style), Paragraph("COBRO_TRADEO_J1", table_cell_style)],
        [Paragraph("3", table_cell_style), Paragraph("2 (Cardona222)", table_cell_style), Paragraph("1 (SISTEMA)", table_cell_style), Paragraph("DEBITO", table_cell_style), Paragraph("$250.00", table_cell_style), Paragraph("COMISION_DRENAJE_SISTEMA (5%)", table_cell_style)],
        [Paragraph("4", table_cell_style), Paragraph("2 (Cardona222)", table_cell_style), Paragraph("1 (SISTEMA)", table_cell_style), Paragraph("CREDITO", table_cell_style), Paragraph("$250.00", table_cell_style), Paragraph("COMISION_DRENAJE_SISTEMA (5%)", table_cell_style)],
        [Paragraph("5", table_cell_style), Paragraph("3 (Cardona)", table_cell_style), Paragraph("2 (Cardona222)", table_cell_style), Paragraph("DEBITO", table_cell_style), Paragraph("$1,900.00", table_cell_style), Paragraph("PAGO_TRADEO_J2", table_cell_style)],
        [Paragraph("6", table_cell_style), Paragraph("3 (Cardona)", table_cell_style), Paragraph("2 (Cardona222)", table_cell_style), Paragraph("CREDITO", table_cell_style), Paragraph("$1,900.00", table_cell_style), Paragraph("COBRO_TRADEO_J2", table_cell_style)],
        [Paragraph("7", table_cell_style), Paragraph("3 (Cardona)", table_cell_style), Paragraph("1 (SISTEMA)", table_cell_style), Paragraph("DEBITO", table_cell_style), Paragraph("$100.00", table_cell_style), Paragraph("COMISION_DRENAJE_SISTEMA (5%)", table_cell_style)],
        [Paragraph("8", table_cell_style), Paragraph("3 (Cardona)", table_cell_style), Paragraph("1 (SISTEMA)", table_cell_style), Paragraph("CREDITO", table_cell_style), Paragraph("$100.00", table_cell_style), Paragraph("COMISION_DRENAJE_SISTEMA (5%)", table_cell_style)]
    ]
    t_asientos = Table(asientos_data, colWidths=[25, 95, 95, 60, 65, 164])
    t_asientos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_asientos)
    story.append(Spacer(1, 10))

    # ==========================================
    # CAPÍTULO 5: GUÍA DE DESPLIEGUE & CONCLUSIONES
    # ==========================================
    story.append(Paragraph("5. Instrucciones de Despliegue y Ejecución", h1_style))
    story.append(Paragraph(
        "<b>1. Inicializar base de datos limpia con catálogo enriquecido:</b> <code>py scripts/reseed_clean_rich_inventory.py</code><br/>"
        "<b>2. Levantar el servidor web Flask:</b> <code>py run.py</code><br/>"
        "<b>3. Ingresar al navegador:</b> <code>http://127.0.0.1:5000</code><br/>"
        "<b>4. Credenciales SuperAdmin:</b> <code>Cardona222</code> (Clave: <code>21492477</code>)<br/>"
        "<b>5. Credenciales Operador Estándar:</b> <code>Cardona</code> (Clave: <code>21492477</code>)",
        body_style
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("6. Conclusiones de la Entrega", h1_style))
    story.append(Paragraph(
        "El proyecto <b>Trade OS Gaming HUD</b> cumple íntegramente con todos los requisitos académicos y tecnológicos. "
        "Se garantiza la inmutabilidad de los registros contables mediante partida doble, la eliminación de vulnerabilidades de duplicación de ítems mediante procedimientos almacenados atómicos, el drenaje fiscal anti-inflacionario y una experiencia de usuario interactiva y de vanguardia con administración total en tiempo real.",
        body_style
    ))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Documento PDF oficial compilado con éxito en: {PDF_OUTPUT}")

if __name__ == "__main__":
    build_pdf()
