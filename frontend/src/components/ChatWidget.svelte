<script>
    import { createEventDispatcher, onMount } from 'svelte';//onMount  ti permette di eseguire il codice appena viene crato il componente   
    import { fly } from 'svelte/transition';

    const dispatch = createEventDispatcher(); //dispatcher è un metodo per permettere ad un componente figlio di comunicare con un genitorie
    const API_URL = 'http://127.0.0.1:5000'; //Crea un'istanza del dispatcher di eventi per comunicare con i componenti padre.



    // Stato della chat
    let messages = [
        { id: 1, text: 'Ciao! Sono il tuo assistente virtuale. Come posso aiutarti oggi?', sender: 'ai' }
    ];
    let userInput = '';
    let isLoading = false;
    let messagesContainer;

    // Funzione per far scrollare la chat in fondo
    function scrollToBottom() {
        setTimeout(() => {
            if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight; //Imposta la posizione di scroll verticale
            }
        }, 50);
    }

    onMount(scrollToBottom);

    async function handleSend() {
        if (!userInput.trim()) return;//Controlla che l'input non sia vuoto o solo spazi bianchi.



        const currentInput = userInput; //salva l'imput corrente prima di resettarlo
        messages = [...messages, { id: Date.now(), text: currentInput, sender: 'user' }];//Aggiorna l'array dei messaggi
        userInput = '';//messaggio utente
        scrollToBottom();
        isLoading = true;

        try {
            const response = await fetch(`${API_URL}/api/chat`, {//chiamata ai
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },//specifica il fatto che srtiamo inviando in json
                body: JSON.stringify({ message: currentInput }),//converte in stringa json
            });

            if (!response.ok) {
                throw new Error('Il server ha risposto con un errore.');
            }

            const data = await response.json();
            messages = [...messages, { id: Date.now() + 1, text: data.reply, sender: 'ai' }];
        } catch (error) {
            console.error("Errore nella chiamata API della chat:", error);
            messages = [...messages, { id: Date.now() + 1, text: "Spiacente, non riesco a connettermi all'assistente in questo momento.", sender: 'ai' }];
        } finally {
            isLoading = false;
            scrollToBottom();
        }
    }
</script>

<div class="chat-overlay" transition:fly={{ y: 20, duration: 300 }}>
    <div class="chat-widget">
        <header class="chat-header">
            <h3>Assistente AI</h3>
            <button class="close-btn" on:click={() => dispatch('close')}>×</button>
        </header>

        <div class="chat-messages" bind:this={messagesContainer}>
            {#each messages as message (message.id)}
                <div class="message" class:user={message.sender === 'user'} class:ai={message.sender === 'ai'}>
                    {message.text}
                </div>
            {/each}
            {#if isLoading}
                <div class="message ai typing">
                    <span>.</span><span>.</span><span>.</span>
                </div>
            {/if}
        </div>

        <form class="chat-input-form" on:submit|preventDefault={handleSend}>
            <input type="text" bind:value={userInput} placeholder="Scrivi un messaggio..." autocomplete="off" disabled={isLoading} />
            <button type="submit" disabled={isLoading}>Invia</button>
        </form>
    </div>
</div>

<style>
    .chat-overlay {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999; /* Valore molto alto per essere sicuro che sia in primo piano */
    }
    .chat-widget {
        width: 350px;
        height: 500px;
        background-color: var(--colore-sfondo-principale);
        border: 1px solid var(--colore-bordi);
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    .chat-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem;
        background-color: var(--colore-sfondo-secondario);
        border-bottom: 1px solid var(--colore-bordi);
    }
    .chat-header h3 {
        margin: 0;
        font-size: 1rem;
    }
    .close-btn {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: var(--colore-testo);
    }
    .chat-messages {
        flex-grow: 1;
        padding: 1rem;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    .message {
        padding: 0.6rem 1rem;
        border-radius: 18px;
        max-width: 80%;
        line-height: 1.4;
    }
    .message.ai {
        background-color: var(--colore-bordi);
        color: var(--colore-testo);
        align-self: flex-start;
        border-bottom-left-radius: 4px;
    }
    .message.user {
        background-color: var(--colore-accento);
        color: var(--colore-sfondo-principale);
        align-self: flex-end;
        border-bottom-right-radius: 4px;
    }
    .chat-input-form {
        display: flex;
        border-top: 1px solid var(--colore-bordi);
        padding: 0.5rem;
    }
    .chat-input-form input {
        flex-grow: 1;
        border: none;
        padding: 0.75rem;
        background: none;
        color: var(--colore-testo);
    }
    .chat-input-form input:focus {
        outline: none;
    }
    .chat-input-form button {
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .typing span { display: inline-block; animation: blink 1.4s infinite both; }
    .typing span:nth-child(2) { animation-delay: 0.2s; }
    .typing span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes blink { 0% { opacity: 0.2; } 20% { opacity: 1; } 100% { opacity: 0.2; } }
</style>