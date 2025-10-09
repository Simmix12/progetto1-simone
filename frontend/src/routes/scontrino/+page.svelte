<script>
    import { onMount } from 'svelte';
    import { carrello } from '../../stores.js';

    const API_URL = 'http://127.0.0.1:5000';
    let scontrinoFinale = null;
    let errore = '';
    let isLoading = true;

    onMount(async () => {
        const carrelloCorrente = $carrello;
        if (Object.keys(carrelloCorrente).length === 0) {
            errore = "Operazione non valida: il carrello è già vuoto.";
            isLoading = false;
            return;
        }

        const carrelloArray = Object.values(carrelloCorrente).map(item => ({
            id: item.id,
            nome: item.nome,
            prezzo_lordo: item.prezzo_lordo,
            categoria: item.categoria,
            quantita: item.quantita
        }));

        try {
            const response = await fetch(`${API_URL}/api/scontrino`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(carrelloArray)
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.errore || "Errore sconosciuto.");
            scontrinoFinale = data;
            $carrello = {}; // Svuota il carrello dopo aver generato lo scontrino
        } catch (e) {
            errore = e.message;
        } finally {
            isLoading = false;
        }
    });

    // --- NUOVE FUNZIONI PER STAMPA E DOWNLOAD ---

    function stampaRicevuta() {
        window.print();
    }

    async function scaricaComePDF() {
        const scontrinoElement = document.querySelector('.contenitore-scontrino');
        if (!scontrinoElement) return;

        // Importiamo le librerie dinamicamente solo quando servono (lato client)
        const { default: jsPDF } = await import('jspdf');
        const { default: html2canvas } = await import('html2canvas');

        const canvas = await html2canvas(scontrinoElement, {
            scale: 3, // Aumenta la scala per una migliore qualità
            backgroundColor: '#ffffff',
            // Rimuoviamo i controlli per evitare che appaiano nel PDF
            ignoreElements: (element) => element.classList.contains('actions'),
        });
        
        const imgData = canvas.toDataURL('image/png');
        
        // Impostiamo dimensioni simili a uno scontrino termico (80mm di larghezza)
        const pdfWidth = 80; 
        const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
        const pdf = new jsPDF({
            orientation: 'portrait',
            unit: 'mm',
            format: [pdfWidth, pdfHeight]
        });

        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
        pdf.save(`scontrino-buyhub-${Date.now()}.pdf`);
    }
</script>

<svelte:head>
    <title>Scontrino - Buy Hub</title>
</svelte:head>

