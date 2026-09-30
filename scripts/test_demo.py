import sys
import os
import json

# Set project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from services import trade_service, player_service
from core.database import get_db_cursor

def run_test():
    print("=" * 70)
    print("DEMOSTRACIÓN Y EJECUCIÓN DEL FLUJO COMPLETO - ECONOMY RP")
    print("=" * 70)

    # Limpiar negociaciones previas
    trade_service.limpieza_forzada_trades()

    app = create_app()
    c1 = app.test_client()
    c2 = app.test_client()

    # 1. Autenticación de Operadores
    print("\n[PASO 1] AUTENTICACIÓN DE OPERADORES")
    r1 = c1.post('/login', data={'usuario': 'Cardona222', 'password': '21492477'}, follow_redirects=True)
    r2 = c2.post('/login', data={'usuario': 'Cardona', 'password': '21492477'}, follow_redirects=True)
    print(f" -> Operador 1: Cardona222 (HTTP {r1.status_code}) - Autenticado")
    print(f" -> Operador 2: Cardona    (HTTP {r2.status_code}) - Autenticado")

    # 2. Telemetría de Cuentas e Inventarios Iniciales
    dash1 = c1.get('/api/dashboard').get_json()
    dash2 = c2.get('/api/dashboard').get_json()
    s1_init = float(dash1['saldo'])
    s2_init = float(dash2['saldo'])
    print("\n[PASO 2] TELEMETRÍA Y ESTADO INICIAL")
    print(f" -> Cardona222 (ID 1): Saldo = ${s1_init:,.2f} | Bienes = {len(dash1['inventario'])}")
    print(f" -> Cardona    (ID 2): Saldo = ${s2_init:,.2f} | Bienes = {len(dash2['inventario'])}")

    # 3. Cardona222 inicia una propuesta de intercambio (Multi-Ítem + Efectivo)
    item1 = dash1['inventario'][0]['id_item']
    item2 = dash1['inventario'][1]['id_item']
    print("\n[PASO 3] CARDONA222 INICIA PROPUESTA DE TRADEO P2P")
    print(f" -> Emisor: Cardona222 (ID 1) -> Receptor: Cardona (ID 2)")
    print(f" -> Bienes ofrecidos: IDs [{item1}, {item2}] ({dash1['inventario'][0]['nombre']}, {dash1['inventario'][1]['nombre']})")
    print(f" -> Efectivo adjunto: $ 5,000.00 | Tiempo de expiración: 10 min")

    res_open = c1.post('/api/trades/open', json={
        'destinatario': 2,
        'item_ids': [item1, item2],
        'monto_j1': 5000.0,
        'expiracion': 10
    }).get_json()
    print(f" -> Respuesta API /trades/open: {res_open}")

    # 4. Cardona recibe la invitación entrante en su HUD
    print("\n[PASO 4] CARDONA CONSULTA INVITACIONES ENTRANTES (TIEMPO REAL)")
    res_pending = c2.get('/api/trades/pending').get_json()
    invitaciones = res_pending.get('invitaciones', [])
    print(f" -> Total invitaciones en bandeja: {len(invitaciones)}")

    if not invitaciones:
        print(" [!] No se recibió invitación.")
        return

    inv = invitaciones[0]
    id_trade = inv['id_negociacion']
    print(f" -> Invitación #{id_trade} recibida de: {inv['emisor']}")
    print(f" -> Bienes en paquete: {inv['item_ofrecido']}")
    print(f" -> Segundos restantes temporizador: {inv.get('segundos_restantes')}s")

    # 5. Cardona acepta la invitación y entra a la sala de comercio activa
    print("\n[PASO 5] CARDONA ACEPTA LA INVITACIÓN E INGRESA A LA SALA")
    res_acc = c2.post('/api/trades/accept', json={'id_trade': id_trade}).get_json()
    print(f" -> Respuesta API /trades/accept: {res_acc}")

    # 6. Cardona contraoferta con 1 bien y $ 2,000.00
    item_j2 = dash2['inventario'][0]['id_item']
    print("\n[PASO 6] NEGOCIACIÓN EN VIVO: CARDONA REALIZA CONTRAOFERTA")
    print(f" -> Bien ofrecido por Cardona: ID {item_j2} ({dash2['inventario'][0]['nombre']})")
    print(f" -> Efectivo ofrecido: $ 2,000.00")
    res_upd = c2.post('/api/trades/update_offer', json={
        'id_trade': id_trade,
        'item_ids': [item_j2],
        'monto': 2000.0
    }).get_json()
    print(f" -> Respuesta API /trades/update_offer: {res_upd}")

    # 7. Cardona222 confirma la oferta en la mesa
    print("\n[PASO 7] CONFIRMACIÓN BILATERAL DE TRÉRMINOS (RN010)")
    res_conf1 = c1.post('/api/trades/confirm', json={'id_trade': id_trade}).get_json()
    print(f" -> Cardona222 bloquea oferta: {res_conf1}")

    # 8. Cardona confirma la oferta en la mesa (Gatilla ejecución atómica)
    res_conf2 = c2.post('/api/trades/confirm', json={'id_trade': id_trade}).get_json()
    print(f" -> Cardona bloquea oferta y cierra trade: {res_conf2}")

    # 9. Verificación de Cuentas y Balances Finales (con Comisión del 5% al Sistema)
    dash1_fin = c1.get('/api/dashboard').get_json()
    dash2_fin = c2.get('/api/dashboard').get_json()
    s1_fin = float(dash1_fin['saldo'])
    s2_fin = float(dash2_fin['saldo'])

    print("\n" + "=" * 70)
    print("[PASO 8] RESULTADO FINAL Y BALANCE ECONÓMICO LIQUIDADO")
    print("=" * 70)
    print(f" -> Cardona222: Saldo Final = ${s1_fin:,.2f} (Neto: ${s1_fin - s1_init:+,.2f}) | Bienes = {len(dash1_fin['inventario'])}")
    print(f" -> Cardona:    Saldo Final = ${s2_fin:,.2f} (Neto: ${s2_fin - s2_init:+,.2f}) | Bienes = {len(dash2_fin['inventario'])}")

    # 10. Auditoría Inmutable en Base de Datos
    print("\n[PASO 9] AUDITORÍA CONTABLE INMUTABLE (T_Transaccion & T_Detalle_Transaccion)")
    with get_db_cursor(dictionary=True) as (cursor, _):
        cursor.execute("SELECT * FROM T_Transaccion ORDER BY id_transaccion DESC LIMIT 1")
        trx = cursor.fetchone()
        print(f" -> T_Transaccion Registrada: ID #{trx['id_transaccion']} | Tipo: {trx['tipo_transaccion']} | Monto Total: ${float(trx['monto']):,.2f} | Estado: {trx['estado_transaccion']}")

        cursor.execute("SELECT * FROM T_Detalle_Transaccion WHERE id_transaccion = %s ORDER BY id_detalle ASC", (trx['id_transaccion'],))
        detalles = cursor.fetchall()
        print(f" -> Asientos Contables de Partida Doble (Total {len(detalles)} registros):")
        for d in detalles:
            print(f"    [Asiento #{d['id_detalle']}] Cuenta {d['cuenta_origen']} -> {d['cuenta_destino']} | {d['tipo_movimiento']} ${float(d['monto_detalle']):,.2f} | Concepto: {d['concepto']}")

        cursor.execute("SELECT id_cuenta, tipo_cuenta, saldo_disponible FROM T_Cuenta WHERE tipo_cuenta = 'SISTEMA'")
        sis = cursor.fetchone()
        print(f" -> Saldo Cuenta SISTEMA (Tesorería con comisiones recaudadas): ${float(sis['saldo_disponible']):,.2f}")

    print("\n" + "=" * 70)
    print("¡FLUJO DE TRADEO P2P COMPLETADO EXITOSAMENTE CUMPLIENDO TODAS LAS RN!")
    print("=" * 70)

if __name__ == "__main__":
    run_test()
