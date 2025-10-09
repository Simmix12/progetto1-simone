<script>
    import { carrello, utente } from '../stores.js';
    import LoginModal from './LoginModal.svelte';
    import { fly } from 'svelte/transition'; // Importato per le animazioni

    // Calcoliamo il numero totale di articoli nel carrello per il badge
    $: numeroArticoli = Object.values($carrello).reduce((acc, item) => acc + item.quantita, 0);

    // Stato per controllare la visibilità del popup di login
    let showLoginModal = false;

    // Stato per controllare la visibilità del menu del profilo
    let showProfileMenu = false;

    function handleLogout() {
        $utente = null;
        showProfileMenu = false; // Chiudi il menu dopo il logout
    }
</script>

{#if showLoginModal}
    <LoginModal on:close={() => (showLoginModal = false)} />
{/if}

<header class="site-header">
    <nav class="navbar-content">
        <a href="/" class="logo-container" aria-label="Buy Hub Homepage">
            <!-- NUOVO LOGO SVG -->
            <svg class="logo-svg" xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
                <line x1="3" y1="6" x2="21" y2="6"/>
                <path d="M16 10a4 4 0 0 1-8 0"/>
            </svg>
            <span class="site-name">Buy Hub</span>
        </a>

        <div class="actions-container">
            <a href="/carrello" class="action-button" title="Vai al Carrello">
                {#if numeroArticoli > 0}
                    <span class="badge">{numeroArticoli}</span>
                {/if}
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="9" cy="21" r="1" />
                    <circle cx="20" cy="21" r="1" />
                    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                </svg>
            </a>

            {#if $utente}
                <div class="profile-menu-container">
                    <button class="action-button" title="Profilo Utente" on:click={() => (showProfileMenu = !showProfileMenu)}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                            <circle cx="12" cy="7" r="4" />
                        </svg>
                    </button>

                    {#if showProfileMenu}
                        <div class="profile-dropdown" transition:fly={{ y: -10, duration: 200 }}>
                            <div class="dropdown-header">
                                Ciao, <strong>{$utente.username}</strong>!
                            </div>
                            <ul>
                                <li>
                                    <a href="/profilo">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                                        <span>Gestisci Dati</span>
                                    </a>
                                </li>
                                <li>
                                    <a href="/reimposta-password">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                                        <span>Reimposta Password</span>
                                    </a>
                                </li>
                                <li>
                                    <button on:click={handleLogout}>
                                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                                        <span>Logout</span>
                                    </button>
                                </li>
                            </ul>
                        </div>
                    {/if}
                </div>
            {:else}
                <button class="action-button" title="Accedi" on:click={() => (showLoginModal = true)}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                        <circle cx="12" cy="7" r="4" />
                    </svg>
                </button>
            {/if}
        </div>
    </nav>
</header>

<style>
    .site-header {
        background-color: var(--colore-sfondo-secondario);
        padding: 1rem 2rem;
        border-bottom: 1px solid var(--colore-bordi);
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    .navbar-content {
        max-width: 1400px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .logo-container {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        text-decoration: none;
    }
    .logo-svg {
        color: var(--colore-accento);
    }
    .site-name {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--colore-testo);
    }

    .actions-container {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .action-button {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 10px;
        border-radius: 50%;
        transition: background-color 0.2s ease, transform 0.2s ease;
        background: none;
        border: none;
        cursor: pointer;
        color: var(--colore-testo-secondario);
    }
    .action-button:hover {
        background-color: var(--colore-bordi);
        color: var(--colore-testo);
        transform: scale(1.1);
    }
    .action-button svg {
        stroke: currentColor;
    }
    .badge {
        position: absolute;
        top: 0;
        right: 0;
        background-color: var(--colore-accento);
        color: var(--colore-sfondo-secondario);
        font-weight: bold;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        font-size: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        transform: translate(30%, -30%);
        border: 2px solid var(--colore-sfondo-secondario);
    }

    /* --- STILI MENU A TENDINA MIGLIORATI --- */
    .profile-menu-container {
        position: relative;
    }

    .profile-dropdown {
        position: absolute;
        top: calc(100% + 12px);
        right: 0;
        min-width: 240px;
        background-color: var(--colore-sfondo-secondario);
        border: 1px solid var(--colore-bordi);
        border-radius: 8px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        z-index: 100;
        overflow: hidden;
    }

    .profile-dropdown .dropdown-header {
        padding: 1rem;
        border-bottom: 1px solid var(--colore-bordi);
        font-size: 0.9rem;
        color: var(--colore-testo-secondario);
    }
    .profile-dropdown .dropdown-header strong {
        color: var(--colore-testo);
    }

    .profile-dropdown ul {
        list-style: none;
        margin: 0;
        padding: 0.5rem;
    }
    
    .profile-dropdown ul li a,
    .profile-dropdown ul li button {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        width: 100%;
        text-align: left;
        padding: 0.75rem 1rem;
        background: none;
        border: none;
        color: var(--colore-testo);
        font-size: 1rem;
        font-weight: 500;
        cursor: pointer;
        text-decoration: none;
        border-radius: 6px;
        transition: background-color 0.2s ease, color 0.2s ease;
    }

    .profile-dropdown ul li a:hover,
    .profile-dropdown ul li button:hover {
        background-color: var(--colore-accento);
        color: white;
    }
    
    .profile-dropdown ul li button svg {
        stroke: currentColor;
    }

    .profile-dropdown ul li:last-child button {
        color: #f87171;
    }
    
    .profile-dropdown ul li:last-child button:hover {
        background-color: #ef4444;
        color: white;
    }

    /* =======================================================
       NUOVA REGOLA PER NASCONDERE LA NAVBAR DURANTE LA STAMPA
       =======================================================
    */
    @media print {
        .site-header {
            display: none !important;
        }
    }
</style>