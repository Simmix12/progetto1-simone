<script>
    import Navbar from '../components/Navbar.svelte';
    import ChatWidget from '../components/ChatWidget.svelte';
    import '../app.css';

    let showChat = false;
</script>

{#if showChat}
    <ChatWidget on:close={() => (showChat = false)} />
{/if}

{#if !showChat}
    <button class="chat-toggle-btn" on:click={() => (showChat = true)} aria-label="Apri chat">
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
    </button>
{/if}

<div class="app-container">
    <Navbar />

    <main>
        <slot />
    </main>

    <footer class="site-footer">
        <div class="footer-content">
            <div class="footer-left">
                <h3>Servizio Clienti</h3>
                <div class="contact-info">
                    <p><strong>Telefono:</strong> <a href="tel:+393274780833">+39 327 478 0833</a></p>
                    <p><strong>Orari:</strong> Lun-Ven, 9:00 - 18:00</p>
                    <p><strong>Email:</strong> <a href="mailto:supporto@miosito.it">otiepan.noce@gmail.com</a></p>
                </div>
            </div>
        </div>
    </footer>
</div>

<style>
    .app-container {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }

    main {
        flex-grow: 1;
        padding: 1.5rem;
    }
    
    .site-footer {
        margin-top: auto;
        background-color: var(--colore-sfondo-secondario);
        color: var(--colore-testo);
        padding: 2rem 1rem;
        border-top: 1px solid var(--colore-bordi);
    }

    .footer-content {
        max-width: 1200px;
        /* MODIFICA: Rimosso 'auto' per allineare il blocco più a sinistra */
        margin: 0;
        display: flex;
        justify-content: flex-start;
        align-items: center;
        text-align: left;
    }

    .footer-content h3 {
        margin: 0 0 1rem 0;
        font-size: 1.2rem;
        color: var(--colore-accento);
    }

    .contact-info p {
        margin: 0.5rem 0;
        line-height: 1.5;
    }

    .contact-info a {
        color: var(--colore-testo);
        text-decoration: none;
        transition: color 0.2s ease;
    }

    .contact-info a:hover {
        color: var(--colore-accento);
        text-decoration: underline;
    }

    .chat-toggle-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1999;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background-color: var(--colore-accento);
        color: var(--colore-sfondo-principale);
        display: flex;
        justify-content: center;
        align-items: center;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .chat-toggle-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 16px rgba(0,0,0,0.25);
    }

    @media (max-width: 768px) {
        main {
            padding: 1rem;
        }
        .footer-content {
            flex-direction: column;
            gap: 1.5rem;
            align-items: flex-start;
        }
        .site-footer {
            padding: 1.5rem 1rem;
        }
    }
</style>

