:: A batch script to build and upload to PyPI

:: Delete old builds
set builds=".\dist\"
if exist %builds% del %builds% /q /s

python setup.py sdist bdist_wheel

if "%1%"=="test" goto test
:pypi
python -m twine upload dist/*
goto end

:test
python -m twine upload --repository testpypi dist/*
goto end

:end
