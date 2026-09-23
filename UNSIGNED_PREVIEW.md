# PyNivo 0.1.0 Preview

This is an early Windows preview for testing and feedback.

## Important Windows warning

This installer is **not digitally signed** because the project does not yet
have a publicly trusted code-signing certificate. Windows may display
**Windows protected your PC** or identify the publisher as **Unknown
publisher**. Download the installer only from the official PyNivo GitHub
release page and verify its SHA-256 checksum before running it.

To continue after a Microsoft Defender SmartScreen prompt, select **More
info**, confirm the filename is `PyNivo-0.1.0-Preview-Setup-x64.exe`, and then
select **Run anyway**. Managed work or school computers may prohibit unsigned
software.

## Verify the download

The release contains `SHA256SUMS.txt`. In PowerShell, run:

```powershell
Get-FileHash .\PyNivo-0.1.0-Preview-Setup-x64.exe -Algorithm SHA256
Get-Content .\SHA256SUMS.txt
```

The two hashes must match exactly. A matching checksum verifies the download,
but it is not a substitute for a digital signature.

## License and notices

PyNivo is Copyright 2026 Asad Abbas and licensed under Apache License 2.0.
Third-party notices and Qt/PySide6 LGPL compliance materials are bundled with
the application and available in the source repository.
