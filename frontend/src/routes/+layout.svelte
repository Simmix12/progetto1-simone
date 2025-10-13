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
            <div class="footer-section">
                <h3>Servizio Clienti</h3>
                <div class="contact-info">
                    <p><strong>Telefono:</strong> <a href="tel:+393274780833">+39 327 478 0833</a></p>
                    <p><strong>Orari:</strong> Lun-Ven, 9:00 - 18:00</p>
                    <p><strong>Email:</strong> <a href="mailto:supporto@miosito.it">otiepan.noce@gmail.com</a></p>
                </div>
            </div>

            <div class="footer-section">
                <h3>Dove Siamo</h3>
                <div class="address-info">
                    <p>Via Repubblica, 10</p>
                    <p>25121 Brescia (BS)</p>
                    <p>Italia</p>
                </div>
            </div>
            <div class="footer-section">
                <h3>Pagamenti Sicuri</h3>
                <div class="payment-methods">
                    <div class="payment-icons">
                        <span class="payment-icon">💳</span>
                        <span class="payment-icon">🔒</span>
                        <span class="payment-icon">📱</span>
                    </div>
                    <p>Pagamenti 100% sicuri e crittografati</p>
                </div>
            </div>

            <div class="footer-section">
                <h3>Seguici</h3>
                <div class="social-links">
                    <a href="#" aria-label="Facebook" class="social-link">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                        </svg>
                    </a>
                    <a href="#" aria-label="Instagram" class="social-link">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                        </svg>
                    </a>
                </div>
            </div>
        </div>

        <div class="footer-bottom">
            <div class="footer-bottom-content">
                <p>&copy; 2025 Buy Hub. Tutti i diritti riservati.</p>
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
        padding: 2rem 1rem 0;
        border-top: 1px solid var(--colore-bordi);
    }

    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        padding-bottom: 2rem;
        text-align: center;
    }

    .footer-section h3 {
        margin: 0 0 1rem 0;
        font-size: 1.2rem;
        color: var(--colore-accento);
    }

    .contact-info p,
    .address-info p { /* <-- REGOLA AGGIUNTA QUI PER COERENZA */
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

    .payment-methods {
        text-align: center;
    }

    .payment-icons {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .payment-icon {
        font-size: 1.5rem;
    }

    .social-links {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .social-link {
        color: var(--colore-testo);
        transition: color 0.2s ease;
        padding: 0.5rem;
        border-radius: 50%;
        background-color: var(--colore-bordi);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .social-link:hover {
        color: var(--colore-accento);
        background-color: var(--colore-primario);
    }

    .footer-bottom {
        border-top: 1px solid var(--colore-bordi);
        padding: 1rem 0;
        background-color: var(--colore-sfondo-principale);
    }

    .footer-bottom-content {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        gap: 2rem;
        text-align: center;
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
            grid-template-columns: 1fr;
            gap: 1.5rem;
            text-align: center;
        }

        .footer-bottom-content {
            flex-direction: column;
            gap: 1rem;
        }

        .site-footer {
            padding: 1.5rem 1rem 0;
        }
    }

    @media (max-width: 480px) {
        .payment-icons {
            justify-content: center;
        }
    }

    /* =======================================================
        NUOVA REGOLA PER NASCONDERE IL FOOTER DURANTE LA STAMPA
        =======================================================
    */
    @media print {
        .site-footer {
            display: none !important;
        }
    }
</style>