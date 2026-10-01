/**
 * Trade OS - Real-time Gaming HUD Client Script v3.0
 * Features:
 * - Collapsible Dock Sidebar with persistence
 * - Cyberpunk HUD Notifications & Modals
 * - Ultra-visual Item Rarity Engine & Dynamic Glowing Frames
 * - Real-time Countdown Timers for all Trade Lifecycle Steps
 * - Interactive Transaction Invoice / Factura Modal
 * - Bilateral Multi-Item Trading Engine
 */

// Global State
let currentTradeId = null;
let pollingInterval = null;
let roomSecondsRemaining = null;
let roomTimerInterval = null;
let pendingInvitesTimers = {};

// ==========================================
// 1. COLLAPSIBLE SIDEBAR ENGINE (DOCK MODE)
// ==========================================
function initSidebarState() {
    const isCollapsed = localStorage.getItem('sidebar_collapsed') === 'true';
    const body = document.body;
    const toggleIcon = document.getElementById('sidebar-toggle-icon');

    if (isCollapsed) {
        body.classList.add('sidebar-collapsed');
        if (toggleIcon) toggleIcon.textContent = 'chevron_right';
    } else {
        body.classList.remove('sidebar-collapsed');
        if (toggleIcon) toggleIcon.textContent = 'chevron_left';
    }
}

function toggleSidebar() {
    const body = document.body;
    const isCollapsed = body.classList.toggle('sidebar-collapsed');
    const toggleIcon = document.getElementById('sidebar-toggle-icon');

    if (toggleIcon) {
        toggleIcon.textContent = isCollapsed ? 'chevron_right' : 'chevron_left';
    }
    localStorage.setItem('sidebar_collapsed', isCollapsed);
}

// ==========================================
// 2. HUD CYBERPUNK NOTIFICATIONS & MODALS
// ==========================================
function showHudToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('hud-toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'pointer-events-auto flex items-center gap-3 p-3.5 rounded-xl bg-[#1c1a25]/95 backdrop-blur-2xl border shadow-2xl transition-all duration-300 transform translate-y-2 opacity-0';
    
    let borderColor = 'border-primary/40';
    let iconColor = 'text-primary';
    let icon = 'info';
    let glow = 'shadow-[0_0_20px_rgba(0,229,255,0.25)]';

    if (type === 'success') {
        borderColor = 'border-tertiary/40';
        iconColor = 'text-tertiary';
        icon = 'check_circle';
        glow = 'shadow-[0_0_20px_rgba(91,233,173,0.3)]';
    } else if (type === 'error') {
        borderColor = 'border-error/40';
        iconColor = 'text-error';
        icon = 'error';
        glow = 'shadow-[0_0_20px_rgba(255,180,171,0.3)]';
    } else if (type === 'warning') {
        borderColor = 'border-[#f59e0b]/40';
        iconColor = 'text-[#f59e0b]';
        icon = 'warning';
        glow = 'shadow-[0_0_20px_rgba(245,158,11,0.3)]';
    }

    toast.classList.add(borderColor, glow);
    toast.innerHTML = `
        <span class="material-symbols-outlined ${iconColor} text-[22px] shrink-0">${icon}</span>
        <div class="flex flex-col flex-1 min-w-0">
            <span class="font-headline-sm text-xs uppercase tracking-wider text-on-surface font-bold">${type}</span>
            <span class="font-body-sm text-xs text-on-surface-variant leading-snug">${message}</span>
        </div>
        <button type="button" class="text-on-surface-variant hover:text-on-surface ml-auto p-1" onclick="this.parentElement.remove()">
            <span class="material-symbols-outlined text-[16px]">close</span>
        </button>
    `;

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
    });

    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

async function showHudConfirm(options = {}) {
    const {
        title = '¿ESTÁS SEGURO?',
        text = 'Esta acción no se puede deshacer.',
        icon = 'warning',
        confirmButtonText = 'CONFIRMAR',
        cancelButtonText = 'CANCELAR',
        isDanger = false
    } = options;

    if (window.Swal) {
        const result = await Swal.fire({
            title: title,
            text: text,
            icon: icon,
            showCancelButton: true,
            confirmButtonText: confirmButtonText,
            cancelButtonText: cancelButtonText,
            customClass: {
                popup: 'hud-swal',
                title: 'hud-swal-title',
                htmlContainer: 'hud-swal-html',
                confirmButton: isDanger ? 'hud-swal-cancel !bg-error-container !text-error' : 'hud-swal-confirm',
                cancelButton: 'hud-swal-cancel'
            },
            background: '#1c1a25',
            color: '#e6e0f0',
            buttonsStyling: false
        });
        return result.isConfirmed;
    }

    return window.confirm(`${title}\n${text}`);
}

