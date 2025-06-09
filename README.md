<h1>Sowftware PC per collaudo centrale Leonardo L24</h1>
Necessario eseguire manualmente il provisionig dal back-office VIMAC.<br>
I certificati per l'autenticazione sono cablati nel software e vanno copiati dal back-office.
La stessa cosa per IDT.

<h2>How To</h2>
<li>Per modificare la GUI lanciare lo script .\.venv\Scripts\designer.exe e aprire il file \gui\MainWindow.ui</li>
<li>Salvare le modifiche e generare il codice python generate_ui.bat</li>
<li>Per generare l'eseguibile lanciare lo script create_exe.bat. L'eseguibile viene creato nella cartella dist</li>
