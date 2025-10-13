<script>
	
</script>

<div class="modal-backdrop">
	<div class="modal-content">
		<slot />
	</div>
</div>

<style>
	.modal-backdrop {
		position: fixed; /* Si fissa sulla finestra del browser */
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.7); /* Sfondo nero con 70% di opacità */
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 1000; /* Assicura che sia sopra tutto il resto */
	}

	.modal-content {
		background-color: var(--colore-sfondo-secondario);
		padding: 2.5rem;
		border-radius: 12px;
		border: 1px solid var(--colore-bordi);
		box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
		text-align: center;
		max-width: 500px;
		width: 90%; /* Occupa il 90% della larghezza su schermi piccoli */
	}
</style>