// ==========================================
// 3. ITEM IMAGE CATALOG & ULTRA-VISUAL RARITY
// ==========================================
const ItemCatalog = {
    presets: {
        'mustang': {
            image: '/static/img/login_bg.png',
            rarity: 'legendary',
            category: 'VEHÍCULO'
        },
        'coche': {
            image: 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=240&auto=format&fit=crop&q=80',
            rarity: 'epic',
            category: 'VEHÍCULO'
        },
        'vehiculo': {
            image: 'https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=240&auto=format&fit=crop&q=80',
            rarity: 'epic',
            category: 'VEHÍCULO'
        },
        'moto': {
            image: 'https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=240&auto=format&fit=crop&q=80',
            rarity: 'rare',
            category: 'VEHÍCULO'
        },
        'llave': {
            image: 'https://images.unsplash.com/photo-1582139329536-e7284fece509?w=240&auto=format&fit=crop&q=80',
            rarity: 'rare',
            category: 'ACCESO'
        },
        'pistola': {
            image: 'https://images.unsplash.com/photo-1595590424283-b8f17842773f?w=240&auto=format&fit=crop&q=80',
            rarity: 'rare',
            category: 'ARMAMENTO'
        },
        'glock': {
            image: 'https://images.unsplash.com/photo-1585589074467-a2f07297d264?w=240&auto=format&fit=crop&q=80',
            rarity: 'rare',
            category: 'ARMAMENTO'
        },
        'rifle': {
            image: 'https://images.unsplash.com/photo-1584441405886-bc91be61e56a?w=240&auto=format&fit=crop&q=80',
            rarity: 'epic',
            category: 'ARMAMENTO'
        },
        'ak': {
            image: 'https://images.unsplash.com/photo-1584441405886-bc91be61e56a?w=240&auto=format&fit=crop&q=80',
            rarity: 'epic',
            category: 'ARMAMENTO'
        },
        'cuchillo': {
            image: 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=240&auto=format&fit=crop&q=80',
            rarity: 'common',
            category: 'CORTANTE'
        },
        'maletin': {
            image: 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=240&auto=format&fit=crop&q=80',
            rarity: 'legendary',
            category: 'VALIOSO'
        },
        'dinero': {
            image: 'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=240&auto=format&fit=crop&q=80',
            rarity: 'legendary',
            category: 'DIVISA'
        },
        'oro': {
            image: 'https://images.unsplash.com/photo-1610375461246-83df859d849d?w=240&auto=format&fit=crop&q=80',
            rarity: 'legendary',
            category: 'METAL PRECIOSO'
        },
        'diamante': {
            image: 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=240&auto=format&fit=crop&q=80',
            rarity: 'legendary',
            category: 'JOYA'
        },
        'rolex': {
            image: 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=240&auto=format&fit=crop&q=80',
            rarity: 'legendary',
            category: 'LUJO'
        },
        'laptop': {
            image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=240&auto=format&fit=crop&q=80',
            rarity: 'epic',
            category: 'CYBER-TECH'
        },
        'chip': {
            image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=240&auto=format&fit=crop&q=80',
            rarity: 'epic',
            category: 'HARDWARE'
        },
        'botiquin': {
            image: 'https://images.unsplash.com/photo-1603398938378-e54eab446dde?w=240&auto=format&fit=crop&q=80',
            rarity: 'common',
            category: 'MÉDICO'
        },
        'comida': {
            image: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=240&auto=format&fit=crop&q=80',
            rarity: 'common',
            category: 'CONSUMIBLE'
        },
        'agua': {
            image: 'https://images.unsplash.com/photo-1548839140-29a749e1bc4e?w=240&auto=format&fit=crop&q=80',
            rarity: 'common',
            category: 'CONSUMIBLE'
        }
    },

    fallbackPool: [
        { image: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=240&auto=format&fit=crop&q=80', rarity: 'rare', category: 'ACTIVO' },
        { image: 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=240&auto=format&fit=crop&q=80', rarity: 'epic', category: 'TECNOLOGÍA' },
        { image: 'https://images.unsplash.com/photo-1563089145-599997674d42?w=240&auto=format&fit=crop&q=80', rarity: 'legendary', category: 'ESPECIAL' },
        { image: 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=240&auto=format&fit=crop&q=80', rarity: 'common', category: 'INSUMO' }
    ],

    getItemData(name) {
        const cleanName = (name || '').toLowerCase().trim();
        for (const [keyword, data] of Object.entries(this.presets)) {
            if (cleanName.includes(keyword)) {
                return data;
            }
        }
        let hash = 0;
        for (let i = 0; i < cleanName.length; i++) {
            hash = (hash << 5) - hash + cleanName.charCodeAt(i);
            hash |= 0;
        }
        const index = Math.abs(hash) % this.fallbackPool.length;
        return this.fallbackPool[index];
    },

    getRarityClass(rarity) {
        switch (rarity) {
            case 'legendary': return 'rarity-frame-legendary';
            case 'epic': return 'rarity-frame-epic';
            case 'rare': return 'rarity-frame-rare';
            default: return 'rarity-frame-common';
        }
    },

    getRarityBadge(rarity) {
        switch (rarity) {
            case 'legendary':
                return '<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold uppercase bg-[#ffd700]/25 text-[#ffd700] border border-[#ffd700]/40 shadow-[0_0_8px_rgba(255,215,0,0.4)] shrink-0">★ LEG</span>';
            case 'epic':
                return '<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold uppercase bg-[#c026d3]/25 text-[#c026d3] border border-[#c026d3]/40 shadow-[0_0_8px_rgba(192,38,211,0.4)] shrink-0">◆ ÉPICO</span>';
            case 'rare':
                return '<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold uppercase bg-primary-container/25 text-primary border border-primary-container/40 shadow-[0_0_8px_rgba(0,229,255,0.3)] shrink-0">▲ RARO</span>';
            default:
                return '<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold uppercase bg-tertiary/25 text-tertiary border border-tertiary/40 shrink-0">● COMÚN</span>';
        }
    },

    renderItemCard(item) {
        const data = this.getItemData(item.nombre);
        const priceFmt = Number(item.precio || 0).toLocaleString('en-US', {minimumFractionDigits: 2});
        const rarityClass = this.getRarityClass(data.rarity);
        const badge = this.getRarityBadge(data.rarity);

        return `
            <div class="flex items-center gap-2.5 p-2 rounded-xl ${rarityClass} shadow-md shrink-0 w-full select-none relative overflow-hidden transition-all duration-200 hover:brightness-110">
                <!-- Tactical Corner Indicator -->
                <div class="absolute top-1 left-1 w-1.5 h-1.5 border-t border-l border-white/50 pointer-events-none"></div>

                <!-- High-Impact Image Render -->
                <div class="relative w-11 h-11 rounded-lg bg-surface-container-lowest overflow-hidden shrink-0 border border-white/15">
                    <img src="${data.image}" alt="${item.nombre}" class="w-full h-full object-cover"/>
                </div>

                <!-- Item Metadata -->
                <div class="flex flex-col min-w-0 flex-1 justify-center">
                    <div class="flex items-center justify-between gap-1.5 w-full">
                        <span class="font-headline-sm text-xs text-on-surface font-bold uppercase tracking-wide truncate" title="${item.nombre}">${item.nombre}</span>
                        ${badge}
                    </div>
                    <div class="flex items-center justify-between gap-1.5 w-full mt-0.5">
                        <span class="font-label-sm text-[10px] text-on-surface-variant uppercase tracking-wider truncate">${data.category}</span>
                        <span class="font-label-lg text-xs text-tertiary font-mono font-bold shrink-0">$ ${priceFmt}</span>
                    </div>
                </div>
            </div>
        `;
    }
};

function decorateItemPlaceholders() {
    document.querySelectorAll('.item-img-placeholder').forEach(el => {
        const name = el.dataset.itemName;
        if (!name) return;
        const data = ItemCatalog.getItemData(name);
        el.innerHTML = `<img src="${data.image}" alt="${name}" class="w-full h-full object-cover"/>`;
    });
}

// ==========================================
// 4. MULTI-ITEM SELECTION HELPERS
// ==========================================
function updateInviteSelectedCount() {
    const checked = document.querySelectorAll('input[name="invite_items"]:checked');
    const countEl = document.getElementById('invite-selected-count');
    if (countEl) {
        countEl.textContent = `${checked.length} seleccionado${checked.length === 1 ? '' : 's'}`;
    }
}

function updateRoomSelectedItems() {
    const checked = document.querySelectorAll('input[name="room_my_items"]:checked');
    const countEl = document.getElementById('room-selected-count');
    if (countEl) {
        countEl.textContent = `${checked.length} ítem${checked.length === 1 ? '' : 's'}`;
    }
}

// ==========================================
// 5. COUNTDOWN TIMER ENGINE (TEMPORIZADORES EN TIEMPO REAL)
// ==========================================
function formatSeconds(sec) {
    if (isNaN(sec) || sec < 0) sec = 0;
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function startRoomCountdown(seconds) {
    roomSecondsRemaining = seconds;
    if (roomTimerInterval) clearInterval(roomTimerInterval);

    const clockEl = document.getElementById('trade-countdown-clock');
    const timerContainer = document.getElementById('trade-timer-container');

    const tick = () => {
        if (roomSecondsRemaining <= 0) {
            if (clockEl) clockEl.innerText = '00:00';
            if (roomTimerInterval) clearInterval(roomTimerInterval);
            
            showHudToast("¡TIEMPO AGOTADO! La negociación ha expirado por inactividad.", 'error');
            cancelCurrentTrade(true);
            return;
        }

        if (clockEl) clockEl.innerText = formatSeconds(roomSecondsRemaining);

        if (timerContainer) {
            if (roomSecondsRemaining <= 25) {
                timerContainer.classList.add('hud-timer-urgent');
                if (clockEl) {
                    clockEl.classList.add('text-error');
                    clockEl.classList.remove('text-primary');
                }
            } else {
                timerContainer.classList.remove('hud-timer-urgent');
                if (clockEl) {
                    clockEl.classList.remove('text-error');
                    clockEl.classList.add('text-primary');
                }
            }
        }

        roomSecondsRemaining--;
    };

    tick();
    roomTimerInterval = setInterval(tick, 1000);
}

// ==========================================
// 6. DASHBOARD TELEMETRY & INVENTORY
// ==========================================
async function updateDashboard() {
    try {
        const response = await fetch('/api/dashboard');
        if (!response.ok) return;
        const data = await response.json();

        if (data.error) return;

        // Update 4 Telemetry Cards
        const saldoEl = document.getElementById('saldo-display');
        if (saldoEl && data.saldo !== undefined && data.saldo !== null) {
            saldoEl.innerText = `$ ${Number(data.saldo).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }

        const patEl = document.getElementById('patrimonio-display');
        if (patEl && data.patrimonio_total !== undefined) {
            patEl.innerText = `$ ${Number(data.patrimonio_total).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }

        const valBienesEl = document.getElementById('valor-bienes-display');
        if (valBienesEl && data.valor_inventario !== undefined) {
            valBienesEl.innerText = `$ ${Number(data.valor_inventario).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }

        const itemsCountEl = document.getElementById('items-count-display');
        if (itemsCountEl && data.total_items !== undefined) {
            itemsCountEl.innerText = `${data.total_items} / ${data.limite_bienes || 100}`;
        }

        const itemsStatusEl = document.getElementById('items-status-display');
        if (itemsStatusEl && data.items_libres !== undefined) {
            itemsStatusEl.innerHTML = `${data.items_libres} Libres • <span class="text-error font-bold">${data.items_con_deuda || 0} Con Deuda</span>`;
        }

        const tradesCountEl = document.getElementById('trades-count-display');
        if (tradesCountEl && data.total_trades !== undefined) {
            tradesCountEl.innerHTML = `${data.total_trades} <span class="text-sm font-normal text-outline">Trades</span>`;
        }

        const comisionEl = document.getElementById('comision-display');
        if (comisionEl && data.porcentaje_comision !== undefined) {
            comisionEl.innerText = `Tasa Red: ${Number(data.porcentaje_comision).toFixed(1)}% Drenaje`;
        }


        // Update Inventory Table
        const invListEl = document.getElementById('inventory-list');
        if (invListEl && data.inventario) {
            if (data.inventario.length === 0) {
                invListEl.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center py-8 text-on-surface-variant">
                            <span class="material-symbols-outlined text-[28px] text-outline">inventory_2</span>
                            <p class="mt-1 font-label-sm text-xs">No posees bienes o activos registrados actualmente.</p>
                        </td>
                    </tr>
                `;
                return;
            }

            invListEl.innerHTML = '';
            data.inventario.forEach(function(item) {
                const row = document.createElement('tr');
                row.className = 'group hover:bg-surface-container/70 transition-all';
                
                const precioFmt = Number(item.precio || 0).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                const hasDebt = item.tiene_deuda;
                const itemData = ItemCatalog.getItemData(item.nombre);
                const rarityBadge = ItemCatalog.getRarityBadge(itemData.rarity);
                const rarityClass = ItemCatalog.getRarityClass(itemData.rarity);
                
                const statusBadge = hasDebt 
                    ? `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-error-container/20 text-error font-bold text-xs border border-error/30"><span class="w-1.5 h-1.5 rounded-full bg-error"></span> CON DEUDA</span>`
                    : `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-tertiary-container/15 text-tertiary font-bold text-xs border border-tertiary/25"><span class="w-1.5 h-1.5 rounded-full bg-tertiary shadow-[0_0_6px_#5be9ad]"></span> LIBRE / OK</span>`;

                row.innerHTML = `
                    <td class="py-3 px-space-md font-headline-sm text-sm text-on-surface font-semibold group-hover:text-primary transition-colors">
                        <div class="flex items-center gap-3">
                            <div class="w-12 h-12 rounded-xl bg-surface-container-lowest overflow-hidden border border-white/20 shrink-0 shadow-md ${rarityClass}">
                                <img src="${itemData.image}" alt="${item.nombre}" class="w-full h-full object-cover group-hover:scale-115 transition-transform duration-300"/>
                            </div>
                            <div class="flex flex-col">
                                <div class="flex items-center gap-2">
                                    <span class="font-bold">${item.nombre}</span>
                                    ${rarityBadge}
                                </div>
                                <span class="font-label-sm text-[10px] text-outline uppercase">${itemData.category}</span>
                            </div>
                        </div>
                    </td>
                    <td class="py-3 px-space-md text-right font-label-lg text-sm text-tertiary font-bold font-mono">
                        $ ${precioFmt}
                    </td>
                    <td class="py-3 px-space-md text-center">
                        ${statusBadge}
                    </td>
                    <td class="py-3 px-space-md text-right">
                        <a href="/trade" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-surface-container-highest hover:bg-primary-container hover:text-on-primary-container text-primary font-headline-sm text-xs uppercase tracking-wider transition-all shadow-sm">
                            <span class="material-symbols-outlined text-[14px]">swap_horiz</span>
                            <span>Tradear</span>
                        </a>
                    </td>
                `;
                invListEl.appendChild(row);
            });
        }
    } catch (e) {
        console.error("[Dashboard Error]", e);
    }
}

// ==========================================
// 7. SEND MULTI-ITEM TRADE INVITATION
// ==========================================
async function sendTradeInvite() {
    const targetPlayerId = document.getElementById('target-player-id')?.value;
    const checkedItems = Array.from(document.querySelectorAll('input[name="invite_items"]:checked')).map(cb => cb.value);
    const money = document.getElementById('my_money')?.value;
    const sendBtn = document.getElementById('btn-invite');

    if (!targetPlayerId) {
        showHudToast("Por favor ingresa un ID numérico de jugador válido.", 'warning');
        return;
    }

    const currentUserId = document.body.dataset.userId;
    if (String(targetPlayerId).trim() === String(currentUserId).trim()) {
        showHudToast("No puedes iniciar una negociación contigo mismo.", 'warning');
        return;
    }

    if (checkedItems.length === 0 && (!money || Number(money) <= 0)) {
        showHudToast("Debes ofrecer al menos un bien o un monto de dinero.", 'warning');
        return;
    }

    try {
        if (sendBtn) {
            sendBtn.innerHTML = '<span class="material-symbols-outlined text-[20px] animate-spin">sync</span><span>TRANSMITIENDO OFERTA...</span>';
            sendBtn.classList.add('pointer-events-none', 'opacity-80');
        }

        const response = await fetch('/api/trades/open', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                destinatario: targetPlayerId,
                item_ids: checkedItems,
                monto_j1: money || 0,
                expiracion: 2 // 2 minutos para aceptar
            })
        });
        const result = await response.json();

        if (sendBtn) {
            sendBtn.innerHTML = '<span class="material-symbols-outlined text-[22px]">sync_alt</span><span>Transmitir Invitación de Trade</span>';
            sendBtn.classList.remove('pointer-events-none', 'opacity-80');
        }

        if (result.success) {
            showHudToast("Oferta P2P transmitida exitosamente (2 min para aceptar)", 'success');
            document.getElementById('target-player-id').value = '';
            document.getElementById('my_money').value = '';
            document.querySelectorAll('input[name="invite_items"]:checked').forEach(cb => cb.checked = false);
            updateInviteSelectedCount();
            checkIncomingTrades();
        } else {
            showHudToast(result.message, 'error');
        }
    } catch (e) {
        console.error("[Invite Error]", e);
        if (sendBtn) {
            sendBtn.innerHTML = '<span class="material-symbols-outlined text-[22px]">sync_alt</span><span>Transmitir Invitación de Trade</span>';
            sendBtn.classList.remove('pointer-events-none', 'opacity-80');
        }
        showHudToast("Error de conexión al enviar invitación: " + e.message, 'error');
    }
}

// ==========================================
// 8. INCOMING TRADES & ACTIVE ROOM CHECK
// ==========================================
async function checkIncomingTrades() {
    const listEl = document.getElementById('trades-pending-list');
    const headerDot = document.getElementById('header-notif-dot');

    try {
        // 1. Check Pending Invites
        const response = await fetch('/api/trades/pending');
        if (response.ok) {
            const data = await response.json();
            if (data.success && listEl) {
                if (data.invitaciones.length === 0) {
                    listEl.innerHTML = `
                        <div class="flex flex-col items-center justify-center p-8 rounded-2xl bg-surface-container-low/70 backdrop-blur-xl text-center gap-2 border border-outline-variant/10 shadow-md">
                            <span class="material-symbols-outlined text-outline text-[32px]">inbox</span>
                            <span class="font-headline-sm text-sm uppercase text-on-surface">No hay invitaciones pendientes</span>
                            <p class="font-body-sm text-xs text-on-surface-variant max-w-xs">
                                Tu cola de solicitudes P2P está despejada. Las nuevas ofertas entrantes aparecerán aquí al instante.
                            </p>
                        </div>
                    `;
                    if (headerDot) headerDot.classList.add('hidden');
                } else {
                    listEl.innerHTML = '';
                    if (headerDot) headerDot.classList.remove('hidden');

                    data.invitaciones.forEach(trade => {
                        const card = document.createElement('div');
                        card.className = 'flex flex-col rounded-2xl bg-surface-container/90 backdrop-blur-2xl p-4 shadow-xl gap-3 border border-secondary/30 relative overflow-hidden';
                        
                        const montoFmt = Number(trade.monto_j1 || 0).toLocaleString('en-US', {minimumFractionDigits: 2});
                        const itemsList = trade.items_list || [];
                        const seconds = trade.segundos_restantes !== undefined ? trade.segundos_restantes : 120;

                        let itemsHtml = '<span class="font-bold text-on-surface-variant text-xs">Sin Ítems Adjuntos</span>';
                        if (itemsList.length > 0) {
                            itemsHtml = itemsList.map(it => ItemCatalog.renderItemCard(it)).join('');
                        }

                        const itemsCount = itemsList.length;
                        const countBadge = itemsCount > 0 ? `<span class="text-primary font-mono font-bold">(${itemsCount})</span>` : '';

                        card.innerHTML = `
                            <div class="flex items-start justify-between gap-2">
                                <div class="flex items-center gap-2.5">
                                    <div class="w-10 h-10 rounded-xl bg-surface-container-high flex items-center justify-center text-primary-fixed border border-primary/20">
                                        <span class="material-symbols-outlined text-[20px]">person</span>
                                    </div>
                                    <div class="flex flex-col">
                                        <div class="flex items-center gap-1.5">
                                            <span class="font-headline-sm text-sm text-on-surface font-bold">${trade.emisor}</span>
                                            <span class="font-label-sm text-[10px] px-1.5 py-0.5 rounded bg-surface-container-highest text-primary font-mono font-bold">#${trade.id_jugador_1}</span>
                                        </div>
                                        <span class="font-body-sm text-xs text-on-surface-variant">te invita a comerciar</span>
                                    </div>
                                </div>
                                <div class="flex items-center gap-1 px-2.5 py-1 rounded-full bg-error-container/20 text-error border border-error/30 font-label-sm text-[11px] font-bold">
                                    <span class="material-symbols-outlined text-[14px] animate-pulse">timer</span>
                                    <span id="pending-timer-${trade.id_negociacion}">${formatSeconds(seconds)}</span>
                                </div>
                            </div>

                            <div class="flex flex-col gap-2 p-3 rounded-xl bg-surface-container-low/90 border border-outline-variant/10 text-xs">
                                <div class="flex items-center justify-between text-outline uppercase text-[10px] font-bold">
                                    <span>Bienes Ofrecidos ${countBadge}:</span>
                                    ${itemsCount > 2 ? '<span class="text-[9px] text-on-surface-variant font-normal">desplaza para ver todos ↓</span>' : ''}
                                </div>
                                <div class="flex flex-col gap-2 max-h-52 overflow-y-auto pr-1">${itemsHtml}</div>
                                <div class="flex items-center justify-between text-on-surface pt-2 border-t border-outline-variant/10">
                                    <span class="text-outline uppercase text-[10px]">Efectivo Adjunto:</span>
                                    <span class="font-bold text-tertiary font-mono text-sm drop-shadow-[0_0_8px_rgba(91,233,173,0.5)]">$ ${montoFmt}</span>
                                </div>
                            </div>

                            <div class="grid grid-cols-2 gap-2">
                                <button onclick="aceptarTrade(${trade.id_negociacion})" 
                                        class="flex items-center justify-center gap-1.5 py-2.5 px-4 rounded-xl bg-primary-container text-on-primary-container font-headline-sm text-xs uppercase font-bold tracking-wider shadow-[0_0_16px_rgba(0,229,255,0.4)] hover:brightness-110 active:scale-95 transition-all">
                                    <span class="material-symbols-outlined text-[16px]">door_open</span>
                                    <span>Aceptar</span>
                                </button>
                                <button onclick="cancelTradeInvite(${trade.id_negociacion})" 
                                        class="flex items-center justify-center gap-1.5 py-2.5 px-4 rounded-xl bg-error-container/20 text-error hover:bg-error-container/40 font-headline-sm text-xs uppercase font-bold tracking-wider transition-all">
                                    <span class="material-symbols-outlined text-[16px]">close</span>
                                    <span>Rechazar</span>
                                </button>
                            </div>
                        `;
                        listEl.appendChild(card);
                    });
                }
            }
        }

        // 2. Check Active Trade Room
        const activeResponse = await fetch('/api/trades/active');
        if (activeResponse.ok) {
            const activeData = await activeResponse.json();
            const activePanel = document.getElementById('active-trade-panel');
            const negPanel = document.getElementById('negotiation-panel');

            if (activeData.success && activeData.data && activeData.data.id_negociacion) {
                currentTradeId = activeData.data.id_negociacion;
                if (activePanel) activePanel.style.display = 'flex';
                if (negPanel) negPanel.style.display = 'none';

                if (!pollingInterval) {
                    pollingInterval = setInterval(syncTradeTable, 1500);
                }
                syncTradeTable();
            } else {
                if (activePanel) activePanel.style.display = 'none';
                if (negPanel) negPanel.style.display = 'grid';
                if (pollingInterval) {
                    clearInterval(pollingInterval);
                    pollingInterval = null;
                }
                if (roomTimerInterval) {
                    clearInterval(roomTimerInterval);
                    roomTimerInterval = null;
                }
                currentTradeId = null;
            }
        }
    } catch (e) {
        console.error("[Trades Check Error]", e);
    }
}

// ==========================================
// 9. ACCEPT / REJECT INVITATION
// ==========================================
async function aceptarTrade(idTrade) {
    try {
        const response = await fetch('/api/trades/accept', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ id_trade: idTrade })
        });
        const result = await response.json();

        if (result.success) {
            showHudToast("Invitación aceptada. Ingresando a la sala de comercio...", 'success');
            const activeResponse = await fetch('/api/trades/active');
            const activeData = await activeResponse.json();
            if (activeData.success && activeData.data && activeData.data.id_negociacion) {
                currentTradeId = activeData.data.id_negociacion;
                document.getElementById('active-trade-panel').style.display = 'flex';
                document.getElementById('negotiation-panel').style.display = 'none';
                if (!pollingInterval) {
                    pollingInterval = setInterval(syncTradeTable, 1500);
                }
                syncTradeTable();
            } else {
                location.reload();
            }
        } else {
            showHudToast(result.message, 'error');
        }
    } catch (e) {
        console.error("[Accept Trade Error]", e);
        showHudToast("Error de conexión al aceptar invitación", 'error');
    }
}

