<script>
// ✅ CORRECT PATH
    import { utente } from '../../stores.js';    
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';

    // URL dell'API backend
    const API_URL = 'http://127.0.0.1:5000';

    // Dati del form, separati per chiarezza
    let passwordData = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    };

    let feedbackMessage = ''; // Per messaggi di successo o errore
    let isLoading = false; // Per gestire lo stato di caricamento

    // Controlla se l'utente è loggato al caricamento del componente
    onMount(() => {
        if (!$utente) {
            goto('/'); // Se non c'è utente, torna alla home
        }
    });

    // Funzione per gestire l'aggiornamento della password
    async function handleChangePassword() {
        if (!$utente) return;

        // Validazione di base sul frontend
        if (passwordData.newPassword !== passwordData.confirmPassword) {
            feedbackMessage = 'Errore: Le nuove password non coincidono.';
            return;
        }
        if (passwordData.newPassword.length < 6) {
            feedbackMessage = 'Errore: La nuova password deve essere di almeno 6 caratteri.';
            return;
        }

        isLoading = true;
        feedbackMessage = 'Aggiornamento in corso...';

        try {
            const response = await fetch(`${API_URL}/api/profilo/${$utente.id}/change-password`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    current_password: passwordData.currentPassword,
                    new_password: passwordData.newPassword
                })
            });

            const result = await response.json();

            if (!response.ok) {
                // Se la risposta non è OK, lancia un errore con il messaggio del backend
                throw new Error(result.errore || 'Si è verificato un errore sconosciuto.');
            }

            feedbackMessage = 'Password aggiornata con successo!';
            // Svuota i campi dopo il successo
            passwordData = { currentPassword: '', newPassword: '', confirmPassword: '' };

        } catch (e) {
            // Mostra il messaggio di errore proveniente dal backend
            feedbackMessage = `Errore: ${e.message}`;
        } finally {
            isLoading = false;
        }
    }
</script>

<svelte:head>
    <title>Reimposta Password</title>
</svelte:head>

<div class="password-reset-container">
    <h1>Reimposta la Tua Password</h1>
    <p>Per la tua sicurezza, inserisci la tua password attuale prima di sceglierne una nuova.</p>

    <form class="password-reset-form" on:submit|preventDefault={handleChangePassword}>
        <fieldset>
            <legend>Cambia Password</legend>
            
            <label>
                Password Attuale
                <input type="password" bind:value={passwordData.currentPassword} placeholder="••••••••" required />
            </label>
            
            <label>
                Nuova Password
                <input type="password" bind:value={passwordData.newPassword} placeholder="Minimo 6 caratteri" required />
            </label>

            <label>
                Conferma Nuova Password
                <input type="password" bind:value={passwordData.confirmPassword} placeholder="Ripeti la nuova password" required />
            </label>
        </fieldset>

        {#if feedbackMessage}
            <p class="feedback">{feedbackMessage}</p>
        {/if}

        <button type="submit" disabled={isLoading}>
            {isLoading ? 'Salvataggio...' : 'Salva Nuova Password'}
        </button>
    </form>
</div>

<style>
    .password-reset-container { max-width: 600px; margin: 2rem auto; padding: 2rem; background-color: var(--colore-sfondo-secondario); border: 1px solid var(--colore-bordi); border-radius: 8px; }
    h1 { text-align: center; color: var(--colore-accento); margin-bottom: 1rem; }
    p { text-align: center; margin-bottom: 2rem; font-size: 0.95rem; }
    .password-reset-form { display: flex; flex-direction: column; gap: 1.5rem; }
    
    fieldset { border: 1px solid var(--colore-bordi); border-radius: 6px; padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem;}
    legend { padding: 0 0.5rem; font-weight: bold; color: var(--colore-accento); }
    
    label { display: flex; flex-direction: column; font-weight: bold; font-size: 0.9rem; }
    input { margin-top: 0.5rem; padding: 0.75rem; font-size: 1rem; border-radius: 5px; border: 1px solid var(--colore-bordi); }
    
    button { padding: 0.8rem; font-size: 1.1rem; font-weight: bold; cursor: pointer; border-radius: 5px; background-color: var(--colore-accento); color: var(--colore-sfondo-principale); border: none; }
    button:disabled { background-color: #ccc; cursor: not-allowed; }

    .feedback { text-align: center; font-weight: bold; padding: 0.5rem; border-radius: 4px; }
</style>