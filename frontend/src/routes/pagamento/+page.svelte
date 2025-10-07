<script>
	import { carrello } from '../../stores.js';
	import { page } from '$app/stores'; // Per leggere i parametri URL
	import { goto } from '$app/navigation';

	// Leggiamo il metodo di pagamento dall'URL
	const metodoPagamento = $page.url.searchParams.get('metodo');

	const carrelloItems = Object.values($carrello);
	const totaleCarrello = carrelloItems.reduce(
        (acc, item) => acc + item.prezzo_lordo * item.quantita, 0
    );

	function confermaPagamento() {
		// Qui, in un'app reale, invieresti i dati del form a un server di pagamento.
		// Per ora, simuliamo il successo e andiamo alla pagina dello scontrino.
		console.log("Dati di pagamento inviati con successo.");
		goto('/scontrino');
	}
</script>

<svelte:head>
	<title>Finalizza Pagamento</title>
</svelte:head>

<h1>Finalizza il tuo ordine</h1>

<div class="checkout-layout">
	<section class="riepilogo-ordine">
		<h2>Riepilogo Ordine</h2>
		{#if carrelloItems.length > 0}
			<ul>
				{#each carrelloItems as item}
					<li>
						<span>{item.nome} (x{item.quantita})</span>
						<strong>{(item.prezzo_lordo * item.quantita).toFixed(2)} €</strong>
					</li>
				{/each}
			</ul>
			<hr />
			<div class="totale">
				<span>Totale</span>
				<strong>{totaleCarrello.toFixed(2)} €</strong>
			</div>
		{:else}
			<p>Il carrello è vuoto.</p>
		{/if}
	</section>

	<section class="dettagli-pagamento">
		<h2>Dettagli Pagamento</h2>
		
		{#if metodoPagamento === 'carta'}
			<form on:submit|preventDefault={confermaPagamento}>
				<label>
					Numero Carta
					<input type="text" placeholder="0000 0000 0000 0000" required />
				</label>
				<div class="form-row">
					<label>
						Scadenza (MM/AA)
						<input type="text" placeholder="MM/AA" required />
					</label>
					<label>
						CVC
						<input type="text" placeholder="123" required />
					</label>
				</div>
				<button type="submit">Paga {totaleCarrello.toFixed(2)} €</button>
			</form>
		{:else if metodoPagamento === 'paypal'}
			<div class="paypal-info">
				<p>Verrai reindirizzato a PayPal per completare il pagamento in sicurezza.</p>
				<button on:click={confermaPagamento}>Continua su PayPal</button>
			</div>
		{:else if metodoPagamento === 'bonifico'}
			<div class="bonifico-info">
				<p>Effettua il bonifico alle seguenti coordinate:</p>
				<p><strong>IBAN:</strong> IT00 A123 4567 8901 2345 6789 0</p>
				<p><strong>Causale:</strong> Ordine #{Math.floor(Math.random() * 10000)}</p>
				<button on:click={confermaPagamento}>Ho effettuato il bonifico</button>
			</div>
		{:else}
			<p>Metodo di pagamento non valido. <a href="/carrello">Torna indietro</a> e scegline uno.</p>
		{/if}
	</section>
</div>

<style>
	.checkout-layout {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
		max-width: 1200px;
		margin: 2rem auto;
	}
	section {
		background-color: var(--colore-sfondo-secondario);
		padding: 2rem;
		border: 1px solid var(--colore-bordi);
		border-radius: 8px;
	}
	ul { list-style: none; padding: 0; }
	li, .totale { display: flex; justify-content: space-between; padding: 0.75rem 0; }
	.totale { font-size: 1.2rem; }
	
	/* Stili per il form */
	form { display: flex; flex-direction: column; gap: 1rem; }
	.form-row { display: flex; gap: 1rem; }
	.form-row > * { flex: 1; }
	label { display: flex; flex-direction: column; font-size: 0.9rem; }
	input { padding: 0.75rem; border-radius: 5px; border: 1px solid var(--colore-bordi); background-color: var(--colore-sfondo-principale); color: var(--colore-testo); margin-top: 0.25rem; }
	button { width: 100%; margin-top: 1rem; padding: 1rem; font-size: 1.2rem; }

	@media (max-width: 900px) {
		.checkout-layout {
			grid-template-columns: 1fr;
		}
	}
</style>
ciao