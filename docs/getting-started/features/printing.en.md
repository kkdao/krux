----8<----
warning-printer.en.txt
----8<----

Krux has the ability to print mnemonic backup (Words, Numbers, Tiny Seed template; but not Stackbit 1248) and any QR code (SeedQR, signed PSBT, Address, XPUB, Wallet output descriptor, ...) via a locally-connected TTL serial thermal printer. Consult the [parts list](../../parts.md/#optional-ttl-serial-thermal-printer) page for supported printers.

<img src="../../../img/maixpy_amigo/print-qr-printing-150.png">
<img src="../../../img/maixpy_m5stickv/print-qr-printing-125.png">

<video width="430" controls>
  <source src="../../../img/printing-qr.mp4" type="video/mp4"></source>
</video>

<video width="400" controls>
  <source src="../../../img/scanning-printed-qr.mp4" type="video/mp4"></source>
</video>

<video width="480" controls>
  <source src="../../../img/printing-scanning-psbt.mp4" type="video/mp4"></source>
</video>


<img src="../../../img/maixpy_m5stickv/print-qr-prompt-125.png" align="right">
<img src="../../../img/maixpy_amigo/print-qr-prompt-150.png" align="right">

Once a thermal printer and driver have been enabled in [Krux settings](../settings.md/#thermal), all screens that display a QR code will offer the option to `Print to QR`. Other formats of mnemonic backup will also ask if you want to `Print to QR?`. 

There are many ways you can use this functionality, including:

- Printing backups of your mnemonics and multisig wallet output descriptor
- Printing your xpubs and receive addresses to share
- Printing signed messages and PSBTs

Since printed thermal paper fades quickly, you can also print your backups on sticker thermal paper to use as templates for punching into more resilient materials like steel.

We also have plans to add support for other kinds of QR "printers" in the future, including CNC machines. In this case, gcode will be generated that can be sent directly to a GRBL controller to cut your QRs out of wood or metal!

Just be careful what you do with the printed codes, since most smartphones can now quickly and easily read QR codes. Treat your QR mnemonic the same way you would treat a plaintext copy of it.

<div style="clear: both"></div>
