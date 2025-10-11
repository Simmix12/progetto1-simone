<script>
	import { carrello, utente } from '../../stores.js';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	const API_URL = 'http://127.0.0.1:5000';

	let datiFatturazione = {
		nome: '',
		cognome: '',
		via: '',
		citta: '',
		cap: '',
		provincia: ''
	};
	
	let isMobile = false;
	let showRiepilogo = false;
	
	onMount(async () => {
		checkMobile();
		window.addEventListener('resize', checkMobile);
		
		if ($utente) {
			try {
				const response = await fetch(`${API_URL}/api/profilo/${$utente.id}`);
				if (response.ok) {
					const profilo = await response.json();
					datiFatturazione = {
						nome: profilo.nome || '',
						cognome: profilo.cognome || '',
						via: profilo.indirizzo?.via || '',
						citta: profilo.indirizzo?.citta || '',
						cap: profilo.indirizzo?.cap || '',
						provincia: profilo.indirizzo?.provincia || ''
					};
				}
			} catch (error) {
				console.error("Errore nel caricamento dei dati di fatturazione:", error);
			}
		}
		
		return () => {
			window.removeEventListener('resize', checkMobile);
		};
	});

	function checkMobile() {
		isMobile = window.innerWidth <= 768;
	}

	const metodoPagamento = $page.url.searchParams.get('metodo');

	const carrelloItems = Object.values($carrello);
	const totaleCarrello = carrelloItems.reduce(
		(acc, item) => acc + item.prezzo_lordo * item.quantita,
		0
	);

	let cardNumber = '', expiryDate = '', cvc = '';
	let errors = {}, validatedFields = {};

	function formatCardNumber(e) {
		const value = e.target.value.replace(/\D/g, '');
		cardNumber = (value.match(/.{1,4}/g) || []).join(' ').slice(0, 19);
	}

	function formatExpiryDate(e) {
		const value = e.target.value.replace(/\D/g, '');
		expiryDate = value.length > 2 ? `${value.slice(0, 2)}/${value.slice(2, 4)}` : value;
	}

    // MODIFICATO: La funzione ora gestisce anche i campi di fatturazione
	function validateField(fieldName) {
        // Pulisce l'errore generale quando l'utente inizia a correggere
        delete errors.generale;
		delete errors[fieldName];
		delete validatedFields[fieldName];

		switch (fieldName) {
            // NUOVI controlli per la fatturazione
            case 'nome':
                if (!datiFatturazione.nome.trim()) errors.nome = 'Il nome è obbligatorio.';
                else validatedFields.nome = true;
                break;
            case 'cognome':
                if (!datiFatturazione.cognome.trim()) errors.cognome = 'Il cognome è obbligatorio.';
                else validatedFields.cognome = true;
                break;
            case 'via':
                if (!datiFatturazione.via.trim()) errors.via = 'L\'indirizzo è obbligatorio.';
                else validatedFields.via = true;
                break;
            case 'citta':
                if (!datiFatturazione.citta.trim()) errors.citta = 'La città è obbligatoria.';
                else validatedFields.citta = true;
                break;
            case 'cap':
                if (!/^\d{5}$/.test(datiFatturazione.cap.trim())) errors.cap = 'Il CAP deve avere 5 cifre.';
                else validatedFields.cap = true;
                break;
            case 'provincia':
                if (!/^[A-Z]{2}$/i.test(datiFatturazione.provincia.trim())) errors.provincia = 'Usa 2 lettere (es. MI).';
                else validatedFields.provincia = true;
                break;

            // Controlli per la carta (invariati)
			case 'cardNumber':
				if (!/^\d{16}$/.test(cardNumber.replace(/\s/g, ''))) errors.cardNumber = 'Il numero della carta deve essere di 16 cifre.';
				else validatedFields.cardNumber = true;
				break;
			case 'expiryDate':
				const expiryRegex = /^(0[1-9]|1[0-2])\/?([0-9]{2})$/;
				if (!expiryRegex.test(expiryDate)) errors.expiryDate = 'Usa il formato MM/AA.';
				else {
					const [, month, year] = expiryDate.match(expiryRegex);
					const expiry = new Date(`20${year}`, month, 1); // Controlla il primo giorno del mese di scadenza
					const today = new Date();
					// La carta è valida fino all'ultimo giorno del mese di scadenza
					if (expiry < new Date(today.getFullYear(), today.getMonth(), 1)) errors.expiryDate = 'La carta è scaduta.';
					else validatedFields.expiryDate = true;
				}
				break;
			case 'cvc':
				if (!/^\d{3,4}$/.test(cvc)) errors.cvc = 'Il CVC deve avere 3 o 4 cifre.';
				else validatedFields.cvc = true;
				break;
		}
		errors = { ...errors };
		validatedFields = { ...validatedFields };
	}

    // NUOVA funzione per validare tutti i campi in un colpo solo
    function validateAllFields() {
        const billingFields = ['nome', 'cognome', 'via', 'citta', 'cap', 'provincia'];
        billingFields.forEach(field => validateField(field));

        if (metodoPagamento === 'carta') {
            const paymentFields = ['cardNumber', 'expiryDate', 'cvc'];
            paymentFields.forEach(field => validateField(field));
        }
        
        // Ritorna true se non ci sono errori
        return Object.keys(errors).length === 0;
    }

    // MODIFICATO: Ora la funzione controlla tutto prima di procedere
	function confermaPagamento() {
        if (!validateAllFields()) {
            errors.generale = "Per favore, correggi i campi evidenziati in rosso.";
            errors = { ...errors };
            return;
        }

		console.log("Dati di pagamento e fatturazione inviati:", { ...datiFatturazione });
		goto('/scontrino');
	}

    // NUOVA funzione per gestire l'invio degli altri metodi di pagamento
    function confermaOrdineSemplice() {
        const billingFields = ['nome', 'cognome', 'via', 'citta', 'cap', 'provincia'];
        billingFields.forEach(field => validateField(field));

        if (Object.keys(errors).length > 0) {
            errors.generale = "Per favore, compila tutti i dati di fatturazione prima di continuare.";
            errors = { ...errors };
            return;
        }

        goto('/scontrino');
    }
