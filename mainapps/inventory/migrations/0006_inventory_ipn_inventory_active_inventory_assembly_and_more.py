# Generated by Django 5.1.7 on 2025-03-17 11:56

import django.core.validators
import django.db.models.deletion
import mainapps.common.custom_fields
import mainapps.common.settings
import mainapps.inventory.helpers.field_validators
import mptt.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("company", "0002_initial"),
        ("inventory", "0005_rename_i_type_inventory_inventory_type"),
        ("stock", "0002_remove_stocklocationtype_icon_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="inventory",
            name="IPN",
            field=models.CharField(
                blank=True,
                help_text="Internal Part Number",
                max_length=100,
                null=True,
                verbose_name="IPN",
            ),
        ),
        migrations.AddField(
            model_name="inventory",
            name="active",
            field=models.BooleanField(
                default=True,
                help_text="Is this Inventory active?",
                verbose_name="Active",
            ),
        ),
        migrations.AddField(
            model_name="inventory",
            name="assembly",
            field=models.BooleanField(
                default=False,
                help_text="Can this Inventory be built from other Inventory?",
                verbose_name="Assembly",
            ),
        ),
        migrations.AddField(
            model_name="inventory",
            name="component",
            field=models.BooleanField(
                default=False,
                help_text="Can this Inventory be used to build other Inventory?",
                verbose_name="Component",
            ),
        ),
        migrations.AddField(
            model_name="inventory",
            name="default_supplier",
            field=models.ForeignKey(
                blank=True,
                help_text="Default supplier For the Inventory",
                limit_choices_to={"is_supplier": True},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="default_inventories",
                to="company.company",
                verbose_name="Default Supplier",
            ),
        ),
        migrations.AddField(
            model_name="inventory",
            name="locked",
            field=models.BooleanField(
                default=False,
                help_text="Locked Inventory cannot be edited",
                verbose_name="Locked",
            ),
        ),
        migrations.AddField(
            model_name="inventory",
            name="officer_in_charge",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="inventories_incharge",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Created By",
            ),
        ),
        migrations.AddField(
            model_name="inventory",
            name="purchaseable",
            field=models.BooleanField(
                default=True,
                help_text="Can this Inventory be purchased from external suppliers?",
                verbose_name="Purchaseable",
            ),
        ),
        migrations.AddField(
            model_name="inventory",
            name="salable",
            field=models.BooleanField(
                default=True,
                help_text="Can this Inventory be sold to customers?",
                verbose_name="Salable",
            ),
        ),
        migrations.AddField(
            model_name="inventory",
            name="testable",
            field=models.BooleanField(
                default=False,
                help_text="Can this Inventory have test results recorded against it?",
                verbose_name="Testable",
            ),
        ),
        migrations.AddField(
            model_name="inventory",
            name="trackable",
            field=models.BooleanField(
                default=True,
                help_text="Does this Inventory have tracking for unique items?",
                verbose_name="Trackable",
            ),
        ),
        migrations.AddField(
            model_name="inventory",
            name="virtual",
            field=models.BooleanField(
                default=False,
                help_text="Is this a virtual inventory, such as a software product or license?",
                verbose_name="Virtual",
            ),
        ),
        migrations.AddField(
            model_name="inventorycategory",
            name="default_location",
            field=mptt.fields.TreeForeignKey(
                blank=True,
                help_text="Default location for parts in this category",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="default_categories",
                to="stock.stocklocation",
                verbose_name="Default Location",
            ),
        ),
        migrations.AddField(
            model_name="inventorycategory",
            name="structural",
            field=models.BooleanField(
                default=False,
                help_text="Parts may not be directly assigned to a structural category, but may be assigned to child categories.",
                verbose_name="Structural",
            ),
        ),
        migrations.CreateModel(
            name="InventoryPricing",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "currency",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("AFN", "AFGHANI"),
                            ("EUR", "EURO"),
                            ("ALL", "LEK"),
                            ("DZD", "ALGERIAN DINAR"),
                            ("USD", "US DOLLAR"),
                            ("AOA", "KWANZA"),
                            ("XCD", "EAST CARIBBEAN DOLLAR"),
                            ("ARS", "ARGENTINE PESO"),
                            ("AMD", "ARMENIAN DRAM"),
                            ("AWG", "ARUBAN FLORIN"),
                            ("AUD", "AUSTRALIAN DOLLAR"),
                            ("AZN", "AZERBAIJAN MANAT"),
                            ("BSD", "BAHAMIAN DOLLAR"),
                            ("BHD", "BAHRAINI DINAR"),
                            ("BDT", "TAKA"),
                            ("BBD", "BARBADOS DOLLAR"),
                            ("BYN", "BELARUSIAN RUBLE"),
                            ("BZD", "BELIZE DOLLAR"),
                            ("BMD", "BERMUDIAN DOLLAR"),
                            ("INR", "INDIAN RUPEE"),
                            ("BTN", "NGULTRUM"),
                            ("BOP", "BOLIVIAN PESO"),
                            ("BOB", "BOLIVIANO"),
                            ("BWP", "PULA"),
                            ("NOK", "NORWEGIAN KRONE"),
                            ("BRL", "BRAZILIAN REAL"),
                            ("BND", "BRUNEI DOLLAR"),
                            ("BGN", "BULGARIAN LEV"),
                            ("BIF", "BURUNDI FRANC"),
                            ("CVE", "CABO VERDE ESCUDO"),
                            ("KHR", "RIEL"),
                            ("CAD", "CANADIAN DOLLAR"),
                            ("KYD", "CAYMAN ISLANDS DOLLAR"),
                            ("CLP", "CHILEAN PESO"),
                            ("CNY", "YUAN RENMINBI"),
                            ("COP", "COLOMBIAN PESO"),
                            ("KMF", "COMORIAN FRANC "),
                            ("CDF", "CONGOLESE FRANC"),
                            ("NZD", "NEW ZEALAND DOLLAR"),
                            ("CRC", "COSTA RICAN COLON"),
                            ("XOF", "CFA FRANC BCEAO"),
                            ("CUP", "CUBAN PESO"),
                            ("ANG", "NETHERLANDS ANTILLEAN GUILDER"),
                            ("CZK", "CZECH KORUNA"),
                            ("DKK", "DANISH KRONE"),
                            ("DJF", "DJIBOUTI FRANC"),
                            ("DOP", "DOMINICAN PESO"),
                            ("EGP", "EGYPTIAN POUND"),
                            ("SVC", "EL SALVADOR COLON"),
                            ("ERN", "NAKFA"),
                            ("SZL", "LILANGENI"),
                            ("ETB", "ETHIOPIAN BIRR"),
                            ("FKP", "FALKLAND ISLANDS POUND"),
                            ("FJD", "FIJI DOLLAR"),
                            ("GMD", "DALASI"),
                            ("GEL", "LARI"),
                            ("GHS", "GHANA CEDI"),
                            ("GIP", "GIBRALTAR POUND"),
                            ("GTQ", "QUETZAL"),
                            ("GBP", "POUND STERLING"),
                            ("GNF", "GUINEAN FRANC"),
                            ("GYD", "GUYANA DOLLAR"),
                            ("HTG", "GOURDE"),
                            ("HNL", "LEMPIRA"),
                            ("HKD", "HONG KONG DOLLAR"),
                            ("HUF", "FORINT"),
                            ("ISK", "ICELAND KRONA"),
                            ("IDR", "RUPIAH"),
                            ("IRR", "IRANIAN RIAL"),
                            ("IQD", "IRAQI DINAR"),
                            ("ILS", "NEW ISRAELI SHEQEL"),
                            ("JMD", "JAMAICAN DOLLAR"),
                            ("JPY", "YEN"),
                            ("JOD", "JORDANIAN DINAR"),
                            ("KZT", "TENGE"),
                            ("KES", "KENYAN SHILLING"),
                            ("KPW", "NORTH KOREAN WON"),
                            ("KRW", "WON"),
                            ("KWD", "KUWAITI DINAR"),
                            ("KGS", "SOM"),
                            ("LAK", "LAO KIP"),
                            ("LBP", "LEBANESE POUND"),
                            ("LSL", "LOTI"),
                            ("ZAR", "RAND"),
                            ("LRD", "LIBERIAN DOLLAR"),
                            ("LYD", "LIBYAN DINAR"),
                            ("CHF", "SWISS FRANC"),
                            ("MOP", "PATACA"),
                            ("MKD", "DENAR"),
                            ("MYR", "MALAYSIAN RINGGIT"),
                            ("MVR", "RUFIYAA"),
                            ("MUR", "MAURITIUS RUPEE"),
                            ("MXN", "MEXICAN PESO"),
                            ("MDL", "MOLDOVAN LEU"),
                            ("MNT", "TUGRIK"),
                            ("MAD", "MOROCCAN DIRHAM"),
                            ("MZN", "MOZAMBIQUE METICAL"),
                            ("MMK", "KYAT"),
                            ("NAD", "NAMIBIA DOLLAR"),
                            ("NPR", "NEPALESE RUPEE"),
                            ("OMR", "RIAL OMANI"),
                            ("PKR", "PAKISTAN RUPEE"),
                            ("PHP", "PHILIPPINE PESO"),
                            ("PLN", "ZLOTY"),
                            ("QAR", "QATARI RIAL"),
                            ("RON", "ROMANIAN LEU"),
                            ("RUB", "RUSSIAN RUBLE"),
                            ("RWF", "RWANDA FRANC"),
                            ("SHP", "SAINT HELENA POUND"),
                            ("SAR", "SAUDI RIYAL"),
                            ("RSD", "SERBIAN DINAR"),
                            ("SCR", "SEYCHELLES RUPEE"),
                            ("SLL", "LEONE"),
                            ("SLE", "LEONE"),
                            ("SGD", "SINGAPORE DOLLAR"),
                            ("SBD", "SOLOMON ISLANDS DOLLAR"),
                            ("SOS", "SOMALI SHILLING"),
                            ("SSP", "SOUTH SUDANESE POUND"),
                            ("LKR", "SRI LANKA RUPEE"),
                            ("SDG", "SUDANESE POUND"),
                            ("SRD", "SURINAM DOLLAR"),
                            ("SEK", "SWEDISH KRONA"),
                            ("SYP", "SYRIAN POUND"),
                            ("TWD", "NEW TAIWAN DOLLAR"),
                            ("TJS", "SOMONI"),
                            ("TZS", "TANZANIAN SHILLING"),
                            ("THB", "BAHT"),
                            ("TTD", "TRINIDAD AND TOBAGO DOLLAR"),
                            ("TND", "TUNISIAN DINAR"),
                            ("TRY", "TURKISH LIRA"),
                            ("TMT", "TURKMENISTAN NEW MANAT"),
                            ("UGX", "UGANDA SHILLING"),
                            ("UAH", "HRYVNIA"),
                            ("AED", "UAE DIRHAM"),
                            ("UZS", "UZBEKISTAN SUM"),
                            ("VES", "BOLÍVAR SOBERANO"),
                            ("VED", "BOLÍVAR SOBERANO"),
                            ("YER", "YEMENI RIAL"),
                            ("ZMW", "ZAMBIAN KWACHA"),
                            ("ZWL", "ZIMBABWE DOLLAR"),
                            ("VND", "DONG"),
                            ("NGN", "NAIRA"),
                            ("VUV", "VATU"),
                            ("PAB", "BALBOA"),
                            ("PGK", "KINA"),
                            ("PYG", "GUARANI"),
                            ("PEN", "SOL"),
                            ("WST", "TALA"),
                            ("STN", "DOBRA"),
                            ("MGA", "MALAGASY ARIARY"),
                            ("MWK", "MALAWI KWACHA"),
                            ("MRU", "OUGUIYA"),
                            ("UYU", "PESO URUGUAYO"),
                            ("TOP", "PA'ANGA"),
                            ("NIO", "NICARAGUAN CÓRDOBA"),
                            ("CUC", "PESO CONVERTIBLE"),
                            ("BAM", "CONVERTIBLE MARK"),
                            ("XPF", "CFP FRANC"),
                            ("XAF", "CFA FRANC BEAC"),
                            ("BTC", "BITCOIN"),
                            ("XBT", "BITCOIN"),
                            ("LTC", "LITECOIN"),
                            ("NMC", "NAMECOIN"),
                            ("PPC", "PEERCOIN"),
                            ("XRP", "RIPPLE"),
                            ("DOGE", "DOGECOIN"),
                            ("GRC", "GRIDCOIN"),
                            ("XPM", "PRIMECOIN"),
                            ("OMG", "OMG NETWORK"),
                            ("NXT", "NXT"),
                            ("AUR", "AURORACOIN"),
                            ("BLZ", "BLUZELLE"),
                            ("DASH", "DASH"),
                            ("NEO", "NEO"),
                            ("MZC", "MAZACOIN"),
                            ("XMR", "MONERO"),
                            ("TIT", "TITCOIN"),
                            ("XVG", "VERGE"),
                            ("VTC", "VERTCOIN"),
                            ("XLM", "STELLAR"),
                            (None, "COINYE"),
                            ("ETH", "ETHEREUM"),
                            ("ETC", "ETHEREUM CLASSIC"),
                            ("XNO", "NANO"),
                            ("USDT", "TETHER"),
                            (None, "ONECOIN"),
                            ("FIRO", "FIRO"),
                            ("ZEC", "ZCASH"),
                            ("ZRX", "0X"),
                            ("AAVE", "AAVE"),
                            ("BNT", "BANCOR"),
                            ("BAT", "BASIC ATTENTION TOKEN"),
                            ("BCH", "BITCOIN CASH"),
                            ("BTG", "BITCOIN GOLD"),
                            ("BNB", "BINANCE COIN"),
                            ("ADA", "CARDANO"),
                            ("COTI", "COTI"),
                            ("LINK", "CHAINLINK"),
                            ("MANA", "DECENTRALAND"),
                            ("ENS", "ETHEREUM NAME SERVICE"),
                            ("EOS", "EOS.IO"),
                            ("ENJ", "ENJIN"),
                            ("FET", "FETCH.AI"),
                            ("NMR", "NUMERAIRE"),
                            ("MLN", "MELON"),
                            ("MATIC", "POLYGON"),
                            ("STORJ", "STORJ"),
                            ("LRC", "LOOPRING"),
                            ("BCC", "BITCONNECT"),
                            (None, "AMBACOIN"),
                            ("ACH", "ALCHEMY PAY"),
                            ("BSV", "BITCOIN SV"),
                            ("CRO", "CRONOS"),
                            ("FTM", "FANTOM"),
                            ("CKB", "NERVOS NETWORK"),
                            ("USTC", "TERRACLASSICUSD"),
                            ("LUNA", "TERRA"),
                            ("USDC", "USD COIN"),
                            ("UNI", "UNISWAP"),
                            ("MDT", "MEASURABLE DATA TOKEN"),
                            ("SNX", "SYNTHETIX"),
                            ("QNT", "QUANT"),
                            (None, "KODAKCOIN"),
                            ("PTR", "PETRO"),
                            ("ALGO", "ALGORAND"),
                            ("ANKR", "ANKR"),
                            ("AXS", "AXIE INFINITY"),
                            ("BAND", "BAND PROTOCOL"),
                            ("BICO", "BICONOMY"),
                            ("BUSD", "BINANCE USD"),
                            ("ATOM", "COSMOS"),
                            ("CHZ", "CHILIZ"),
                            ("OXT", "ORCHID"),
                            ("TRB", "TELLOR"),
                            ("WBTC", "WRAPPED BITCOIN"),
                            ("1INCH", "1INCH NETWORK"),
                            ("AVAX", "AVALANCHE"),
                            ("API3", "API3"),
                            ("AMP", "AMP"),
                            ("BAL", "BALANCER"),
                            ("BOND", "BARNBRIDGE"),
                            ("FIDA", "BONFIDA"),
                            ("BCHA", "BITCOIN CASH ABC"),
                            ("CELO", "CELO"),
                            ("COMP", "COMPOUND"),
                            ("CRV", "CURVE"),
                            ("FIL", "FILECOIN"),
                            ("CAKE", "PANCAKESWAP"),
                            ("DOT", "POLKADOT"),
                            ("MIR", "MIRROR PROTOCOL"),
                            ("GRT", "THE GRAPH"),
                            ("SHIB", "SHIBA INU"),
                            ("SOL", "SOLANA"),
                            ("SUSHI", "SUSHISWAP"),
                            ("YFI", "YEARN.FINANCE"),
                            ("FORTH", "AMPLEFORTH GOVERNANCE TOKEN"),
                            ("BIT", "BITDAO"),
                            ("CTSI", "CARTESI"),
                            ("DESO", "DECENTRALIZED SOCIAL"),
                            ("SFM", "SAFEMOON"),
                            ("APE", "APECOIN"),
                            ("APT", "APTOS"),
                            ("XPD", "PALLADIUM"),
                            ("XPT", "PLATINUM"),
                            ("XAU", "GOLD"),
                            ("XAG", "SILVER"),
                            ("XSU", "SUCRE"),
                            ("XDR", "SDR (SPECIAL DRAWING RIGHT)"),
                            ("XUA", "ADB UNIT OF ACCOUNT"),
                            (
                                "XBA",
                                "BOND MARKETS UNIT EUROPEAN COMPOSITE UNIT (EURCO)",
                            ),
                            (
                                "XBB",
                                "BOND MARKETS UNIT EUROPEAN MONETARY UNIT (E.M.U.-6)",
                            ),
                            (
                                "XBC",
                                "BOND MARKETS UNIT EUROPEAN UNIT OF ACCOUNT 9 (E.U.A.-9)",
                            ),
                            (
                                "XBD",
                                "BOND MARKETS UNIT EUROPEAN UNIT OF ACCOUNT 17 (E.U.A.-17)",
                            ),
                            (
                                "XXX",
                                "THE CODES ASSIGNED FOR TRANSACTIONS WHERE NO CURRENCY IS INVOLVED",
                            ),
                            ("MXV", "MEXICAN UNIDAD DE INVERSION (UDI)"),
                            ("USN", "US DOLLAR (NEXT DAY)"),
                            ("UYW", "UNIDAD PREVISIONAL"),
                            ("CHE", "WIR EURO"),
                            ("CHW", "WIR FRANC"),
                            ("UYI", "URUGUAY PESO EN UNIDADES INDEXADAS (UI)"),
                            ("BOV", "MVDOL"),
                            ("CLF", "UNIDAD DE FOMENTO"),
                            ("COU", "UNIDAD DE VALOR REAL"),
                        ],
                        default=mainapps.common.settings.DEFAULT_CURRENCY_CODE,
                        help_text="Set company default currency",
                        max_length=12,
                        validators=[
                            mainapps.inventory.helpers.field_validators.validate_currency_code
                        ],
                        verbose_name="Base Currency",
                    ),
                ),
                ("scheduled_for_update", models.BooleanField(default=False)),
                (
                    "bom_cost_min",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Minimum cost of component parts",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Minimum BOM Cost",
                    ),
                ),
                (
                    "bom_cost_max",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Maximum cost of component parts",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Maximum BOM Cost",
                    ),
                ),
                (
                    "purchase_cost_min",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Minimum historical purchase cost",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Minimum Purchase Cost",
                    ),
                ),
                (
                    "purchase_cost_max",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Maximum historical purchase cost",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Maximum Purchase Cost",
                    ),
                ),
                (
                    "internal_cost_min",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Minimum cost based on internal price breaks",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Minimum Internal Price",
                    ),
                ),
                (
                    "internal_cost_max",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Maximum cost based on internal price breaks",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Maximum Internal Price",
                    ),
                ),
                (
                    "supplier_price_min",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Minimum price of part from external suppliers",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Minimum Supplier Price",
                    ),
                ),
                (
                    "supplier_price_max",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Maximum price of part from external suppliers",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Maximum Supplier Price",
                    ),
                ),
                (
                    "variant_cost_min",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Calculated minimum cost of variant parts",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Minimum Variant Cost",
                    ),
                ),
                (
                    "variant_cost_max",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Calculated maximum cost of variant parts",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Maximum Variant Cost",
                    ),
                ),
                (
                    "override_min",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Override minimum cost",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Minimum Cost",
                    ),
                ),
                (
                    "override_max",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Override maximum cost",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Maximum Cost",
                    ),
                ),
                (
                    "overall_min",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Calculated overall minimum cost",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Minimum Cost",
                    ),
                ),
                (
                    "overall_max",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Calculated overall maximum cost",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Maximum Cost",
                    ),
                ),
                (
                    "sale_price_min",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Minimum sale price based on price breaks",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Minimum Sale Price",
                    ),
                ),
                (
                    "sale_price_max",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Maximum sale price based on price breaks",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Maximum Sale Price",
                    ),
                ),
                (
                    "sale_history_min",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Minimum historical sale price",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Minimum Sale Cost",
                    ),
                ),
                (
                    "sale_history_max",
                    mainapps.common.custom_fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        default=0.0,
                        help_text="Maximum historical sale price",
                        max_digits=19,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Maximum Sale Cost",
                    ),
                ),
                (
                    "inventory",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="inventory.inventory",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
