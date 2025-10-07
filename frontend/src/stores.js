import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// Store per il carrello (che già usi)
const storedCart = browser ? localStorage.getItem('carrello') : null;
export const carrello = writable(JSON.parse(storedCart) || {});
if (browser) {
	carrello.subscribe((value) => localStorage.setItem('carrello', JSON.stringify(value)));
}

// <-- NUOVO: Store per l'utente -->
// Cerchiamo l'utente nel sessionStorage. Se non c'è, il valore è null.
const storedUser = browser ? sessionStorage.getItem('utente') : null;
export const utente = writable(JSON.parse(storedUser) || null);

// Ogni volta che lo store 'utente' cambia, lo salviamo nel sessionStorage.
if (browser) {
	utente.subscribe((value) => {
		if (value) {
			sessionStorage.setItem('utente', JSON.stringify(value));
		} else {
			sessionStorage.removeItem('utente');
		}
	});
}