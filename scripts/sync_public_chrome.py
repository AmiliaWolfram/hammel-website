"""The public header/footer are injected at request time by PublicChromeMiddleware.
Edit website/shared/header.html and website/shared/footer.html only.
No sync or per-page edits are necessary. This script is retained for compatibility.
"""
if __name__ == "__main__":
    print("Public chrome is now shared dynamically; no synchronization required.")