async function cancelTradeInvite(idTrade) {
    try {
        const response = await fetch('/api/trades/cancel', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ id_trade: idTrade })
        });
        const result = await response.json();
        if (result.success) {
            showHudToast("Invitación rechazada.", 'info');
            checkIncomingTrades();
        }
    } catch (e) {
        console.error("[Reject Invite Error]", e);
    }
}

// ==========================================
// 10. SYNC ACTIVE TRADE TABLE (REAL-TIME POLLING & MULTI-ITEM)
// ==========================================
async function syncTradeTable() {
    if (!currentTradeId) return;

    try {
        const response = await fetch(`/api/trades/${currentTradeId}/status`);
        if (!response.ok) return;
        const result = await response.json();

        if (!result.success || !result.data) return;

        const trade = result.data;
        const myId = document.body.dataset.userId;
        const isPlayer1 = String(trade.id_jugador_1) === String(myId);

        // Synchronize room countdown timer
        if (trade.segundos_restantes !== undefined && trade.segundos_restantes !== null) {
            if (roomSecondsRemaining === null || Math.abs(roomSecondsRemaining - trade.segundos_restantes) > 3) {
                startRoomCountdown(trade.segundos_restantes);
            }
        }

        // Trade lifecycle termination states
        if (trade.estado === 'COMPLETADO') {
            if (pollingInterval) clearInterval(pollingInterval);
            if (roomTimerInterval) clearInterval(roomTimerInterval);
            await showHudConfirm({
                title: '¡COMERCIO COMPLETADO!',
                text: 'La transferencia de ítems y fondos ha sido ejecutada e inscrita en el registro inmutable.',
                icon: 'success',
                confirmButtonText: 'VER EN DASHBOARD'
            });
            window.location.href = '/dashboard';
            return;
        }

        if (trade.estado === 'CANCELADO' || trade.estado === 'EXPIRADO') {
            if (pollingInterval) clearInterval(pollingInterval);
            if (roomTimerInterval) clearInterval(roomTimerInterval);
            showHudToast(trade.estado === 'EXPIRADO' ? "La negociación expiró por tiempo límite." : "La negociación ha sido cancelada.", 'error');
            setTimeout(() => { window.location.href = '/trade'; }, 1500);
            return;
        }

        // Other Player Data & Multi-items
        const otherItemsList = isPlayer1 ? (trade.items_j2_details || trade.items_j2_list || []) : (trade.items_j1_details || trade.items_j1_list || []);
        const otherMoney = isPlayer1 ? trade.monto_j2 : trade.monto_j1;
        const otherConfirmed = isPlayer1 ? trade.confirmacion_j2 : trade.confirmacion_j1;

        const otherContainerEl = document.getElementById('other-items-container');
        const otherMoneyEl = document.getElementById('other-money-display');
        const otherBadgeEl = document.getElementById('other-status-badge');

        if (otherContainerEl) {
            if (otherItemsList.length > 0) {
                otherContainerEl.innerHTML = otherItemsList.map(it => ItemCatalog.renderItemCard(it)).join('');
            } else {
                const singleName = isPlayer1 ? (trade.nombre_item_j2 || trade.item_j2_nombre) : (trade.nombre_item_j1 || trade.item_j1_nombre);
                if (singleName) {
                    otherContainerEl.innerHTML = ItemCatalog.renderItemCard({ nombre: singleName, precio: 0 });
                } else {
                    otherContainerEl.innerHTML = '<p class="font-headline-sm text-sm text-on-surface-variant font-bold">Sin Ítems Ofrecidos</p>';
                }
            }
        }

        if (otherMoneyEl) {
            otherMoneyEl.innerText = `$ ${Number(otherMoney || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}`;
        }
        
        if (otherBadgeEl) {
            otherBadgeEl.innerHTML = otherConfirmed
                ? '<span class="text-tertiary flex items-center gap-1 font-bold"><span class="w-2 h-2 rounded-full bg-tertiary shadow-[0_0_8px_#5be9ad]"></span> ✓ LISTO / CONFIRMADO</span>'
                : '<span class="text-on-surface-variant flex items-center gap-1">⏳ Esperando Ajuste...</span>';
        }

        // My Confirmation Data
        const myConfirmed = isPlayer1 ? trade.confirmacion_j1 : trade.confirmacion_j2;
        const myBadgeEl = document.getElementById('my-status-badge');
        if (myBadgeEl) {
            myBadgeEl.innerHTML = myConfirmed
                ? '<span class="text-tertiary flex items-center gap-1 font-bold"><span class="w-2 h-2 rounded-full bg-tertiary shadow-[0_0_8px_#5be9ad]"></span> ✓ OFERTA BLOQUEADA</span>'
                : '<span class="text-on-surface-variant flex items-center gap-1">⏳ Pendiente de Confirmación</span>';
        }

        // My Offer initial sync if user has not yet interacted with room inputs
        if (!window.hasUserEditedTradeOffer) {
            const myRawIds = isPlayer1 ? (trade.items_j1_ids || (trade.id_item_j1 ? String(trade.id_item_j1) : '')) : (trade.items_j2_ids || (trade.id_item_j2 ? String(trade.id_item_j2) : ''));
            const myIdsArray = myRawIds ? String(myRawIds).split(',').map(s => s.trim()) : [];
            const myMoney = isPlayer1 ? trade.monto_j1 : trade.monto_j2;

            document.querySelectorAll('input[name="room_my_items"]').forEach(cb => {
                cb.checked = myIdsArray.includes(String(cb.value));
            });
            updateRoomSelectedItems();

            const moneyInput = document.getElementById('trade-money-input');
            if (moneyInput && (moneyInput.value === '' || moneyInput.value === '0' || moneyInput.value === '0.00')) {
                if (parseFloat(myMoney) > 0) {
                    moneyInput.value = parseFloat(myMoney);
                }
            }
        }
    } catch (e) {
        console.error("[Sync Table Error]", e);
    }
}

