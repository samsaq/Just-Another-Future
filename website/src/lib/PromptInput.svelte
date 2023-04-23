<script lang="ts">

    import { onMount, onDestroy } from "svelte";
    import { app, getAnalytics , functions, database } from '../firebase.js';
    import { ref, get, DataSnapshot, set, child } from "firebase/database";

    const MAX_PROMPTS = 100;
    const promptRef = ref(database, "/futurePrompts")

    async function addPrompt(promptText: string) {
        const snapshot = await get(promptRef);
        let startIdx = 0;
        let numChildren = 0;
        snapshot.forEach(child => {
        numChildren++;
        });
        if (numChildren >= MAX_PROMPTS) { //to keep database size small, we will overwrite the oldest prompts
            startIdx = (numChildren % MAX_PROMPTS) ;
        } else {
            startIdx = numChildren;
        }
        const newPromptRef = child(promptRef, `${startIdx}`);
        await set(newPromptRef, promptText);
    }

    let promptInput: string = "";

    function promptSubmission(event: KeyboardEvent) {
        if (event.key === "Enter" && promptInput !== "") { // Using enter key to submit
            console.log(promptInput);
            addPrompt(promptInput);
        }
    }

</script>

<label class="label">
    <input class="input" type="text" placeholder="Imagine the future..." bind:value={promptInput} on:keydown={promptSubmission}/>
</label>

<style lang="postcss">

</style>