<div class="contenitore-scontrino">
    {#if isLoading}
        <p class="messaggio-caricamento">Generazione dello scontrino in corso...</p>
    {:else if scontrinoFinale}
        <!-- Questo titolo è visibile solo a schermo -->
        <h1 class="titolo-schermo">Grazie per il tuo acquisto!</h1>
        
        <!-- Intestazione Scontrino (visibile sempre, ma stilizzata diversamente) -->
        <div class="receipt-header">
            <h2>Buy Hub</h2>
            <p>Via del Commercio, 123 - 25121 Brescia (BS)</p>
            <p>P.IVA 01234567890</p>
            <p>Data: {new Date(scontrinoFinale.data_creazione).toLocaleString('it-IT')}</p>
        </div>

        <hr class="dashed"/>

        <!-- Voci Scontrino -->
        <ul class="receipt-items">
            {#each scontrinoFinale.voci as voce}
                <li class="receipt-item">
                    <div class="item-info">
                        <span class="item-qty-price">{voce.quantita}x {voce.nome_prodotto}</span>
                    </div>
                    <span class="item-total">{voce.prezzo_totale.toFixed(2)} €</span>
                </li>
            {/each}
        </ul>
        
        <hr class="dashed"/>

        <!-- Totali -->
        <div class="totali">
            <p><span>SUBTOTALE</span> <span>{(scontrinoFinale.totale_complessivo - scontrinoFinale.totale_iva).toFixed(2)} €</span></p>
            <p><span>TOTALE IVA</span> <span>{scontrinoFinale.totale_iva.toFixed(2)} €</span></p>
            <p class="complessivo"><span>TOTALE</span> <strong>{scontrinoFinale.totale_complessivo.toFixed(2)} €</strong></p>
        </div>

        <hr class="dashed"/>

        <!-- Footer Scontrino -->
        <div class="receipt-footer">
            <p>Grazie per averci scelto!</p>
            <p>www.buyhub.it</p>
        </div>
        
        <!-- Bottoni Azioni (nascosti in stampa) -->
        <div class="actions">
            <a href="/" class="action-btn secondary">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="m15 18-6-6 6-6"/>
                </svg>
                Torna al Negozio
            </a>
            <button on:click={stampaRicevuta} class="action-btn print">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 6 2 18 2 18 9"></polyline>
                    <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
                    <rect x="6" y="14" width="12" height="8"></rect>
                </svg>
                Stampa
            </button>
            <button on:click={scaricaComePDF} class="action-btn primary">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Scarica PDF
            </button>
        </div>

    {:else if errore}
        <h1>Oops! Qualcosa è andato storto.</h1>
        <p class="errore">{errore}</p>
        <a href="/carrello" class="action-btn secondary">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m15 18-6-6 6-6"/>
            </svg>
            Torna al Carrello
        </a>
    {/if}
</div>

<style>
    /* --- STILI GENERALI (VISUALIZZAZIONE A SCHERMO) --- */
    .contenitore-scontrino { 
        max-width: 600px; 
        margin: 2rem auto; 
        padding: 2.5rem; 
        background-color: var(--colore-sfondo-secondario); 
        border: 1px solid var(--colore-bordi); 
        border-radius: 12px; 
        font-family: 'Inter', sans-serif;
    }
    .titolo-schermo { text-align: center; color: var(--colore-accento); margin-bottom: 2rem; }
    h1, h2 { text-align: center; }
    
    .receipt-header h2 { margin: 0; color: var(--colore-testo); }
    .receipt-header p, .receipt-footer p { margin: 0.25rem 0; font-size: 0.9em; color: var(--colore-testo-secondario); text-align: center; }

    ul { list-style: none; padding: 0; }
    .receipt-item, .totali p { display: flex; justify-content: space-between; padding: 0.6rem 0; align-items: center;}
    .item-info { display: flex; flex-direction: column; }
    .item-qty-price { font-size: 1em; }
    hr.dashed { border: none; border-top: 2px dashed var(--colore-bordi); margin: 1.5rem 0; }
    .complessivo { font-size: 1.2rem; }
    .complessivo strong { font-size: 1.3rem; color: var(--colore-accento); }
    
    /* --- NUOVI STILI PER I BOTTONI --- */
    .actions {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 2.5rem;
        gap: 1rem;
        flex-wrap: wrap;
    }

    .action-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 0.875rem 1.5rem;
        font-size: 0.95rem;
        font-weight: 600;
        text-decoration: none;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        min-width: 140px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .action-btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }

    .action-btn:hover::before {
        left: 100%;
    }

    .action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }

    .action-btn:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    /* Bottone Primario (Scarica PDF) */
    .action-btn.primary {
        background: linear-gradient(135deg, var(--colore-accento), #3b82f6);
        color: white;
        border: 2px solid transparent;
    }

    .action-btn.primary:hover {
        background: linear-gradient(135deg, #3b82f6, var(--colore-accento));
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
    }

    /* Bottone Secondario (Torna al Negozio) */
    .action-btn.secondary {
        background: transparent;
        color: var(--colore-testo-principale);
        border: 2px solid var(--colore-bordi);
        background-color: var(--colore-sfondo-principale);
    }

    .action-btn.secondary:hover {
        background-color: var(--colore-bordi);
        border-color: var(--colore-testo-secondario);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    }

    /* Bottone Stampa */
    .action-btn.print {
        background: linear-gradient(135deg, #6b7280, #9ca3af);
        color: white;
        border: 2px solid transparent;
    }

    .action-btn.print:hover {
        background: linear-gradient(135deg, #9ca3af, #6b7280);
        box-shadow: 0 6px 20px rgba(107, 114, 128, 0.3);
    }

    /* Icone */
    .action-btn svg {
        flex-shrink: 0;
        transition: transform 0.3s ease;
    }

    .action-btn:hover svg {
        transform: scale(1.1);
    }

    .action-btn.primary:hover svg {
        animation: bounce 0.6s ease infinite alternate;
    }

    .action-btn.print:hover svg {
        animation: shake 0.5s ease;
    }

    /* Animazioni */
    @keyframes bounce {
        0% { transform: translateY(0); }
        100% { transform: translateY(-2px); }
    }

    @keyframes shake {
        0%, 100% { transform: rotate(0); }
        25% { transform: rotate(-5deg); }
        75% { transform: rotate(5deg); }
    }

    /* Responsive */
    @media (max-width: 640px) {
        .actions {
            flex-direction: column;
            gap: 0.75rem;
        }

        .action-btn {
            width: 100%;
            max-width: 280px;
            min-width: auto;
        }

        .contenitore-scontrino {
            margin: 1rem;
            padding: 1.5rem;
        }
    }

    .errore { color: #f87171; text-align: center; font-size: 1.1rem; }
    .messaggio-caricamento { text-align: center; font-size: 1.2rem; padding: 2rem; }

    /* --- STILI PER LA STAMPA E IL PDF --- */
    @media print {
        body * { visibility: hidden; }
        .contenitore-scontrino, .contenitore-scontrino * { visibility: visible; }
        .actions { display: none !important; } /* Nasconde i bottoni */
        .titolo-schermo { display: none !important; }

        .contenitore-scontrino {
            position: absolute; left: 0; top: 0;
            margin: 0; padding: 15px;
            width: 300px; /* Larghezza tipica (80mm) */
            border-radius: 0;
            border: none; box-shadow: none;
            background-color: white !important;
            color: black !important;
            font-family: 'Courier New', Courier, monospace !important;
            font-size: 12px;
        }
        
        h2 { font-size: 1.2em; text-transform: uppercase; margin: 0 0 10px 0; }
        .receipt-header p, .receipt-footer p { font-size: 0.9em; margin: 2px 0; color: black; }
        
        hr.dashed { border-top: 1px dashed black; margin: 10px 0; }

        .receipt-items { font-size: 1em; }
        .receipt-item, .totali p { padding: 3px 0; }
        
        .totali { font-size: 1em; }
        .complessivo, .complessivo strong { text-transform: uppercase; font-weight: bold; font-size: 1.1em; color: black; }

        a { text-decoration: none; color: black; }
    }
</style>