// ==========================================
// 11. UPDATE & CONFIRM TRADE OFFERS
// ==========================================
async function updateTradeOffer() {
    const checkedItems = Array.from(document.querySelectorAll('input[name="room_my_items"]:checked')).map(cb => cb.value);
    const money = document.getElementById('trade-money-input')?.value || 0;

    if (!currentTradeId) {
        showHudToast("No hay una sala de trade activa.", 'error');
        return;
    }

    try {
        const response = await fetch('/api/trades/update_offer', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                id_trade: currentTradeId,
                item_ids: checkedItems,
                monto: money
            })
        });
        const result = await response.json();
        if (result.success) {
            showHudToast("Oferta actualizada. Confirmaciones y tiempo reiniciados.", 'info');
            syncTradeTable();
        } else {
            showHudToast(result.message, 'error');
        }
    } catch (e) {
        console.error("[Update Offer Error]", e);
    }
}

async function confirmTrade() {
    if (!currentTradeId) {
        showHudToast("No hay una sala de trade activa.", 'error');
        return;
    }

    try {
        const response = await fetch('/api/trades/confirm', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ id_trade: currentTradeId })
        });
        const result = await response.json();
        if (result.success) {
            showHudToast("✓ Tu oferta ha sido bloqueada y confirmada.", 'success');
            syncTradeTable();
        } else {
            showHudToast(result.message, 'error');
        }
    } catch (e) {
        console.error("[Confirm Error]", e);
    }
}

