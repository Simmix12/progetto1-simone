<script>
	import { createEventDispatcher } from 'svelte';
	import { utente } from '../stores.js';// Store Svelte per lo stato globale dell'utente
	import Modal from './Modal.svelte';

	const dispatch = createEventDispatcher();
	const API_URL = 'http://127.0.0.1:5000';//URL base dell'API backend.



	// Stati condivisi per entrambe le form
	let username = '';
	let password = '';
	let errore = '';
	let isLoading = false;//Flag booleano che indica se è in corso una richiesta API.
    let isRegistering = false; //  Stato per passare tra Accedi (false) e Registrati (true)

	// Stati aggiuntivi solo per la registrazione
    let email = '';
    let confirmPassword = '';

	// Funzione per il Login (esistente)
	async function handleLogin() {
		isLoading = true;
		errore = ''; //reset di aventuali errori precedenti
		try {
			const response = await fetch(`${API_URL}/api/login`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password })
			});

			const data = await response.json(); //effettua una chiamata all'endpoint di login con le credenziali

			if (!response.ok) {
				throw new Error(data.errore || 'Credenziali non valide. Riprova.');
			}

			// Successo: aggiorna store e chiudi
			$utente = data.utente; // se è avvenuto aggiorna(store) con i dati dell' utente
			dispatch('close');
		} catch (e) {
			errore = e.message;
		} finally {
			isLoading = false;
		}
	}

    // NUOVO: Funzione per la Registrazione
    async function handleRegister() { //controlla che la pass e la conferma pass coincidano
        if (password !== confirmPassword) {
            errore = 'Le password non corrispondono.';
            return;
        }

        isLoading = true;
        errore = '';

        try {//chiamata allì'endpoint di registrazione con tutti i dati richiesti   
            const response = await fetch(`${API_URL}/api/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.json();

            if (!response.ok) {
                // Gestione errori di validazione dal backend (es. utente già esistente)
                throw new Error(data.errore || 'Errore durante la registrazione.');
            }

            // Successo: l'utente viene registrato E loggato
            $utente = data.utente;//backend restituisce già l'utente loggato    
            dispatch('close');
        } catch (e) {
            errore = e.message;
        } finally {
            isLoading = false;
        }
    }

    // Funzione per resettare gli stati quando si cambia form
    function toggleForm(isReg) {
        isRegistering = isReg;
        // Resetta i campi e gli errori per non confondere l'utente
        username = '';
        password = '';
        email = '';
        confirmPassword = '';
        errore = '';
    }
</script>

<Modal>
	<div class="login-container">
        <div class="tabs">
            <button
                class:active={!isRegistering}
                on:click={() => toggleForm(false)}
            >
                Accedi
            </button>
            <button
                class:active={isRegistering}
                on:click={() => toggleForm(true)}
            >
                Registrati
            </button>
        </div>

		<h2>{isRegistering ? 'Registrati' : 'Accedi'}</h2>

        {#if isRegistering}
            <form on:submit|preventDefault={handleRegister}>
                <label>
                    Username
                    <input type="text" bind:value={username} required placeholder="mario.rossi" />
                </label>
                <label>
                    Email
                    <input type="email" bind:value={email} required placeholder="mario.rossi@mail.it" />
                </label>
                <label>
                    Password
                    <input type="password" bind:value={password} required placeholder="••••••••" />
                </label>
                <label>
                    Conferma Password
                    <input type="password" bind:value={confirmPassword} required placeholder="••••••••" />
                </label>

                {#if errore}
                    <p class="errore">{errore}</p>
                {/if}

                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Registrazione in corso...' : 'Registrati'}
                </button>
            </form>

        {:else}
            <form on:submit|preventDefault={handleLogin}>
                <label>
                    Username
                    <input type="text" bind:value={username} required placeholder="mario.rossi" />
                </label>
                <label>
                    Password
                    <input type="password" bind:value={password} required placeholder="••••••••" />
                </label>

                {#if errore}
                    <p class="errore">{errore}</p>
                {/if}

                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Accesso in corso...' : 'Accedi'}
                </button>
            </form>
        {/if}

		<button class="close-btn" on:click={() => dispatch('close')}>Chiudi</button>
	</div>
</Modal>

<style>
	.login-container {
		text-align: center;
		color: var(--colore-testo);
	}
    /* NUOVO STILE: Tab per Accedi/Registrati */
    .tabs {
        display: flex;
        justify-content: center;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid var(--colore-bordi);
    }
    .tabs button {
        background: none;
        border: none;
        padding: 0.75rem 1.5rem;
        cursor: pointer;
        font-size: 1.1rem;
        font-weight: 500;
        color: var(--colore-testo);
        opacity: 0.6;
        transition: opacity 0.2s, border-bottom 0.2s;
        border-bottom: 3px solid transparent;
        margin-bottom: -1px; /* Per allineare meglio col bordo sotto */
    }
    .tabs button.active {
        opacity: 1;
        font-weight: bold;
        border-bottom-color: var(--colore-accento); /* Colore primario */
    }

	form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		margin-top: 1.5rem;
	}
	label {
		text-align: left;
		font-weight: bold;
	}
	input {
		width: 100%;
		padding: 0.75rem;
		margin-top: 0.25rem;
		border-radius: 5px;
		border: 1px solid var(--colore-bordi);
	}
	.errore {
		color: #e53e3e;
		background-color: rgba(229, 62, 62, 0.1);
		padding: 0.5rem;
		border-radius: 5px;
		font-size: 0.9rem;
	}
	.close-btn {
		margin-top: 1rem;
		background: none;
		border: none;
		color: var(--colore-testo);
		text-decoration: underline;
		cursor: pointer;
	}
</style>