# Component Versions

Current tested versions for this deployment:

| Component | Version | Updated |
|-----------|---------|---------|
| Matrix Synapse | 1.143.0 | 2025-12-10 |
| Element Web | 1.12.1 | 2025-12-10 |
| mautrix-whatsapp | 0.12.4 | 2025-12-10 |

## Check Installed Versions

```bash
echo "Synapse: $(/opt/matrix/synapse-venv/bin/python -c 'import synapse; print(synapse.__version__)')"
echo "Element: $(cat /var/www/element/version)"
echo "WhatsApp: $(/home/matrix-ai/services/whatsapp-bridge/bin/mautrix-whatsapp --version 2>&1 | head -1)"
```

## Latest Releases

- [Synapse](https://github.com/element-hq/synapse/releases)
- [Element Web](https://github.com/element-hq/element-web/releases)
- [mautrix-whatsapp](https://github.com/mautrix/whatsapp/releases)

## Update Instructions

See [docs/deployment.md](docs/deployment.md#updating-all-components) for detailed update procedures.