async function cancelCurrentTrade(silent = false) {
    if (!currentTradeId) return;

    if (!silent) {
        const confirmed = await showHudConfirm({
            title: '¿ABORTAR NEGOCIACIÓN?',
            text: 'Se cancelará el intercambio y se liberará la sala para ambos operadores.',
            icon: 'warning',
            confirmButtonText: 'SÍ, ABORTAR',
            cancelButtonText: 'CONTINUAR NEGOCIANDO',
            isDanger: true
        });
        if (!confirmed) return;
    }

    try {
        const response = await fetch('/api/trades/cancel', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ id_trade: currentTradeId })
        });
        const result = await response.json();
        if (result.success) {
            if (!silent) showHudToast("Negociación cancelada.", 'info');
            setTimeout(() => { location.reload(); }, 600);
        }
    } catch (e) {
        console.error("[Cancel Error]", e);
    }
}

// ==========================================
// 12. TRANSACTION HISTORY & INVOICE MODAL
// ==========================================
async function updateHistory() {
    try {
        const response = await fetch('/api/history');
        if (!response.ok) return;
        const data = await response.json();
        if (!data.success) return;

        const listEl = document.getElementById('history-list');
        if (!listEl) return;

        const history = data.historial || [];
        listEl.innerHTML = '';
        if (history.length === 0) {
            listEl.innerHTML = '<tr><td colspan="4" class="text-center py-8 text-on-surface-variant font-label-sm">Sin movimientos o transacciones registradas todavía.</td></tr>';
            return;
        }

        history.forEach(function(mov) {
            const row = document.createElement('tr');
            row.className = 'hover:bg-surface-container/70 cursor-pointer transition-colors group';
            row.title = 'Haz click para abrir la factura detallada';
            row.onclick = () => openInvoiceModal(mov);
            
            const montoNum = parseFloat(mov.monto || 0);
            const montoFmt = montoNum.toLocaleString('en-US', {minimumFractionDigits: 2});
            const isTrade = mov.tipo_transaccion === 'TRADEO_P2P';
            
            const tipoIcon = isTrade ? 'swap_horiz' : 'payments';
            const tipoColor = isTrade ? 'text-secondary' : 'text-primary';

            row.innerHTML = `
                <td class="py-3.5 px-space-md font-label-sm text-xs text-on-surface-variant font-mono">
                    ${mov.fecha_hora || '-'}
                </td>
                <td class="py-3.5 px-space-md">
                    <div class="flex items-center gap-2 font-label-md text-xs uppercase ${tipoColor} font-bold group-hover:underline">
                        <span class="material-symbols-outlined text-[18px]">${tipoIcon}</span>
                        <span>${mov.tipo_transaccion}</span>
                        <span class="material-symbols-outlined text-[14px] text-outline opacity-0 group-hover:opacity-100 transition-opacity">open_in_new</span>
                    </div>
                </td>
                <td class="py-3.5 px-space-md text-right font-label-lg text-sm font-bold font-mono text-tertiary">
                    $ ${montoFmt}
                </td>
                <td class="py-3.5 px-space-md text-center">
                    <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-tertiary/10 text-tertiary font-label-sm text-[10px] uppercase font-bold tracking-wider border border-tertiary/20">
                        <span class="w-1.5 h-1.5 rounded-full bg-tertiary shadow-[0_0_6px_#5be9ad]"></span>
                        ${mov.estado_transaccion}
                    </span>
                </td>
            `;
            listEl.appendChild(row);
        });
    } catch (e) {
        console.error("[History Error]", e);
    }
}

