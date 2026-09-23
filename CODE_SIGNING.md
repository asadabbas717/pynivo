# Windows code signing

The GitHub release workflow deliberately refuses to publish an installer unless
it has been signed and verified with Windows SignTool.

## Required GitHub Actions secrets

- `WINDOWS_SIGNING_CERTIFICATE_BASE64`: a base64-encoded PKCS#12/PFX code-signing
  certificate, including its private key and certificate chain.
- `WINDOWS_SIGNING_CERTIFICATE_PASSWORD`: the PFX password.

Store these under **Repository Settings → Secrets and variables → Actions**.
Never commit the PFX file or its password to the repository.

To encode a certificate in PowerShell:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\path\certificate.pfx")) |
    Set-Clipboard
```

The workflow builds the installer, applies an SHA-256 Authenticode signature,
uses a trusted timestamp service, verifies the signature, generates a checksum,
and only then creates a draft GitHub prerelease. The temporary certificate file
is removed even if another step fails.

An EV certificate may require hardware-backed or cloud signing instead of a PFX.
In that case, adapt the signing step to the certificate provider before running
the release workflow.
