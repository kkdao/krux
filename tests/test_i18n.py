import pytest


def test_translations(mocker, m5stickv):
    from krux.krux_settings import t, locale_control
    from krux.translations import available_languages, ref_array
    import binascii

    # Test default language
    assert t("Load Mnemonic") == "Load Mnemonic"

    # Test pt_BR
    locale_control.load_locale("pt_BR")
    assert t("Load Mnemonic") == "Carregar Mnemônico"

    # Test non existent slug
    assert t("New Text") == "New Text"

    # Cross-check available languages reference files
    crc32_index = binascii.crc32("Load Mnemonic".encode("utf-8"))
    reference_index = ref_array.index(crc32_index)
    for lang in available_languages:
        # Construct the path to the nested module
        lang_module_path = f"krux.translations.{lang[:2]}"
        # Import the top-level module (krux)
        lang_trans_module = __import__(lang_module_path, fromlist=[""])
        # Access the translation_array variable from the nested module
        lang_trans_array = getattr(lang_trans_module, "translation_array")
        locale_control.load_locale(lang)
        assert t("Load Mnemonic") == lang_trans_array[reference_index]

    # Restore default locale so other tests are not affected
    locale_control.load_locale("en-US")


def test_t_lookup_hit_and_miss(mocker, m5stickv):
    from krux.krux_settings import t, locale_control

    # Default locale: passthrough.
    locale_control.load_locale("en-US")
    assert t("Load Mnemonic") == "Load Mnemonic"

    # Loaded locale: known slug translates, unknown slug falls back to itself.
    locale_control.load_locale("pt_BR")
    assert t("Load Mnemonic") == "Carregar Mnemônico"
    assert t("__definitely_not_a_slug__") == "__definitely_not_a_slug__"

    # Restore default to avoid leaking locale into other tests.
    locale_control.load_locale("en-US")
