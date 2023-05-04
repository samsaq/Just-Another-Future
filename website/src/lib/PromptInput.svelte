<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { app, getAnalytics, functions, database } from "../firebase.js";
  import { ref, get, DataSnapshot, set, child } from "firebase/database";
  import { modalStore } from "@skeletonlabs/skeleton";
  import type { ModalSettings } from "@skeletonlabs/skeleton";
  import { toastStore } from "@skeletonlabs/skeleton";
  import type { ToastSettings } from "@skeletonlabs/skeleton";

  const promptRef = ref(database, "/futurePrompts");
  let promptInput: string = "";

  export let isConnected: boolean = false;

  async function updatePrompt(promptText: string) { //sets the curPrompt to the promptText
    const snapshot = await get(promptRef);
    const newPromptRef = child(promptRef, `curPrompt`);
    const awaitingStatusRef = child(promptRef, `awaitingNewPrompt`);
    const promptStatusSnapshot = await get(awaitingStatusRef);
    const promptStatus = promptStatusSnapshot.val();
    if(promptStatus.awaiting === true)
    {
        await set(newPromptRef, promptText);
        const updatedToast: ToastSettings = {
            message: "Prompt Submitted",
            timeout: 3000,
        };
        toastStore.trigger(updatedToast);
    }
    else
    {
        const prevPromptUnfinished: ModalSettings = {
            type: "alert",
            title: "Animation still running",
            body: "Please wait for the animation to finish.",
        };
        promptInput = "";
        modalStore.trigger(prevPromptUnfinished);
    }
  }

  function submissionFailure() {
    const NonConnectionError: ModalSettings = {
      type: "alert",
      title: "No Connection",
      body: "Please connect the Pi Zero to submit prompts.",
    };
    promptInput = "";
    modalStore.trigger(NonConnectionError);
  }

  function promptSubmission(event: KeyboardEvent) {
    if (isConnected) {
      if (event.key === "Enter" && promptInput !== "") {
        // Using enter key to submit
        console.log("updating curPrompt to: " + promptInput);
        updatePrompt(promptInput);
      }
    } else {
      submissionFailure();
    }
  }
</script>

<label class="label">
  <input
    class="input"
    type="text"
    placeholder="Imagine the future..."
    bind:value={promptInput}
    on:keydown={promptSubmission}
  />
</label>

<style lang="postcss">
</style>