function openInvoiceModal(mov) {
    const modal = document.getElementById('invoice-modal');
    if (!modal || !mov) return;

    const montoNum = parseFloat(mov.monto || 0);
    const montoFmt = montoNum.toLocaleString('en-US', {minimumFractionDigits: 2});
    const trxId = mov.id_transaccion || Math.floor(1000 + Math.random() * 9000);

    // Populate Fields
    document.getElementById('invoice-id').innerText = `#TRX-${String(trxId).padStart(6, '0')}-RP`;
    document.getElementById('invoice-date').innerText = mov.fecha_hora || 'REGISTRO INMUTABLE';
    document.getElementById('invoice-type').innerText = mov.tipo_transaccion || 'TRADEO_P2P';
    document.getElementById('invoice-status').innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-tertiary"></span> ${mov.estado_transaccion || 'COMPLETADA'}`;
    document.getElementById('invoice-subtotal').innerText = `$ ${montoFmt}`;
    document.getElementById('invoice-total').innerText = `$ ${montoFmt}`;
    
    // Hash
    document.getElementById('invoice-hash').innerText = `0x${trxId}E9A${Math.random().toString(36).substring(2, 12).toUpperCase()}`;

    // Render Items
    const itemsContainer = document.getElementById('invoice-items-container');
    if (itemsContainer) {
        if (mov.nombre_item) {
            itemsContainer.innerHTML = ItemCatalog.renderItemCard({ nombre: mov.nombre_item, precio: mov.monto });
        } else if (mov.tipo_transaccion === 'PAGO_SALARIO') {
            itemsContainer.innerHTML = `
                <div class="flex items-center gap-3 p-3.5 rounded-xl bg-surface-container-high/60 border border-outline-variant/20">
                    <span class="material-symbols-outlined text-primary text-[28px]">work</span>
                    <div class="flex flex-col">
                        <span class="font-headline-sm text-xs font-bold text-on-surface">JORNADA LABORAL CERTIFICADA</span>
                        <span class="font-label-sm text-[10px] text-on-surface-variant">Liquidación directa desde cuenta de tesorería del servidor</span>
                    </div>
                </div>
            `;
        } else {
            itemsContainer.innerHTML = `
                <div class="flex items-center gap-3 p-3.5 rounded-xl bg-surface-container-high/60 border border-outline-variant/20">
                    <span class="material-symbols-outlined text-tertiary text-[28px]">currency_exchange</span>
                    <div class="flex flex-col">
                        <span class="font-headline-sm text-xs font-bold text-on-surface">INTERCAMBIO P2P VALORIZADO</span>
                        <span class="font-label-sm text-[10px] text-on-surface-variant">Transferencia bilateral protegida por Escrow</span>
                    </div>
                </div>
            `;
        }
    }

    modal.classList.remove('hidden');
}

