def test_vars_exist():
    from krux import metadata
    getattr(metadata, 'VERSION')
    getattr(metadata, 'SIGNER_PUBKEY')