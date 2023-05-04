# Just-Another-Future
Website &amp; Pi-Zero Code for the Artefact - Just Another Future

For Pi Zero:
Process for graceful shutdown for the terminal while running headless:
1. Do a pgrep -f zeroCode.py to get the PID of the process
2. Do a kill -s SIGUSR1 <PID> to send a signal to the process - this signal will be handled for a graceful shutdown