// ==========================================
// 13. LIFECYCLE INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    // 1. Sidebar initial state
    initSidebarState();

    // 2. Decorate existing static placeholders
    decorateItemPlaceholders();

    // 3. Dashboard polling
    if (document.getElementById('saldo-display')) {
        updateDashboard();
        setInterval(updateDashboard, 4000);
    }

    // 4. Trade invitations polling
    if (document.getElementById('trades-pending-list')) {
        checkIncomingTrades();
        setInterval(checkIncomingTrades, 2000);
    }

    // 5. History polling
    if (document.getElementById('history-list')) {
        updateHistory();
        setInterval(updateHistory, 8000);
    }

    // 6. Real-time Admin Notifications & Live Auto-Update
    checkRealtimeNotifications();
    setInterval(checkRealtimeNotifications, 1500);
});

// ==========================================
// 14. REAL-TIME NOTIFICATIONS & LIVE AUTO-UPDATE
// ==========================================
let isCheckingNotifications = false;

async function checkRealtimeNotifications() {
    if (isCheckingNotifications) return;
    isCheckingNotifications = true;

    try {
        const res = await fetch('/api/notifications/unread');
        if (!res.ok) {
            isCheckingNotifications = false;
            return;
        }
        const data = await res.json();
        if (!data.success || !data.notifications || data.notifications.length === 0) {
            isCheckingNotifications = false;
            return;
        }

        const readIds = [];
        for (const notif of data.notifications) {
            readIds.push(notif.id_notificacion);
            showRealtimeAdminAlert(notif);
        }

        // Mark as read on server
        if (readIds.length > 0) {
            await fetch('/api/notifications/mark-read', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids: readIds })
            });
        }

        // Live Auto-Update of active view without page reload
        triggerLiveViewUpdates();

    } catch (e) {
        console.error("[Realtime Notifications Error]", e);
    } finally {
        isCheckingNotifications = false;
    }
}

