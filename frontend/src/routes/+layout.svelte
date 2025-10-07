<script>
	import Navbar from '../components/Navbar.svelte';
	// Importiamo gli stili globali una sola volta qui
	import '../app.css';
</script>

<div class="app-container">
	<Navbar />

	<main>
		<slot />
	</main>
</div>

<style>
	.app-container {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	main {
		flex-grow: 1;
        padding: 1.5rem; /* Aggiungiamo un po' di padding all'area principale */
	}

    @media (max-width: 768px) {
        main {
            padding: 1rem;
        }
    }
</style>