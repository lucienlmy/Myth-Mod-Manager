if not exist "%cd%\venv" (
	python3 -m venv /venv
)
	
cd venv\Scripts
activate