<script lang='ts'>
	// Your custom Skeleton theme:
	import '../theme.postcss';
	// This contains the bulk of Skeletons required styles:
	import '@skeletonlabs/skeleton/styles/all.css';
	// Finally, your application's global stylesheet (sometimes labeled 'app.css')
	import '../app.postcss';
	import { AppShell, AppBar, Modal, Toast } from '@skeletonlabs/skeleton';
</script>

<!-- App Shell -->
<AppShell>
	
	<!-- Page Route Content -->
	<Modal />
	<slot />
	<Toast max = {3} position = "b" background = "variant-filled-primary"/>
</AppShell>