function showRealtimeAdminAlert(notif) {
    const isSwal = Boolean(window.Swal);
    const title = notif.titulo || 'NOTIFICACIÓN DEL SISTEMA';
    const message = notif.mensaje || '';
    const tipo = (notif.tipo || 'ADMIN').toUpperCase();

    let iconType = 'info';
    let borderColor = 'border-primary/40';

    if (tipo === 'SUCCESS') {
        iconType = 'success';
        borderColor = 'border-tertiary/40';
    } else if (tipo === 'WARNING' || tipo === 'ERROR') {
        iconType = 'warning';
        borderColor = 'border-[#f59e0b]/40';
    }

    if (isSwal) {
        Swal.fire({
            title: title,
            html: `
                <div class="flex flex-col gap-3 text-left font-mono text-xs">
                    <p class="text-on-surface leading-relaxed text-sm">${message}</p>
                    <div class="flex items-center gap-1.5 pt-2 border-t border-outline-variant/20 text-tertiary text-[11px] font-bold">
                        <span class="material-symbols-outlined text-[16px] animate-pulse">sync</span>
                        <span>DATOS ACTUALIZADOS AUTOMÁTICAMENTE EN VIVO</span>
                    </div>
                </div>
            `,
            icon: iconType,
            confirmButtonText: 'ENTENDIDO // CONTINUAR',
            customClass: {
                popup: `hud-swal bg-[#1c1a25]/95 backdrop-blur-2xl ${borderColor} border shadow-[0_0_35px_rgba(0,229,255,0.3)] rounded-2xl`,
                title: 'text-on-surface font-headline-md uppercase text-sm font-bold tracking-wider',
                confirmButton: 'bg-primary text-on-primary font-bold text-xs uppercase px-6 py-2.5 rounded-xl shadow-md hover:brightness-110'
            },
            background: '#1c1a25',
            color: '#e6e0f0'
        });
    } else {
        showHudToast(`[${title}] ${message}`, tipo === 'SUCCESS' ? 'success' : (tipo === 'WARNING' ? 'warning' : 'info'), 6000);
    }
}

function triggerLiveViewUpdates() {
    // 1. Dashboard View
    if (document.getElementById('saldo-display') || document.getElementById('inventory-list')) {
        updateDashboard();
    }

    // 2. Trade View
    if (document.getElementById('invite-items-grid')) {
        refreshTradeInventory();
    }
    if (document.getElementById('trades-pending-list')) {
        checkIncomingTrades();
    }

    // 3. History View
    if (document.getElementById('history-list')) {
        updateHistory();
    }

    // 4. Admin View
    if (typeof refreshAdminData === 'function') {
        refreshAdminData();
    }
}

async function refreshTradeInventory() {
    const inviteGrid = document.getElementById('invite-items-grid');
    const roomGrid = document.getElementById('room-my-items-grid');
    if (!inviteGrid && !roomGrid) return;

    try {
        const response = await fetch('/api/dashboard');
        if (!response.ok) return;
        const data = await response.json();
        const items = data.inventario || [];

        // 1. Update Invite Grid
        if (inviteGrid) {
            if (items.length === 0) {
                inviteGrid.innerHTML = '<p class="text-xs text-on-surface-variant col-span-2 text-center py-4">No posees ítems transferibles.</p>';
            } else {
                const currentlyChecked = Array.from(document.querySelectorAll('input[name="invite_items"]:checked')).map(cb => cb.value);
                inviteGrid.innerHTML = '';
                items.forEach(item => {
                    const isChecked = currentlyChecked.includes(String(item.id_item));
                    const itemData = ItemCatalog.getItemData(item.nombre);
                    const label = document.createElement('label');
                    label.className = `flex items-center gap-2.5 p-2 rounded-lg bg-surface-container/60 hover:bg-surface-container cursor-pointer border border-outline-variant/10 transition-all select-none group ${isChecked ? 'border-primary bg-primary-container/10' : ''}`;
                    
                    label.innerHTML = `
                        <input type="checkbox" name="invite_items" value="${item.id_item}" data-name="${item.nombre}" data-price="${item.precio}" ${isChecked ? 'checked' : ''} onchange="updateInviteSelectedCount()"
                               class="rounded bg-surface-container-lowest border-outline-variant text-primary focus:ring-primary w-4 h-4 cursor-pointer"/>
                        <div class="w-8 h-8 rounded bg-surface-container-high flex items-center justify-center text-primary text-xs shrink-0 overflow-hidden ${itemData.rarity ? 'rarity-' + itemData.rarity : ''}">
                            <img src="${itemData.image}" alt="${item.nombre}" class="w-full h-full object-cover"/>
                        </div>
                        <div class="flex flex-col min-w-0">
                            <span class="font-headline-sm text-xs text-on-surface font-semibold truncate group-hover:text-primary transition-colors">${item.nombre}</span>
                            <span class="font-label-sm text-[10px] text-tertiary font-mono">$ ${Number(item.precio).toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
                        </div>
                    `;
                    inviteGrid.appendChild(label);
                });
            }
            updateInviteSelectedCount();
        }

        // 2. Update Room Grid
        if (roomGrid) {
            if (items.length === 0) {
                roomGrid.innerHTML = '<p class="text-center py-3 text-on-surface-variant font-label-sm text-xs">No posees ítems en tu inventario.</p>';
            } else {
                const currentlyChecked = Array.from(document.querySelectorAll('input[name="room_my_items"]:checked')).map(cb => cb.value);
                roomGrid.innerHTML = '';
                items.forEach(item => {
                    const isChecked = currentlyChecked.includes(String(item.id_item));
                    const itemData = ItemCatalog.getItemData(item.nombre);
                    const label = document.createElement('label');
                    label.className = `flex items-center gap-2.5 p-2 rounded-lg bg-surface-container/60 hover:bg-surface-container cursor-pointer border border-outline-variant/10 transition-all select-none group ${isChecked ? 'border-primary bg-primary-container/10' : ''}`;
                    
                    label.innerHTML = `
                        <input type="checkbox" name="room_my_items" value="${item.id_item}" data-name="${item.nombre}" data-price="${item.precio}" ${isChecked ? 'checked' : ''} onchange="window.hasUserEditedTradeOffer=true; updateRoomSelectedItems();"
                               class="rounded bg-surface-container-lowest border-outline-variant text-primary focus:ring-primary w-4 h-4 cursor-pointer"/>
                        <div class="w-7 h-7 rounded bg-surface-container-high flex items-center justify-center text-primary text-xs shrink-0 overflow-hidden ${itemData.rarity ? 'rarity-' + itemData.rarity : ''}">
                            <img src="${itemData.image}" alt="${item.nombre}" class="w-full h-full object-cover"/>
                        </div>
                        <div class="flex flex-col min-w-0 flex-1">
                            <span class="font-headline-sm text-xs text-on-surface truncate font-semibold">${item.nombre}</span>
                            <span class="font-label-sm text-[10px] text-tertiary font-mono">$ ${Number(item.precio).toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
                        </div>
                    `;
                    roomGrid.appendChild(label);
                });
            }
            updateRoomSelectedItems();
        }
    } catch (e) {
        console.error("[Refresh Trade Inv Error]", e);
    }
}