</script>

<svelte:head>
	<title>Completa il tuo ordine</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
</svelte:head>

<h1>Completa il tuo ordine</h1>

{#if isMobile}
	<div class="mobile-riepilogo-banner" class:expanded={showRiepilogo}>
		<div class="banner-header" on:click={() => (showRiepilogo = !showRiepilogo)}>
			<div class="banner-totale">
				<span>Totale:</span>
				<strong>{totaleCarrello.toFixed(2)} €</strong>
			</div>
			<button class="toggle-banner">
				<svg
					width="20"
					height="20"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					class:rotated={showRiepilogo}
				>
					<path d="m6 9 6 6 6-6" />
				</svg>
			</button>
		</div>
		{#if showRiepilogo}
			<div class="banner-content">
				<ul class="items-list">
					{#each carrelloItems as item}
						<li class="item-row">
							<div class="item-info">
								<span class="item-name">{item.nome}</span>
								<span class="item-quantity">x{item.quantita}</span>
							</div>
							<strong class="item-price">{(item.prezzo_lordo * item.quantita).toFixed(2)} €</strong>
						</li>
					{/each}
				</ul>
			</div>
		{/if}
	</div>
{/if}

<div class="checkout-layout">
	{#if !isMobile}
		<aside class="riepilogo-ordine">
			<h2>Riepilogo Ordine</h2>
			<div class="riepilogo-content">
				{#if carrelloItems.length > 0}
					<ul class="items-list">
						{#each carrelloItems as item}
							<li class="item-row">
								<div class="item-info">
									<span class="item-name">{item.nome}</span>
									<span class="item-quantity">x{item.quantita}</span>
								</div>
								<strong class="item-price"
									>{(item.prezzo_lordo * item.quantita).toFixed(2)} €</strong
								>
							</li>
						{/each}
					</ul>
					<hr />
					<div class="totale">
						<span>Totale</span>
						<strong>{totaleCarrello.toFixed(2)} €</strong>
					</div>
				{:else}
					<p class="empty-cart">Il carrello è vuoto.</p>
				{/if}
			</div>
		</aside>
	{/if}

	<div class="colonna-principale">
		<section class="dati-fatturazione card">
			<h2>
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
					<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
					<circle cx="12" cy="7" r="4" />
				</svg>
				Dati di Fatturazione
			</h2>

			{#if errors.generale}
				<p class="error-message general-error">{errors.generale}</p>
			{/if}

			<div class="form-grid">
				<div class="form-group">
					<label for="nome">Nome</label>
					<input
						id="nome"
						type="text"
						placeholder="Mario"
						bind:value={datiFatturazione.nome}
						on:blur={() => validateField('nome')}
						class:invalid={errors.nome}
						class:valid={validatedFields.nome}
						required
					/>
					{#if errors.nome}<p class="error-message">{errors.nome}</p>{/if}
				</div>
				<div class="form-group">
					<label for="cognome">Cognome</label>
					<input
						id="cognome"
						type="text"
						placeholder="Rossi"
						bind:value={datiFatturazione.cognome}
						on:blur={() => validateField('cognome')}
						class:invalid={errors.cognome}
						class:valid={validatedFields.cognome}
						required
					/>
					{#if errors.cognome}<p class="error-message">{errors.cognome}</p>{/if}
				</div>
				<div class="form-group full-width">
					<label for="indirizzo">Indirizzo (Via e Numero Civico)</label>
					<input
						id="indirizzo"
						type="text"
						placeholder="Via Roma, 10"
						bind:value={datiFatturazione.via}
						on:blur={() => validateField('via')}
						class:invalid={errors.via}
						class:valid={validatedFields.via}
						required
					/>
					{#if errors.via}<p class="error-message">{errors.via}</p>{/if}
				</div>
				<div class="form-group">
					<label for="citta">Città</label>
					<input
						id="citta"
						type="text"
						placeholder="Milano"
						bind:value={datiFatturazione.citta}
						on:blur={() => validateField('citta')}
						class:invalid={errors.citta}
						class:valid={validatedFields.citta}
						required
					/>
					{#if errors.citta}<p class="error-message">{errors.citta}</p>{/if}
				</div>
				<div class="form-group">
					<label for="cap">CAP</label>
					<input
						id="cap"
						type="text"
						placeholder="20121"
						bind:value={datiFatturazione.cap}
						on:blur={() => validateField('cap')}
						class:invalid={errors.cap}
						class:valid={validatedFields.cap}
						required
						maxlength="5"
					/>
					{#if errors.cap}<p class="error-message">{errors.cap}</p>{/if}
				</div>
				<div class="form-group">
					<label for="provincia">Provincia</label>
					<input
						id="provincia"
						type="text"
						placeholder="MI"
						maxlength="2"
						bind:value={datiFatturazione.provincia}
						on:blur={() => validateField('provincia')}
						class:invalid={errors.provincia}
						class:valid={validatedFields.provincia}
						required
					/>
					{#if errors.provincia}<p class="error-message">{errors.provincia}</p>{/if}
				</div>
			</div>
		</section>

		<section class="dettagli-pagamento card">
			<h2>
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
					<rect x="1" y="4" width="22" height="16" rx="2" ry="2" />
					<line x1="1" y1="10" x2="23" y2="10" />
				</svg>
				Dettagli Pagamento
			</h2>

			{#if metodoPagamento === 'carta'}
				<form on:submit|preventDefault={confermaPagamento} class="payment-form" novalidate>
					<div class="form-group full-width">
						<label for="cardNumber">Numero Carta</label>
						<input
							id="cardNumber"
							type="text"
							placeholder="0000 0000 0000 0000"
							value={cardNumber}
							on:input={formatCardNumber}
							on:blur={() => validateField('cardNumber')}
							class:invalid={errors.cardNumber}
							class:valid={validatedFields.cardNumber}
							required
						/>
						{#if errors.cardNumber}
							<p class="error-message">{errors.cardNumber}</p>
						{/if}
					</div>

					<div class="form-row">
						<div class="form-group">
							<label for="expiryDate">Scadenza (MM/AA)</label>
							<input
								id="expiryDate"
								type="text"
								placeholder="MM/AA"
								value={expiryDate}
								on:input={formatExpiryDate}
								on:blur={() => validateField('expiryDate')}
								class:invalid={errors.expiryDate}
								class:valid={validatedFields.expiryDate}
								required
							/>
							{#if errors.expiryDate}
								<p class="error-message">{errors.expiryDate}</p>
							{/if}
						</div>
						<div class="form-group">
							<label for="cvc">CVC</label>
							<input
								id="cvc"
								type="text"
								placeholder="123"
								bind:value={cvc}
								maxlength="4"
								on:blur={() => validateField('cvc')}
								class:invalid={errors.cvc}
								class:valid={validatedFields.cvc}
								required
							/>
							{#if errors.cvc}
								<p class="error-message">{errors.cvc}</p>
							{/if}
						</div>
					</div>

					<button type="submit" class="pay-button">
						<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
							<path d="M20 6 9 17l-5-5" />
						</svg>
						Paga {totaleCarrello.toFixed(2)} €
					</button>
				</form>
			{:else if metodoPagamento === 'paypal'}
				<div class="payment-method-info">
					<div class="payment-icon paypal">
						<svg width="24" height="24" viewBox="0 0 24 24">
							<path
								fill="#0070BA"
								d="M20.067 7.238c-.39-.242-2.145-1.403-5.542-1.238-4.284.207-7.641 2.568-8.233 6.427-.102.663-.102 1.297.036 1.897.207.918 1.403.918 1.332-.045-.036-.352-.207-1.297.045-1.897.495-1.062 1.836-1.836 3.465-2.145 1.629-.31 3.221.103 4.307.705.39.242 2.145 1.403 5.542 1.238.207-.69.352-1.403.352-2.116 0-1.297-.352-2.503-1.104-3.426z"
							/>
						</svg>
					</div>
					<p>Verrai reindirizzato a PayPal per completare il pagamento.</p>
					<button class="pay-button paypal" on:click={confermaOrdineSemplice}>
						Continua su PayPal
					</button>
				</div>
			{:else if metodoPagamento === 'bonifico'}
				<div class="payment-method-info">
					<div class="payment-icon bank">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
							<rect x="2" y="8" width="20" height="8" rx="2" />
							<path d="M6 16v3m4-3v3m4-3v3m4-3v3M2 12h20" />
						</svg>
					</div>
					<p>Effettua il bonifico alle seguenti coordinate:</p>
					<div class="bank-details">
						<div class="bank-detail">
							<strong>IBAN:</strong>
							<span>IT00 A123 4567 8901 2345 6789 0</span>
						</div>
						<div class="bank-detail">
							<strong>Causale:</strong>
							<span>Ordine #{Math.floor(Math.random() * 10000)}</span>
						</div>
					</div>
					<button class="pay-button bank" on:click={confermaOrdineSemplice}>
						Ho effettuato il bonifico
					</button>
				</div>
			{:else}
				<div class="invalid-method">
					<p>Metodo di pagamento non valido.</p>
					<a href="/carrello" class="back-link">Torna al carrello</a>
				</div>
			{/if}
		</section>
	</div>
</div>

<style>
	/* NUOVO stile per il messaggio di errore generale */
	.error-message.general-error {
		background-color: rgba(229, 62, 62, 0.1);
		color: #e53e3e;
		padding: 0.75rem;
		border-radius: 8px;
		margin-bottom: 1.5rem;
		text-align: center;
		font-weight: 600;
		border: 1px solid rgba(229, 62, 62, 0.2);
	}

	/* Il resto degli stili è identico al file precedente */
	:global(*) {
		box-sizing: border-box;
	}

	h1 {
		text-align: center;
		color: var(--colore-accento);
		margin: 1rem 0 2rem 0;
		font-size: clamp(1.5rem, 4vw, 2.5rem);
		padding: 0 1rem;
	}

	.checkout-layout {
		display: grid;
		grid-template-columns: 1fr 2fr;
		gap: 2rem;
		max-width: 1400px;
		margin: 0 auto;
		padding: 0 1rem 2rem 1rem;
		align-items: start;
	}

	.mobile-riepilogo-banner {
		position: sticky;
		top: 0;
		background: var(--colore-sfondo-secondario);
		border-bottom: 1px solid var(--colore-bordi);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		z-index: 100;
		margin: 0 -1rem;
	}

	.mobile-riepilogo-banner.expanded {
		height: auto;
		max-height: 50vh;
		overflow-y: auto;
	}

	.banner-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem;
		background: var(--colore-accento);
		color: white;
		cursor: pointer;
	}

	.banner-totale {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 1.1rem;
		font-weight: 600;
	}

	.toggle-banner {
		background: none;
		border: none;
		color: white;
		padding: 0.25rem;
		cursor: pointer;
		border-radius: 4px;
		transition: transform 0.3s ease;
	}

	.toggle-banner:hover {
		background: rgba(255, 255, 255, 0.1);
	}

	.toggle-banner svg.rotated {
		transform: rotate(180deg);
	}

	.banner-content {
		padding: 1rem;
		background: var(--colore-sfondo-secondario);
		border-top: 1px solid var(--colore-bordi);
	}

	.card {
		background: var(--colore-sfondo-secondario);
		border: 1px solid var(--colore-bordi);
		border-radius: 12px;
		padding: 1.5rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
	}

	.card h2 {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin: 0 0 1.5rem 0;
		font-size: 1.25rem;
		color: var(--colore-testo-principale);
	}

	.riepilogo-ordine {
		position: sticky;
		top: 1rem;
		background: var(--colore-sfondo-secondario);
		border: 1px solid var(--colore-bordi);
		border-radius: 12px;
		padding: 1.5rem;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		height: fit-content;
	}

	.riepilogo-ordine h2 {
		margin: 0 0 1rem 0;
		font-size: 1.25rem;
		color: var(--colore-testo-principale);
	}

	.items-list {
		list-style: none;
		padding: 0;
		margin: 0 0 1rem 0;
		max-height: 300px;
		overflow-y: auto;
	}

	.item-row {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		padding: 0.75rem 0;
		border-bottom: 1px solid var(--colore-bordi);
	}

	.item-row:last-child {
		border-bottom: none;
	}

	.item-info {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.item-name {
		font-weight: 500;
		color: var(--colore-testo-principale);
	}

	.item-quantity {
		font-size: 0.875rem;
		color: var(--colore-testo-secondario);
	}

	.item-price {
		color: var(--colore-accento);
		font-weight: 600;
	}

	.totale {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem 0 0 0;
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--colore-testo-principale);
	}

	.empty-cart {
		text-align: center;
		color: var(--colore-testo-secondario);
		margin: 1rem 0;
	}

	.form-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
	}

	.form-group.full-width {
		grid-column: 1 / -1;
	}

	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	label {
		font-size: 0.875rem;
		font-weight: 600;
		margin-bottom: 0.5rem;
		color: var(--colore-testo-principale);
	}

	input {
		padding: 0.875rem;
		border: 2px solid var(--colore-bordi);
		border-radius: 8px;
		background: var(--colore-sfondo-principale);
		color: var(--colore-testo-principale);
		font-size: 1rem;
		transition: all 0.2s ease;
	}

	input:focus {
		outline: none;
		border-color: var(--colore-accento);
		box-shadow: 0 0 0 3px rgba(var(--colore-accento-rgb), 0.1);
	}

	input.invalid {
		border-color: #e53e3e;
		box-shadow: 0 0 0 3px rgba(229, 62, 62, 0.1);
	}

	input.valid {
		border-color: #28a745;
		box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1);
	}

	.error-message {
		color: #e53e3e;
		font-size: 0.75rem;
		margin-top: 0.25rem;
		font-weight: 500;
	}

	.payment-method-info {
		text-align: center;
		padding: 1rem 0;
	}

	.payment-icon {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 48px;
		height: 48px;
		border-radius: 8px;
		margin-bottom: 1rem;
	}

	.payment-icon.paypal {
		background: #f0f8ff;
	}

	.payment-icon.bank {
		background: #f8f9fa;
		color: var(--colore-accento);
	}

	.bank-details {
		text-align: left;
		background: var(--colore-sfondo-principale);
		padding: 1rem;
		border-radius: 8px;
		margin: 1rem 0;
	}

	.bank-detail {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		margin-bottom: 0.75rem;
	}

	.bank-detail:last-child {
		margin-bottom: 0;
	}

	.pay-button {
		width: 100%;
		padding: 1rem 1.5rem;
		font-size: 1.125rem;
		font-weight: 600;
		border: none;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		margin-top: 1rem;
	}

	.pay-button:not(:disabled) {
		background: var(--colore-accento);
		color: white;
	}

	.pay-button:disabled {
		background: var(--colore-bordi);
		color: var(--colore-testo-secondario);
		cursor: not-allowed;
	}

	.pay-button:not(:disabled):hover {
		transform: translateY(-1px);
		box-shadow: 0 4px 12px rgba(var(--colore-accento-rgb), 0.3);
	}

	.pay-button.paypal {
		background: #0070ba;
	}

	.pay-button.bank {
		background: #28a745;
	}

	.back-link {
		display: inline-block;
		padding: 1rem 1.5rem;
		background: var(--colore-bordi);
		color: var(--colore-testo-principale);
		text-decoration: none;
		border-radius: 8px;
		font-weight: 600;
		text-align: center;
		margin-top: 1rem;
		width: 100%;
	}

	.back-link:hover {
		background: var(--colore-testo-secondario);
	}

	@media (max-width: 1024px) {
		.checkout-layout {
			grid-template-columns: 1fr 1.5fr;
			gap: 1.5rem;
		}
	}

	@media (max-width: 768px) {
		.checkout-layout {
			grid-template-columns: 1fr;
			gap: 1rem;
			padding: 0 0.5rem 1rem 0.5rem;
		}

		.mobile-riepilogo-banner {
			margin: 0 -0.5rem;
		}

		.colonna-principale {
			gap: 1rem;
		}

		.card {
			padding: 1.25rem;
		}

		.form-grid {
			grid-template-columns: 1fr;
			gap: 0.875rem;
		}

		.form-row {
			grid-template-columns: 1fr;
			gap: 0.875rem;
		}

		.form-group.full-width {
			grid-column: 1;
		}

		input {
			padding: 0.75rem;
		}

		.pay-button {
			padding: 0.875rem 1.25rem;
			font-size: 1rem;
		}

		h1 {
			margin: 0.5rem 0 1rem 0;
		}
	}

	@media (max-width: 480px) {
		.checkout-layout {
			padding: 0 0.25rem 1rem 0.25rem;
		}

		.card {
			padding: 1rem;
			border-radius: 8px;
		}

		.card h2 {
			font-size: 1.125rem;
			margin-bottom: 1.25rem;
		}

		.banner-header {
			padding: 0.875rem;
		}

		.banner-totale {
			font-size: 1rem;
		}

		.items-list {
			max-height: 200px;
		}

		.item-row {
			padding: 0.5rem 0;
		}

		.totale {
			font-size: 1.125rem;
		}

		input {
			padding: 0.625rem;
			font-size: 0.875rem;
		}

		.pay-button {
			padding: 0.75rem 1rem;
			font-size: 0.875rem;
		}
	}
</style>