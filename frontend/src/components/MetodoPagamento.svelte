<script>
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	// Opzioni di pagamento che vogliamo mostrare
	const opzioni = [
		{ id: 'carta', nome: 'Carta di Credito' },
		{ id: 'paypal', nome: 'PayPal' },
		{ id: 'bonifico', nome: 'Bonifico Bancario' }
	];

	// Questa variabile terrà traccia del metodo selezionato
	let metodoSelezionato = '';

	// Quando 'metodoSelezionato' cambia, questa funzione reattiva ($:)
	// invia un evento al componente genitore (la pagina del carrello)
	// comunicandogli la nuova selezione.
	$: dispatch('selectionChange', metodoSelezionato);
</script>

<div class="payment-options">
	<h3>Scegli un metodo di pagamento</h3>
	<ul>
		{#each opzioni as opzione (opzione.id)}
			<li class:selected={metodoSelezionato === opzione.id}>
				<label>
					<input type="radio" name="payment-method" value={opzione.id} bind:group={metodoSelezionato} />
					<span>{opzione.nome}</span>
				</label>
			</li>
		{/each}
	</ul>
</div>

<style>
	.payment-options {
		margin-top: 2.5rem;
	}
	ul {
		list-style: none;
		padding: 0;
		margin-top: 1rem;
		display: grid;
		gap: 0.75rem;
	}
	li {
		border: 1px solid var(--colore-bordi);
		border-radius: 8px;
		transition: border-color 0.2s ease, box-shadow 0.2s ease;
	}
	li.selected {
		/* Evidenzia l'opzione selezionata con il colore d'accento */
		border-color: var(--colore-accento);
		box-shadow: 0 0 5px hsla(var(--colore-accento), 0.5);
	}
	label {
		display: flex;
		align-items: center;
		padding: 1rem;
		cursor: pointer;
		width: 100%;
	}
	input[type='radio'] {
		margin-right: 1rem;
		/* Stili moderni per i radio button */
		accent-color: var(--colore-accento);
	}
</style>