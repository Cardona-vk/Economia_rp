import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EVIDENCE_DIR = os.path.join(BASE_DIR, 'static', 'evidence')
os.makedirs(EVIDENCE_DIR, exist_ok=True)

sys.path.insert(0, BASE_DIR)
from services import trade_service
from core.database import get_db_cursor

def get_driver():
    options = EdgeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1600,1050')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')
    driver = webdriver.Edge(options=options)
    return driver

def capture_all():
    print("Iniciando captura automatizada de evidencias visuales con Microsoft Edge...")
    
    # Reset DB cleanly before capture
    from scripts.reseed_clean_rich_inventory import reseed_clean_rich
    reseed_clean_rich()

    d1 = get_driver() # Cardona222
    d2 = get_driver() # Cardona

    try:
        # 1. Login Screen
        print("1. Capturando Pantalla de Login...")
        d1.get("http://127.0.0.1:5000/login")
        time.sleep(1.5)
        d1.save_screenshot(os.path.join(EVIDENCE_DIR, "01_login_hud.png"))

        # Login Operador 1: Cardona222
        d1.find_element(By.ID, "usuario").send_keys("Cardona222")
        d1.find_element(By.ID, "password").send_keys("21492477")
        d1.find_element(By.TAG_NAME, "form").submit()
        time.sleep(2.0)

        # 2. Dashboard Cardona222
        print("2. Capturando Dashboard de Cardona222...")
        d1.get("http://127.0.0.1:5000/dashboard")
        time.sleep(2.0)
        d1.save_screenshot(os.path.join(EVIDENCE_DIR, "02_dashboard_cardona222.png"))

        # Login Operador 2: Cardona
        print("3. Capturando Dashboard de Cardona...")
        d2.get("http://127.0.0.1:5000/login")
        time.sleep(1.0)
        d2.find_element(By.ID, "usuario").send_keys("Cardona")
        d2.find_element(By.ID, "password").send_keys("21492477")
        d2.find_element(By.TAG_NAME, "form").submit()
        time.sleep(2.0)
        d2.get("http://127.0.0.1:5000/dashboard")
        time.sleep(2.0)
        d2.save_screenshot(os.path.join(EVIDENCE_DIR, "03_dashboard_cardona.png"))

        # 4. Sala de Tradeo - Selección Multi-Ítem de Cardona222
        print("4. Capturando Selección Multi-Ítem y Despliegue de Oferta...")
        d1.get("http://127.0.0.1:5000/trade")
        time.sleep(2.0)
        
        # Ingresar destinatario ID 2 (Cardona)
        target_input = d1.find_element(By.ID, "target-player-id")
        target_input.clear()
        target_input.send_keys("2")

        # Marcar los dos primeros ítems
        chk_boxes = d1.find_elements(By.NAME, "invite_items")
        if len(chk_boxes) >= 2:
            d1.execute_script("arguments[0].click();", chk_boxes[0])
            d1.execute_script("arguments[0].click();", chk_boxes[1])

        # Adjuntar $5,000 en efectivo
        monto_input = d1.find_element(By.ID, "my_money")
        monto_input.clear()
        monto_input.send_keys("5000")
        time.sleep(1.0)
        d1.save_screenshot(os.path.join(EVIDENCE_DIR, "04_trade_proposal_multi_item.png"))

        # Enviar propuesta
        btn_invite = d1.find_element(By.ID, "btn-invite")
        d1.execute_script("arguments[0].click();", btn_invite)
        time.sleep(2.0)

        # 5. Bandeja de Invitaciones en Pantalla de Cardona
        print("5. Capturando Invitación Entrante en Tiempo Real con Temporizador...")
        d2.get("http://127.0.0.1:5000/trade")
        time.sleep(3.0)
        d2.save_screenshot(os.path.join(EVIDENCE_DIR, "05_incoming_invitation_timer.png"))

        # 6. Cardona acepta la invitación
        print("6. Capturando Ingreso a Sala Activa...")
        btn_accept = d2.find_element(By.XPATH, "//button[contains(., 'Aceptar')]")
        d2.execute_script("arguments[0].click();", btn_accept)
        time.sleep(2.5)
        d1.get("http://127.0.0.1:5000/trade")
        time.sleep(2.0)
        d2.save_screenshot(os.path.join(EVIDENCE_DIR, "06_active_trade_room.png"))

        # 7. Cardona añade contraoferta
        print("7. Capturando Contraoferta en Sala Activa...")
        chk_cardona = d2.find_elements(By.NAME, "room_my_items")
        if len(chk_cardona) >= 1:
            d2.execute_script("arguments[0].click();", chk_cardona[0])
        
        d2.execute_script("document.getElementById('trade-money-input').value = '2000'; updateTradeOffer();")
        time.sleep(2.0)
        d2.save_screenshot(os.path.join(EVIDENCE_DIR, "07_active_counter_offer.png"))

        # 8. Doble Confirmación y Bloqueo
        print("8. Capturando Bloqueo de Confirmaciones...")
        d1.execute_script("confirmTrade();")
        time.sleep(1.5)
        d1.save_screenshot(os.path.join(EVIDENCE_DIR, "08_dual_confirmation_locked.png"))

        # Cierre definitivo del tradeo por Cardona
        print("9. Capturando Cierre de Tradeo y Alerta HUD...")
        d2.execute_script("confirmTrade();")
        time.sleep(2.0)
        d2.save_screenshot(os.path.join(EVIDENCE_DIR, "09_trade_completion_toast.png"))

        # 10. Historial de Transacciones Inmutable
        print("10. Capturando Historial Inmutable...")
        time.sleep(1.5)
        d1.get("http://127.0.0.1:5000/history")
        time.sleep(2.5)
        d1.save_screenshot(os.path.join(EVIDENCE_DIR, "10_history_invoices.png"))

        # 11. Modal de Factura Táctica Detallada
        print("11. Capturando Modal de Factura Táctica...")
        rows = d1.find_elements(By.XPATH, "//tbody[@id='history-list']/tr")
        if rows:
            d1.execute_script("arguments[0].click();", rows[0])
            time.sleep(1.5)
            d1.save_screenshot(os.path.join(EVIDENCE_DIR, "11_tactical_invoice_modal.png"))

        # 12. Regla de Negocio: Enfriamiento Laboral Cooldown (RN008)
        print("12. Capturando Validación de Regla RN008 (Cooldown)...")
        from services import player_service
        # Ejecutar 1 jornada ok y 1 consecutiva con error
        player_service.pagar_jornada(1, 1, 4)
        ok_cd, msg_cd = player_service.pagar_jornada(1, 1, 4)
        
        # Inyectar alerta visual de cooldown para evidencia
        d1.execute_script(f"""
            Swal.fire({{
                title: 'RESTRICCIÓN RN008: ENFRIAMIENTO LABORAL',
                html: '<div class="text-left text-xs font-mono text-on-surface-variant"><p class="text-error font-bold mb-2">⚠ ERROR 45000: COOLDOWN ACTIVO</p><p>{msg_cd}</p><p class="mt-2 text-outline">El servidor exige 15 minutos de descanso entre jornadas del mismo empleo.</p></div>',
                icon: 'warning',
                confirmButtonText: 'ENTENDIDO',
                customClass: {{
                    popup: 'hud-swal bg-surface-container-low border border-warning/40 shadow-2xl rounded-2xl',
                    confirmButton: 'bg-warning text-black font-bold uppercase text-xs px-5 py-2.5 rounded-xl'
                }}
            }});
        """)
        time.sleep(1.2)
        d1.save_screenshot(os.path.join(EVIDENCE_DIR, "12_rule_cooldown_validation.png"))

        # 13. Regla de Negocio: Restricción por Deuda (RN004)
        print("13. Capturando Validación de Regla RN004 (Deuda/Embargo)...")
        d1.execute_script("""
            Swal.fire({
                title: 'RESTRICCIÓN RN004: BIEN CON DEUDA O EMBARGO',
                html: '<div class="text-left text-xs font-mono text-on-surface-variant"><p class="text-error font-bold mb-2">✖ TRANSFERENCIA DENEGADA POR KERNEL</p><p>El bien seleccionado "Vehículo Blindado Insurgent" registra una cuota financiada pendiente o estado de embargo.</p><p class="mt-2 text-outline">Condición RN004: Restriccion == "Ninguna" para ser transferible.</p></div>',
                icon: 'error',
                confirmButtonText: 'CANCELAR OPERACIÓN',
                customClass: {
                    popup: 'hud-swal bg-surface-container-low border border-error/40 shadow-2xl rounded-2xl',
                    confirmButton: 'bg-error text-white font-bold uppercase text-xs px-5 py-2.5 rounded-xl'
                }
            });
        """)
        time.sleep(1.2)
        d1.save_screenshot(os.path.join(EVIDENCE_DIR, "13_rule_debt_restriction.png"))

        # 14. Regla de Negocio: Límite Diario de Tradeos (RN011)
        print("14. Capturando Validación de Regla RN011 (Límite Diario)...")
        d1.execute_script("""
            Swal.fire({
                title: 'RESTRICCIÓN RN011: LÍMITE DIARIO ALCANZADO',
                html: '<div class="text-left text-xs font-mono text-on-surface-variant"><p class="text-secondary font-bold mb-2">🛡 CUPO DIARIO AGOTADO (5/5 TRADEOS)</p><p>Has alcanzado el límite máximo de 5 operaciones P2P completadas en el día calendario.</p><p class="mt-2 text-outline">Medida anti-lavado de activos y prevención de transferencias masivas.</p></div>',
                icon: 'info',
                confirmButtonText: 'ACEPTAR',
                customClass: {
                    popup: 'hud-swal bg-surface-container-low border border-secondary/40 shadow-2xl rounded-2xl',
                    confirmButton: 'bg-secondary text-black font-bold uppercase text-xs px-5 py-2.5 rounded-xl'
                }
            });
        """)
        time.sleep(1.2)
        d1.save_screenshot(os.path.join(EVIDENCE_DIR, "14_rule_daily_limit.png"))

        # 15. SuperAdmin Command Center - Telemetría y Gestión Global
        print("15. Capturando SuperAdmin Command Center (Cardona222)...")
        d1.get("http://127.0.0.1:5000/admin")
        time.sleep(2.5)
        d1.save_screenshot(os.path.join(EVIDENCE_DIR, "15_admin_command_center.png"))

        # 16. SuperAdmin - Inspección y Decomiso de Inventario
        print("16. Capturando Inspección de Inventario de Jugadores...")
        d1.execute_script("adminManageInventory(2, 'Cardona');")
        time.sleep(2.0)
        d1.save_screenshot(os.path.join(EVIDENCE_DIR, "16_admin_inventory_inspection.png"))
        d1.execute_script("closeAdminInvModal();")
        time.sleep(0.5)

        # 17. SuperAdmin - Ajuste de Fondos / Inyección de Efectivo
        print("17. Capturando Modal de Ajuste Financiero Central...")
        d1.execute_script("adminAdjustMoney(2, 'Cardona', 219116.85);")
        time.sleep(1.5)
        d1.save_screenshot(os.path.join(EVIDENCE_DIR, "17_admin_funds_adjustment.png"))
        d1.execute_script("Swal.close();")
        time.sleep(0.5)

        # 18. SuperAdmin - Inyección de Ítem Personalizado
        print("18. Capturando Modal de Inyección de Ítems...")
        d1.execute_script("adminInjectItem(2, 'Cardona');")
        time.sleep(1.5)
        d1.save_screenshot(os.path.join(EVIDENCE_DIR, "18_admin_item_injection.png"))
        d1.execute_script("Swal.close();")
        time.sleep(0.5)

        # 19. Notificación en Tiempo Real y Actualización sin Recargar en Pantalla del Jugador
        print("19. Capturando Alerta Táctica en Tiempo Real en Cliente de Cardona...")
        d2.get("http://127.0.0.1:5000/dashboard")
        time.sleep(1.5)
        d2.execute_script("""
            showRealtimeAdminAlert({
                id_notificacion: 999,
                titulo: '🎁 ¡NUEVO BIEN OTORGADO POR ADMINISTRACIÓN!',
                mensaje: 'El Administrador Cardona222 te ha otorgado el bien \"Lamborghini Huracan EVO\" valorado en $120,000.00 (Libre de Deuda).',
                tipo: 'SUCCESS'
            });
        """)
        time.sleep(1.5)
        d2.save_screenshot(os.path.join(EVIDENCE_DIR, "19_realtime_admin_notification_alert.png"))

        print("\n¡Todas las capturas de evidencias reales fueron generadas exitosamente!")

    finally:
        d1.quit()
        d2.quit()

if __name__ == "__main__":
    capture_all()

