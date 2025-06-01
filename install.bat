@echo off
python -m venv env
call env\Scripts\activate.bat

python -m pip install -r requirements.txt

echo Done
pause