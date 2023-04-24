<script lang="ts">
    import PromptInput from "$lib/PromptInput.svelte";
	import { database} from "../firebase";
	import { ref, onValue, DataSnapshot } from "firebase/database";
	import { onMount, onDestroy } from "svelte";

	let isConnected = false;
	let piZeroRef = ref(database, 'connections/pi-zero');
	//console.log(piZeroRef.toString());
	let unsubscribeIsConnected: (() => void) | undefined;

	onMount(async () => {
		console.log('Attaching listener to', piZeroRef.toString());
		unsubscribeIsConnected = onValue(piZeroRef, (snapshot: DataSnapshot) => {
			//console.log('Value changed to', snapshot.val());
			isConnected = snapshot.val();
		});
	});

	onDestroy(() => {
		//console.log('Removing listener');
		if (unsubscribeIsConnected) {
      	unsubscribeIsConnected();
    	}
	});


</script>

<div class="container h-screen w-screen mx-auto flex justify-center items-center Background flex-col">
	<h2>Just Another Future</h2>
	<div class="space-y-10 text-center py-8">
		<PromptInput isConnected={isConnected}/>
		<div class="text-center">
			{#if isConnected}
				<p>Connected to Pi Zero</p>
			{:else}
				<p>Not Connected to Pi Zero</p>
			{/if}
		</div>
	</div>
</div>

<style lang="postcss">
</style>
