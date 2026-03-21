# Easy-translation Release Draft

## Title

Easy-translation v0.5.1

## Suggested Tag

v0.5.1

## Summary

This release provides a ready-to-use Windows executable for Easy-translation.

## What's New

- Unified app branding as `Easy-translation`
- Added app icon for the window, tray, and packaged executable
- Improved tray behavior: closing or minimizing sends the app to the tray background
- Added tray actions for opening the main window, opening settings, translating the clipboard, and exiting
- Removed candidate translation selection and unified translation output to a single result
- Made Tesseract optional: missing Tesseract no longer blocks saving settings or using non-OCR features
- Expanded `.gitignore` for common Python project artifacts

## Downloads

- `Easy-translation.exe`
- `Easy-translation-windows-x64.zip`

## Notes

- Platform: Windows x64
- Standard translation features work without Tesseract
- Screenshot OCR requires Tesseract to be installed on the user's machine
- Baidu, Tencent, and Ollama still require user-side configuration in Settings

## SHA256

- `Easy-translation.exe`: `5C929ED08F0CFD504DF50B008675994687F731ECE800468AB1831AC006056648`
