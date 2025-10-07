<script>
	import { carrello } from '../../stores.js';
	import { goto } from '$app/navigation';
	import MetodoPagamento from '../../components/MetodoPagamento.svelte';
	// Importiamo il nostro nuovo componente Modal
	import Modal from '../../components/Modal.svelte';

	let carrelloItems = Object.values($carrello);
	let metodoPagamentoScelto = '';

	// Variabile reattiva per controllare se il carrello è vuoto
	$: isCartEmpty = carrelloItems.length === 0;

	$: totaleCarrello = carrelloItems.reduce(
        (acc, item) => acc + item.prezzo_lordo * item.quantita, 0
    );

	function procediAlPagamento() {
		if (!metodoPagamentoScelto) return;
		goto(`/pagamento?metodo=${metodoPagamentoScelto}`);
	}

    function rimuovi(prodottoId) {
        delete $carrello[prodottoId];
        $carrello = $carrello;
		// Aggiorniamo la nostra variabile locale
		carrelloItems = Object.values($carrello);
    }
</script>

<svelte:head>
	<title>Carrello</title>
</svelte:head>

{#if isCartEmpty}
	<Modal>
		<h2>Il tuo carrello è vuoto!</h2>
		<p>Sembra che tu non abbia ancora aggiunto nessun prodotto.</p>
		<a href="/" class="torna-negozio-btn">Torna al Negozio</a>
	</Modal>
{/if}

<h1>Il Tuo Carrello</h1>

<div class:hidden={isCartEmpty}>
	<div class="riepilogo-carrello">
		<ul>
			{#each carrelloItems as item (item.id)}
				<li>
					<span class="nome">{item.nome} (x{item.quantita})</span>
					<span class="prezzo">{(item.prezzo_lordo * item.quantita).toFixed(2)} €</span>
					<button class="rimuovi" on:click={() => rimuovi(item.id)}>×</button>
				</li>
			{/each}
		</ul>
		<hr/>
		<div class="totale">
			<span>Totale Provvisorio</span>
			<strong>{totaleCarrello.toFixed(2)} €</strong>
		</div>

		<MetodoPagamento 
			on:selectionChange={(event) => (metodoPagamentoScelto = event.detail)}
		/>

		<button 
			class="pagamento" 
			on:click={procediAlPagamento} 
			disabled={!metodoPagamentoScelto}
		>
			Vai al Pagamento
		</button>
	</div>
</div>


<style>
	/* Stile aggiunto per il titolo */
	h1 {
		text-align: center;
		font-size: 2.5rem;
		color: var(--colore-accento);
		margin-bottom: 2rem;
		text-shadow: 0 2px 15px rgba(0, 0, 0, 0.2);
	}

	.riepilogo-carrello { max-width: 800px; margin: 2rem auto; padding: 2rem; background-color: var(--colore-sfondo-secondario); border: 1px solid var(--colore-bordi); border-radius: 8px; }
	ul { list-style: none; padding: 0; }
	li { display: flex; align-items: center; padding: 1rem 0; border-bottom: 1px solid var(--colore-bordi); }
	li:last-child { border-bottom: none; }
    .nome { flex-grow: 1; }
    .prezzo { font-weight: bold; margin: 0 1rem; }
    .rimuovi { background: none; border: none; color: #e53e3e; font-size: 1.5rem; cursor: pointer;}
	.totale { display: flex; justify-content: space-between; font-size: 1.2rem; margin-top: 1rem; }
	.pagamento { width: 100%; margin-top: 2rem; padding: 1rem; font-size: 1.2rem; transition: background-color 0.2s ease, opacity 0.2s ease; }
	.pagamento:disabled { opacity: 0.5; cursor: not-allowed; }
	.torna-negozio-btn { display: inline-block; margin-top: 1.5rem; padding: 0.75rem 1.5rem; background-color: var(--colore-accento); color: var(--colore-sfondo-principale); font-weight: bold; text-decoration: none; border-radius: 8px; transition: opacity 0.2s ease; }
	.torna-negozio-btn:hover { opacity: 0.85; }
	.hidden { display: none; }
</style>