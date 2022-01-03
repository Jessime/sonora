rm -rf dist
rm -rf build
rm sonora.spec

pyinstaller \
  --add-data 'sonora/data:data'\
  --windowed \
   -y \
   --clean \
   --icon sonora/data/camera.icns \
   --name sonora \
   --exclude-module _tkinter \
   --exclude-module Tkinter \
   --exclude-module enchant \
   --exclude-module twisted \
   run.py

./dist/sonora/sonora