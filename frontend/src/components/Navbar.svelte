<script>
	import { carrello, utente } from '../stores.js'; // <-- Importiamo anche 'utente'
	import LoginModal from './LoginModal.svelte'; // <-- Importiamo il nuovo componente

	// Calcoliamo il numero totale di articoli nel carrello per il badge
	$: numeroArticoli = Object.values($carrello).reduce((acc, item) => acc + item.quantita, 0);

	// <-- NUOVO: Stato per controllare la visibilità del popup -->
	let showLoginModal = false;

	function handleLogout() {
		$utente = null; // Semplicemente, svuotiamo lo store per fare il logout
	}
</script>

{#if showLoginModal}
	<LoginModal on:close={() => (showLoginModal = false)} />
{/if}

<header>
	<nav class="navbar-content">
		<a href="/" class="site-name">MioSito</a>

		<div class="actions-container">
			<a href="/carrello" class="action-button" title="Vai al Carrello">
				{#if numeroArticoli > 0}
					<span class="badge">{numeroArticoli}</span>
				{/if}
				<svg
					xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
					stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
				>
					<circle cx="9" cy="21" r="1" />
					<circle cx="20" cy="21" r="1" />
					<path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
				</svg>
			</a>

			{#if $utente}
				<div class="user-profile">
					<span>Ciao, {$utente.username}!</span>
					<button class="action-button" title="Logout" on:click={handleLogout}>
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
					</button>
				</div>
			{:else}
				<button class="action-button" title="Accedi / Profilo Utente" on:click={() => (showLoginModal = true)}>
					<svg
						xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
						stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
					>
						<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
						<circle cx="12" cy="7" r="4" />
					</svg>
				</button>
			{/if}
		</div>
	</nav>
</header>

<style>
	/* ... (tutto lo stile precedente rimane uguale) ... */
	header { background-color: var(--colore-sfondo-secondario); padding: 1rem 2rem; border-bottom: 1px solid var(--colore-bordi); }
	.navbar-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
	.site-name { font-size: 1.5rem; font-weight: 700; font-family: 'Montserrat', sans-serif; color: var(--colore-testo); text-decoration: none; }
	.actions-container { display: flex; align-items: center; gap: 0.5rem; }
	.action-button { position: relative; display: flex; align-items: center; justify-content: center; padding: 8px; border-radius: 50%; transition: background-color 0.2s ease; background: none; border: none; cursor: pointer; color: inherit; }
	.action-button:hover { background-color: var(--colore-bordi); }
	.action-button svg { stroke: var(--colore-testo); }
	.badge { position: absolute; top: 0; right: 0; background-color: var(--colore-accento); color: var(--colore-sfondo-principale); font-weight: bold; border-radius: 50%; width: 20px; height: 20px; font-size: 12px; display: flex; align-items: center; justify-content: center; transform: translate(25%, -25%); }

	/* <-- NUOVO STILE per il profilo utente --> */
	.user-profile {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		font-weight: bold;
	}

	@media (max-width: 768px) {
		header { padding: 0.75rem 1rem; }
		.site-name { font-size: 1.25rem; }
		/* Nascondiamo il nome utente su schermi piccoli per risparmiare spazio */
		.user-profile span {
			display: none;
		}
	}
</style>