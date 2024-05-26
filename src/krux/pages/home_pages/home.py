# The MIT License (MIT)

# Copyright (c) 2021-2024 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import gc
from ...display import BOTTOM_PROMPT_LINE
from ...qr import FORMAT_NONE, FORMAT_PMOFN
from ...krux_settings import t, Settings
from ...format import replace_decimal_separator
from .. import (
    Page,
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
)

MAX_POLICY_COSIGNERS_DISPLAYED = 5


class Home(Page):
    """Home is the main menu page of the app"""

    def __init__(self, ctx):
        super().__init__(
            ctx,
            Menu(
                ctx,
                [
                    (
                        t("Backup Mnemonic"),
                        (
                            self.backup_mnemonic
                            if not Settings().security.hide_mnemonic
                            else None
                        ),
                    ),
                    (t("Extended Public Key"), self.public_key),
                    (t("Wallet"), self.wallet),
                    (t("Address"), self.addresses_menu),
                    (t("Sign"), self.sign),
                    (t("Shutdown"), self.shutdown),
                ],
            ),
        )

    def backup_mnemonic(self):
        """Handler for the 'Backup Mnemonic' menu item"""
        from .mnemonic_backup import MnemonicsView

        mnemonics_viewer = MnemonicsView(self.ctx)
        return mnemonics_viewer.mnemonic()

    def public_key(self):
        """Handler for the 'xpub' menu item"""
        from .pub_key_view import PubkeyView

        pubkey_viewer = PubkeyView(self.ctx)
        return pubkey_viewer.public_key()

    def wallet_descriptor(self):
        """Handler for the 'wallet descriptor' menu item"""
        from .wallet_descriptor import WalletDescriptor

        wallet_descriptor = WalletDescriptor(self.ctx)
        return wallet_descriptor.wallet()

    def passphrase(self):
        """Add or replace wallet's passphrase"""
        if not self.prompt(
            t("Add or change wallet passphrase?"), self.ctx.display.height() // 2
        ):
            return MENU_CONTINUE

        from ..wallet_settings import PassphraseEditor
        from ...key import Key
        from ...wallet import Wallet

        passphrase_editor = PassphraseEditor(self.ctx)
        passphrase = passphrase_editor.load_passphrase_menu()
        if passphrase is None:
            return MENU_CONTINUE

        self.ctx.wallet = Wallet(
            Key(
                self.ctx.wallet.key.mnemonic,
                self.ctx.wallet.key.multisig,
                self.ctx.wallet.key.network,
                passphrase,
                self.ctx.wallet.key.account_index,
                self.ctx.wallet.key.script_type,
            )
        )
        return MENU_CONTINUE

    def customize(self):
        """Handler for the 'Customize' Wallet menu item"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            t("Customizing your wallet will generate a new Key.")
            + " "
            + t("Mnemonic and passphrase will be kept.")
        )
        if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
            return MENU_CONTINUE

        from ..wallet_settings import WalletSettings
        from ...key import Key
        from ...wallet import Wallet

        wallet_settings = WalletSettings(self.ctx)
        network, multisig, script_type, account = wallet_settings.customize_wallet(
            self.ctx.wallet.key
        )
        mnemonic = self.ctx.wallet.key.mnemonic
        passphrase = self.ctx.wallet.key.passphrase
        self.ctx.wallet = Wallet(
            Key(
                mnemonic,
                multisig,
                network,
                passphrase,
                account,
                script_type,
            )
        )
        return MENU_CONTINUE

    def bip85(self):
        """Handler for the 'BIP85' menu item"""
        if not self.prompt(
            t("Generate a BIP85 child mnemonic?"), self.ctx.display.height() // 2
        ):
            return MENU_CONTINUE

        from .bip85 import Bip85

        bip85 = Bip85(self.ctx)
        bip85.export()
        return MENU_CONTINUE

    def wallet(self):
        """Handler for the 'wallet' menu item"""

        submenu = Menu(
            self.ctx,
            [
                (t("Wallet Descriptor"), self.wallet_descriptor),
                (t("Passphrase"), self.passphrase),
                (t("Customize"), self.customize),
                ("BIP85", self.bip85),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def addresses_menu(self):
        """Handler for the 'address' menu item"""
        from .addresses import Addresses

        adresses = Addresses(self.ctx)
        return adresses.addresses_menu()

    def sign(self):
        """Handler for the 'sign' menu item"""
        submenu = Menu(
            self.ctx,
            [
                ("PSBT", self.sign_psbt),
                (t("Message"), self.sign_message),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        index, status = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return MENU_CONTINUE
        return status

    def load_psbt(self):
        """Loads a PSBT from camera or SD card"""

        load_menu = Menu(
            self.ctx,
            [
                (t("Load from camera"), lambda: None),
                (
                    t("Load from SD card"),
                    None if not self.has_sd_card() else lambda: None,
                ),
                (t("Back"), lambda: None),
            ],
        )
        index, _ = load_menu.run_loop()

        if index == 2:
            return (None, None, "")

        if index == 0:
            data, qr_format = self.capture_qr_code()
            return (data, qr_format, "")

        # If index == 1
        from ..utils import Utils
        from ...sd_card import PSBT_FILE_EXTENSION

        utils = Utils(self.ctx)
        psbt_filename, _ = utils.load_file(
            PSBT_FILE_EXTENSION, prompt=False, only_get_filename=True
        )
        return (None, FORMAT_NONE, psbt_filename)

    def _sign_menu(self):
        sign_menu = Menu(
            self.ctx,
            [
                (t("Sign to QR code"), lambda: None),
                (
                    t("Sign to SD card"),
                    None if not self.has_sd_card() else lambda: None,
                ),
                (t("Back"), lambda: None),
            ],
        )
        index, _ = sign_menu.run_loop()
        return index

    def sign_psbt(self):
        """Handler for the 'sign psbt' menu item"""
        from ...sd_card import (
            PSBT_FILE_EXTENSION,
            SIGNED_FILE_SUFFIX,
        )

        # Warns in case multisig wallet descriptor is not loaded
        if not self.ctx.wallet.is_loaded() and self.ctx.wallet.is_multisig():
            self.ctx.display.draw_centered_text(
                t("Warning:")
                + "\n"
                + t("Wallet output descriptor not found.")
                + "\n\n"
                + t("Some checks cannot be performed.")
            )
            if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
                return MENU_CONTINUE

        # Load a PSBT
        data, qr_format, psbt_filename = self.load_psbt()

        if data is None and psbt_filename == "":
            # Both the camera and the file on SD card failed!
            self.flash_error(t("Failed to load PSBT"))
            return MENU_CONTINUE

        # PSBT read OK! Will try to sign
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Loading.."))

        qr_format = FORMAT_PMOFN if qr_format == FORMAT_NONE else qr_format
        from ...psbt import PSBTSigner

        # Warns in case of path mismatch
        signer = PSBTSigner(self.ctx.wallet, data, qr_format, psbt_filename)
        path_mismatch = signer.path_mismatch()
        if path_mismatch:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Warning:")
                + " "
                + t("Path mismatch")
                + "\n"
                + "Wallet: "
                + self.ctx.wallet.key.derivation_str()
                + "\n"
                + "PSBT: "
                + path_mismatch
            )
            if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
                return MENU_CONTINUE

        # Show the policy for multisig
        if not self.ctx.wallet.is_loaded() and self.ctx.wallet.is_multisig():
            from ...key import Key

            policy_str = "PSBT policy:\n"
            policy_str += signer.policy["type"] + "\n"
            policy_str += (
                str(signer.policy["m"]) + " of " + str(signer.policy["n"]) + "\n"
            )
            fingerprints = []
            for inp in signer.psbt.inputs:
                # Do we need to loop through all the inputs or just one?
                for pub in inp.bip32_derivations:
                    fingerprint_srt = Key.format_fingerprint(
                        inp.bip32_derivations[pub].fingerprint, True
                    )
                    if fingerprint_srt not in fingerprints:
                        if len(fingerprints) > MAX_POLICY_COSIGNERS_DISPLAYED:
                            fingerprints[-1] = "..."
                            break
                        fingerprints.append(fingerprint_srt)

            policy_str += "\n".join(fingerprints)
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(policy_str)
            if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
                return MENU_CONTINUE

        # Fix zero fingerprint, it is necessary for the signing process on embit in a few cases
        if signer.fill_zero_fingerprint():
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Fingerprint unset in PSBT"))
            if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
                return MENU_CONTINUE

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing ..."))
        outputs, fee_percent = signer.outputs()

        # Warn if fees greater than 30% of what is spent
        if fee_percent >= 30.0:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Warning:")
                + " "
                + t("High fees!")
                + "\n"
                + replace_decimal_separator(("%.1f" % fee_percent))
                + t("% of the amount.")
            )

            if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
                return MENU_CONTINUE

        for message in outputs:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(message)
            self.ctx.input.wait_for_button()

        # memory management
        del data, outputs
        gc.collect()

        index = self._sign_menu()

        if index == 2:  # Back
            return MENU_CONTINUE

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Signing.."))

        signer.sign()

        title = t("Signed PSBT")
        if index == 0:
            # Sign to QR code
            qr_signed_psbt, qr_format = signer.psbt_qr()

            # memory management
            del signer
            gc.collect()

            self.display_qr_codes(qr_signed_psbt, qr_format, file_type="P")

            from ..utils import Utils

            utils = Utils(self.ctx)
            utils.print_standard_qr(qr_signed_psbt, qr_format, title, width=45)
            return MENU_CONTINUE

        # index == 1: Sign to SD card
        from ..file_operations import SaveFile

        save_page = SaveFile(self.ctx)
        psbt_filename, filename_undefined = save_page.set_filename(
            psbt_filename,
            "QRCode",
            SIGNED_FILE_SUFFIX,
            PSBT_FILE_EXTENSION,
        )
        del save_page
        gc.collect()

        if not filename_undefined:
            with open("/sd/" + psbt_filename, "wb") as f:
                # Write PSBT data directly to the file
                signer.psbt.write_to(f)
                self.flash_text(t("Saved to SD card") + ":\n%s" % psbt_filename)

        return MENU_CONTINUE

    def sign_message(self):
        """Handler for the 'sign message' menu item"""
        from .sign_message_ui import SignMessage

        message_signer = SignMessage(self.ctx)
        return message_signer.sign_message()
